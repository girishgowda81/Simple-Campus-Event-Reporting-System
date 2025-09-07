import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from app.models import db, College, Student, Event, Registration, Attendance, Feedback
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    db_url = os.getenv('DATABASE_URL', 'sqlite:///event_reporting.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/initdb', methods=['POST'])
    def initdb():
        with app.app_context():
            db.create_all()
        return jsonify({'status':'ok','message':'Database initialized'}), 201

    @app.route('/colleges', methods=['POST'])
    def create_college():
        data = request.get_json()
        c = College(name=data['name'])
        db.session.add(c)
        db.session.commit()
        return jsonify({'id': c.id, 'name': c.name}), 201

    @app.route('/students', methods=['POST'])
    def create_student():
        data = request.get_json()
        s = Student(name=data['name'], email=data['email'], college_id=data['college_id'])
        db.session.add(s)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error':'Student with this email already exists in this college'}), 409
        return jsonify({'id': s.id, 'name': s.name, 'email': s.email, 'college_id': s.college_id}), 201

    @app.route('/events', methods=['POST'])
    def create_event():
        data = request.get_json()
        e = Event(
            title=data['title'],
            type=data['type'],
            date=datetime.strptime(data['date'],'%Y-%m-%d').date(),
            college_id=data['college_id']
        )
        db.session.add(e)
        db.session.commit()
        return jsonify({'id': e.id, 'title': e.title, 'type': e.type, 'date': str(e.date), 'college_id': e.college_id}), 201

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        # ensure student and event belong to same college
        student = Student.query.get(data['student_id'])
        event = Event.query.get(data['event_id'])
        if not student or not event:
            return jsonify({'error':'Invalid student_id or event_id'}), 400
        if student.college_id != event.college_id:
            return jsonify({'error':'Student and Event belong to different colleges'}), 400

        r = Registration(student_id=student.id, event_id=event.id)
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error':'Student already registered for this event'}), 409
        return jsonify({'id': r.id, 'student_id': r.student_id, 'event_id': r.event_id}), 201

    @app.route('/attendance', methods=['POST'])
    def attendance():
        data = request.get_json()
        # must be registered first
        reg = Registration.query.filter_by(student_id=data['student_id'], event_id=data['event_id']).first()
        if not reg:
            return jsonify({'error':'Student must be registered before marking attendance'}), 400

        a = Attendance(student_id=data['student_id'], event_id=data['event_id'], status=data['status'])
        db.session.add(a)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error':'Attendance already marked for this student & event'}), 409
        return jsonify({'id': a.id, 'status': a.status}), 201

    @app.route('/feedback', methods=['POST'])
    def feedback():
        data = request.get_json()
        # must be registered first
        reg = Registration.query.filter_by(student_id=data['student_id'], event_id=data['event_id']).first()
        if not reg:
            return jsonify({'error':'Student must be registered before submitting feedback'}), 400
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({'error':'Rating must be between 1 and 5'}), 400

        f = Feedback(student_id=data['student_id'], event_id=data['event_id'], rating=rating, comment=data.get('comment'))
        db.session.add(f)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error':'Feedback already submitted for this student & event'}), 409
        return jsonify({'id': f.id, 'rating': f.rating}), 201

    # ---------- Reports ----------
    from sqlalchemy import func, case, desc

    @app.route('/reports/event_popularity')
    def event_popularity():
        college_id = request.args.get('college_id', type=int)
        q = db.session.query(
            Event.id, Event.title, Event.type, Event.date,
            func.count(Registration.id).label('registrations')
        ).outerjoin(Registration, Registration.event_id==Event.id)         .filter(Event.college_id==college_id)         .group_by(Event.id)         .order_by(desc('registrations'))
        data = [
            {'event_id': eid, 'title': title, 'type': etype, 'date': str(date), 'registrations': regs}
            for (eid, title, etype, date, regs) in q.all()
        ]
        return jsonify(data)

    @app.route('/reports/attendance')
    def attendance_report():
        event_id = request.args.get('event_id', type=int)
        q = db.session.query(
            func.avg(case((Attendance.status=='present', 1.0), else_=0.0)) * 100.0
        ).filter(Attendance.event_id==event_id)
        pct = q.scalar() or 0.0
        return jsonify({'event_id': event_id, 'attendance_percentage': round(pct,2)})

    @app.route('/reports/feedback')
    def feedback_report():
        event_id = request.args.get('event_id', type=int)
        q = db.session.query(func.avg(Feedback.rating)).filter(Feedback.event_id==event_id)
        avg_rating = q.scalar()
        return jsonify({'event_id': event_id, 'avg_rating': round(avg_rating,2) if avg_rating else None})

    @app.route('/reports/student_participation')
    def student_participation():
        student_id = request.args.get('student_id', type=int)
        q = db.session.query(func.count(Attendance.id)).filter(
            Attendance.student_id==student_id, Attendance.status=='present'
        )
        return jsonify({'student_id': student_id, 'events_attended': q.scalar()})

    @app.route('/reports/top_active_students')
    def top_active_students():
        college_id = request.args.get('college_id', type=int)
        limit = request.args.get('limit', default=3, type=int)
        q = db.session.query(
            Student.id, Student.name, func.count(Attendance.id).label('events_attended')
        ).join(Attendance, Attendance.student_id==Student.id)         .filter(Student.college_id==college_id, Attendance.status=='present')         .group_by(Student.id)         .order_by(desc('events_attended'))         .limit(limit)
        data = [{'student_id': sid, 'name': name, 'events_attended': cnt} for (sid, name, cnt) in q.all()]
        return jsonify(data)

    @app.route('/reports/event_summary')
    def event_summary():
        college_id = request.args.get('college_id', type=int)
        event_type = request.args.get('event_type', type=str)

        regs = db.session.query(Event.id, func.count(Registration.id).label('registrations'))            .outerjoin(Registration, Registration.event_id==Event.id)            .filter(Event.college_id==college_id, Event.type==event_type)            .group_by(Event.id).subquery()

        att = db.session.query(Event.id,
            (func.avg(case((Attendance.status=='present', 1.0), else_=0.0))*100.0).label('attendance_pct'))            .outerjoin(Attendance, Attendance.event_id==Event.id)            .filter(Event.college_id==college_id, Event.type==event_type)            .group_by(Event.id).subquery()

        fb = db.session.query(Event.id, func.avg(Feedback.rating).label('avg_rating'))            .outerjoin(Feedback, Feedback.event_id==Event.id)            .filter(Event.college_id==college_id, Event.type==event_type)            .group_by(Event.id).subquery()

        q = db.session.query(Event.id, Event.title, Event.date,
                             func.coalesce(regs.c.registrations, 0),
                             func.coalesce(att.c.attendance_pct, 0.0),
                             func.coalesce(fb.c.avg_rating, 0.0))            .outerjoin(regs, regs.c.id==Event.id)            .outerjoin(att, att.c.id==Event.id)            .outerjoin(fb, fb.c.id==Event.id)            .filter(Event.college_id==college_id, Event.type==event_type)            .order_by(Event.date.desc())

        data = []
        for eid, title, date, r, a, f in q.all():
            data.append({
                'event_id': eid, 'title': title, 'date': str(date),
                'registrations': int(r or 0),
                'attendance_pct': round(float(a or 0.0),2),
                'avg_rating': round(float(f or 0.0),2) if f is not None else None
            })
        return jsonify(data)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
