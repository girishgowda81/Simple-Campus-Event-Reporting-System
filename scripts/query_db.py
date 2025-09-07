import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect("D:\Downloads\CampusEventReporting-Prototype\instance\event_reporting.db")
cur = conn.cursor()

print("📌 Tables in the database:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cur.fetchall())

print("\n📌 Events:")
cur.execute("SELECT * FROM event;")
for row in cur.fetchall():
    print(row)

print("\n📌 Students:")
cur.execute("SELECT * FROM Student;")
for row in cur.fetchall():
    print(row)

print("\n📌 Registrations:")
# cur.execute("SELECT * FROM Registration;")
# for row in cur.fetchall():
#     print(row)

# Total registrations per event
cur.execute("""
SELECT e.title, COUNT(r.id) AS total_registrations
FROM event e
LEFT JOIN registration r ON e.id = r.event_id
GROUP BY e.id
ORDER BY total_registrations DESC
""")
print("📌 Event Popularity Report:")
for row in cur.fetchall():
    print(f"Event: {row[0]}, Total Registrations: {row[1]}")



print("\n📌 Attendance:")
cur.execute("SELECT * FROM Attendance;")
for row in cur.fetchall():
    print(row)

cur.execute("""
SELECT s.name, COUNT(DISTINCT a.id) AS attended_events
FROM student s
JOIN registration r ON s.id = r.student_id
JOIN attendance a ON r.id = a.event_id
WHERE a.status='present'
GROUP BY s.id
ORDER BY attended_events DESC
""")

print("\n📌 Student Participation Report:")
for row in cur.fetchall():
    print(f"Student: {row[0]}, Events Attended: {row[1]}")



# print("\n📌 Feedback:")
# cur.execute("SELECT * FROM Feedback;")
# for row in cur.fetchall():
#     print(row)
cur.execute("""
SELECT e.title, ROUND(AVG(f.rating), 2) AS avg_feedback
FROM event e
LEFT JOIN registration r ON e.id = r.event_id
LEFT JOIN feedback f ON r.id = f.event_id
GROUP BY e.id
ORDER BY avg_feedback DESC
""")
print("\n📌 Average Feedback Score per Event:")
for row in cur.fetchall():
    print(f"Event: {row[0]}, Average Rating: {row[1]}")


cur.execute("""
DELETE FROM attendance
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM attendance
    GROUP BY event_id
)
""")
conn.commit()    

conn.close()

