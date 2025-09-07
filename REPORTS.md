# Reports & SQL

## Event Popularity (registrations per event, desc)
```sql
SELECT e.id, e.title, e.type, e.date,
       COUNT(r.id) AS registrations
FROM Event e
LEFT JOIN Registration r ON r.event_id = e.id
WHERE e.college_id = :college_id
GROUP BY e.id
ORDER BY registrations DESC;
```

## Attendance % for a given event
```sql
SELECT e.id, e.title,
       AVG(CASE WHEN a.status = 'present' THEN 1.0 ELSE 0.0 END) * 100 AS attendance_percentage
FROM Event e
LEFT JOIN Attendance a ON a.event_id = e.id
WHERE e.id = :event_id
GROUP BY e.id;
```

## Average Feedback Score for an event
```sql
SELECT e.id, e.title, ROUND(AVG(f.rating), 2) AS avg_rating
FROM Event e
JOIN Feedback f ON f.event_id = e.id
WHERE e.id = :event_id
GROUP BY e.id;
```

## Student Participation (events attended)
```sql
SELECT s.id, s.name, COUNT(a.id) AS events_attended
FROM Student s
JOIN Attendance a ON a.student_id = s.id AND a.status = 'present'
WHERE s.id = :student_id
GROUP BY s.id;
```

## Top 3 Most Active Students (by attendance)
```sql
SELECT s.id, s.name, COUNT(a.id) AS events_attended
FROM Student s
JOIN Attendance a ON a.student_id = s.id AND a.status = 'present'
WHERE s.college_id = :college_id
GROUP BY s.id
ORDER BY events_attended DESC
LIMIT :limit;
```

## Event Summary by Type (registrations, attendance, avg rating)
```sql
WITH regs AS (
  SELECT e.id, COUNT(r.id) AS registrations
  FROM Event e
  LEFT JOIN Registration r ON r.event_id = e.id
  WHERE e.college_id = :college_id AND e.type = :event_type
  GROUP BY e.id
),
att AS (
  SELECT e.id,
         AVG(CASE WHEN a.status='present' THEN 1.0 ELSE 0.0 END) * 100 AS attendance_pct
  FROM Event e
  LEFT JOIN Attendance a ON a.event_id = e.id
  WHERE e.college_id = :college_id AND e.type = :event_type
  GROUP BY e.id
),
fb AS (
  SELECT e.id, ROUND(AVG(f.rating),2) AS avg_rating
  FROM Event e
  LEFT JOIN Feedback f ON f.event_id = e.id
  WHERE e.college_id = :college_id AND e.type = :event_type
  GROUP BY e.id
)
SELECT e.id, e.title, e.date,
       COALESCE(regs.registrations,0) AS registrations,
       COALESCE(att.attendance_pct,0) AS attendance_pct,
       COALESCE(fb.avg_rating,0) AS avg_rating
FROM Event e
LEFT JOIN regs ON regs.id = e.id
LEFT JOIN att  ON att.id  = e.id
LEFT JOIN fb   ON fb.id   = e.id
WHERE e.college_id = :college_id AND e.type = :event_type
ORDER BY e.date DESC;
```
