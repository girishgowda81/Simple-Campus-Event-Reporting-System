# Campus Event Reporting – Prototype

This project is my take on building a simple Campus Event Reporting System as part of the Webknot Campus Drive assignment. The goal was to design and implement a basic system where college staff can create events, and students can register, attend, and give feedback.<br>

I treated this as a small but real-world problem: every campus organizes hackathons, workshops, fests, etc., and managing registrations + attendance manually can get messy. So I built a prototype that captures the essential registrations, attendance, and reports without over-engineering things.

# Key Assumptions & Decisions
•	I assumed each college would have its own set of events and students, but for this prototype I kept all data in a single SQLite database for simplicity.<br>
•	Event IDs are unique within the system.<br>
•	A student can’t register twice for the same event (handled at DB/API level).<br>
•	Feedback is optional, but if given it should be a rating between 1–5.<br>

# Tech Stack
•	Python (Flask) for APIs <br>
•	SQLite as the database (lightweight, easy to set up) <br>
•	Requests.http file for testing endpoints quickly <br>
•	SQL queries for generating event and student reports <br>

# What Works Right Now
•	Students can register for events <br>
•	Admin can mark attendance <br>
•	Students can submit feedback (1–5 rating) <br>
•	Reports available: <br>
    o	Total registrations per event <br>
    o	Attendance percentage  <br>
    o	Average feedback score  <br>
    o	Top 3 most active students  <br>

# test
<img width="2560" height="1258" alt="image" src="https://github.com/user-attachments/assets/2d6f5119-955c-4c66-a153-b76507cb1163" />
<img width="2082" height="1340" alt="Screenshot 2025-09-07 142715" src="https://github.com/user-attachments/assets/964ae893-47ff-4e5d-8770-733d598fd985" />

    






