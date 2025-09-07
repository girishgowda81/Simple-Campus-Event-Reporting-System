# Design Document – Campus Event Reporting

## 1) Data to Track
- Event creation (title, type, date, college).
- Student registration (student ↔ event).
- Attendance (present/absent and timestamp).
- Feedback (rating 1–5, optional comment).

## 2) Scale Assumptions
- ~50 colleges, ~500 students/college, ~20 events/semester.
- Event IDs are globally unique (SQLite autoincrement). College scoping is enforced via `college_id`.
- Single multi-tenant database with `college_id` foreign key on tenant-owned records.

## 3) ER Diagram (text)
```
College (id, name)
Student (id, name, email, college_id)
Event   (id, title, type, date, college_id)
Registration (id, student_id, event_id, created_at)
Attendance   (id, student_id, event_id, status, marked_at)
Feedback     (id, student_id, event_id, rating, comment, created_at)
```
- Unique constraints:
  - A student can register at most once per event.
  - A student can have at most one attendance record per event.
  - A student can have at most one feedback entry per event.

## 4) API Design (REST)
- `POST /colleges` → create a college.
- `POST /students` → create a student.
- `POST /events` → create an event.
- `POST /register` → register a student to an event.
- `POST /attendance` → mark attendance (`present` or `absent`).
- `POST /feedback` → submit rating (1–5) + optional comment.

### Reporting Endpoints
- `GET /reports/event_popularity?college_id=` → registrations per event (desc).
- `GET /reports/attendance?event_id=` → attendance % for an event.
- `GET /reports/feedback?event_id=` → average feedback score.
- `GET /reports/student_participation?student_id=` → events attended count.
- `GET /reports/top_active_students?college_id=&limit=3` → top N students by attendance.
- `GET /reports/event_summary?college_id=&event_type=` → registrations + attendance + avg rating for events of a given type.

## 5) Workflows
### Registration → Attendance → Reporting
1. Admin creates college, students, events.
2. Student registers for an event (`/register`).
3. On event day, staff marks attendance (`/attendance`).
4. After event, student submits feedback (`/feedback`).
5. Reports consumed via `/reports/*`.

## 6) Assumptions & Edge Cases
- Duplicate registration returns 409 Conflict.
- Attendance without prior registration returns 400.
- Feedback requires prior registration; duplicate feedback returns 409.
- Cancelled events could be modeled with `status` field on Event (omitted in prototype for brevity).
- Basic input validation only in prototype.

## 7) Security & Multi-Tenancy (prototype-level)
- No auth in prototype. In production: JWT + role-based access (Admin, Organizer, Student).
- All queries filter by `college_id` where applicable to prevent cross-tenant leakage.

## 8) Future Enhancements
- Pagination & search on list endpoints.
- Admin UI + Student mobile app.
- Soft deletes and audit logs.
- Check-in via QR codes.
