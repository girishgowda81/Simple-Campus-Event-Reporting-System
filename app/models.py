from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)

    __table_args__ = (UniqueConstraint('email','college_id', name='uq_student_email_college'),)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Workshop/Fest/Seminar/etc.
    date = db.Column(db.Date, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint('student_id','event_id', name='uq_registration'),)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present/absent
    marked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint('student_id','event_id', name='uq_attendance'),)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1..5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint('student_id','event_id', name='uq_feedback'),)
