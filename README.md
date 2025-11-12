Attendance Tracker

**Author:** Ravi Kumar  
**Roll No.:** 2501940047  
**Course:** MCA (AI/ML)  
**Faculty:** Ms. Neha Kaushik  
**Assignment Title:**  Attendance Tracker  

---

## 🧾 Project Overview
This project is an advanced ** attendance tracking system** written in Python.  
It helps manage classroom attendance directly from the terminal — with data validation, 
summary generation, and optional saving to file.

---

##  Features
 Add or bulk-add student entries  
 Prevent duplicate or blank entries  
 Manual or automatic check-in time  
 Edit / Delete / Search entries  
 Formatted attendance summary  
 Absentee calculation  
 Save report to `.txt`  
 Persistent storage in `.csv`  
 Backup and export support  

---

## Output 1
No.  Name                      Check-in
---------------------------------------------
1    Riya Sharma               09:00 AM
2    Arjun Singh               09:10 AM
3    Meena Verma               09:15 AM
---------------------------------------------
Total Students Present: 3
Total Absent: 2

##Output 2 

======== Attendance Tracker (Advanced) ========
Choose an option: 7

===== Attendance Summary =====
No.  Name                      Check-in
---------------------------------------------
1    Riya Sharma               09:00 AM
2    Arjun Singh               10:15 AM
3    Meena Verma               09:20 AM
---------------------------------------------
Total Students Present: 3
Do you want to compute absentees (provide class strength)? (yes/no): yes
Enter total number of students in the class: 5
Total Present: 3
Total Absent : 2

##Output 3
======== Attendance Tracker (Advanced) ========
Choose an option: 8
Enter filename for report (default: attendance_report.txt): 

Report exported to 'attendance_report.txt'.

# File Created Content (attendance_report.txt)
KR Mangalam University — Attendance Report
Generated: 2025-11-12 09:10:25
==================================================
Name                           Check-in   Recorded At
--------------------------------------------------
Riya Sharma                    09:00 AM   2025-11-12 09:01:10
Arjun Singh                    10:15 AM   2025-11-12 09:02:04
Meena Verma                    09:20 AM   2025-11-12 09:03:17
--------------------------------------------------
Total Present: 3


