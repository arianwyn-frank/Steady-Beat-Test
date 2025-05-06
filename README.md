# Steady-Beat-Test
My steady beat tester, BeatSteady, is a web-based application designed for elementary music classrooms. It helps students test their ability to keep a consistent beat and gives teachers and researchers precise, millisecond-level insights into student rhythm accuracy.

Objective
- Students tap along to steady beats at 100 BPM and 120 BPM
- The app records each tap’s timing offset in milliseconds
- Teachers can monitor progress and identify rhythm challenges
- Researchers can use the timing data for quantitative analysis of tempo accuracy

Backend
The backend is built on a lightweight yet powerful SQLite3 database that automatically creates and manages:
- users: student login and profile info
- classrooms: grouped cohorts for teacher access
- scores: performance logs for each test session

Setup Instructions
1) Clone the repository
2) Ensure you have Python installed (version 3.7 or higher recommended)
3) From the project directory, run:
  - python app.py
3) Open your browser and go to:
  - http://localhost:5000
That’s it—you’re ready to start testing steady beats!
