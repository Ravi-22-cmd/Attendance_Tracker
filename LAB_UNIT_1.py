"""
-----------------------------------------------------------------------------
Name        : Ravi Kumar
Date        : 12 November 2025
Assignment  : Advanced Command Line Attendance Tracker
Course      : MCA (AI/ML) - Programming for Problem Solving Using Python
Faculty     : Ms. Neha Kaushik
-----------------------------------------------------------------------------

Features:
- Menu-driven CLI: add, bulk add, view, search, edit, delete, summary
- Persistent storage in 'attendance.csv' (creates if missing)
- Flexible time parsing and validation (e.g., "09:15", "9:15 AM", "09:15 AM")
- Optional auto-timestamping using system time
- Class roster mode to compute absentees
- Export report to text file with generation timestamp
- Backup CSV file creation
- Case-insensitive duplicate prevention
-----------------------------------------------------------------------------

Usage: python tracker.py
"""
import csv
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple

CSV_FILE = "attendance.csv"
BACKUP_FILE = "attendance_backup.csv"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "check_in_time", "recorded_at"])
        print(f"Created new attendance file: {CSV_FILE}")


def load_attendance() -> List[Dict[str, str]]:
    ensure_csv()
    rows = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({"name": r["name"], "check_in_time": r["check_in_time"], "recorded_at": r["recorded_at"]})
    return rows


def save_attendance(rows: List[Dict[str, str]]): 
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "check_in_time", "recorded_at"])
        writer.writeheader()
        writer.writerows(rows)


def backup_csv():
    if os.path.exists(CSV_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"attendance_backup_{timestamp}.csv"
        shutil.copy(CSV_FILE, backup_name)
        print(f"Backup created: {backup_name}")


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())  


def name_exists(rows: List[Dict[str, str]], name: str) -> bool:
    return any(r["name"].lower() == name.lower() for r in rows)


def parse_time_input(time_str: str) -> str:
    s = time_str.strip()
    formats = ["%I:%M %p", "%H:%M", "%I:%M%p", "%H:%M:%S"]
    last_exc = None
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%I:%M %p") 
        except Exception as e:
            last_exc = e

    s2 = s.replace(" ", "").upper()
    if len(s2) in (3, 4) and s2.isdigit():
        # 915 -> 09:15
        if len(s2) == 3:
            s2 = "0" + s2
        return f"{s2[:2]}:{s2[2:]}".strip()
    raise ValueError(f"Could not parse time '{time_str}'. Please enter like '09:15' or '09:15 AM'.")



def add_single_entry(rows: List[Dict[str, str]]):
    name = input("Enter student name: ").strip()
    name = normalize_name(name)
    if not name:
        print("Name cannot be empty.")
        return
    if name_exists(rows, name):
        print("Duplicate entry — this student is already present.")
        return

    choice = input("Enter check-in time manually or use current time? (manual/now): ").strip().lower()
    if choice in ("now", "current", "n"):
        check_in = datetime.now().strftime("%I:%M %p")
    else:
        raw = input("Enter check-in time (e.g., 09:15 AM): ").strip()
        try:
            check_in = parse_time_input(raw)
        except ValueError as e:
            print(e)
            return

    recorded_at = datetime.now().strftime(DATE_FORMAT)
    rows.append({"name": name, "check_in_time": check_in, "recorded_at": recorded_at})
    save_attendance(rows)
    print(f"Recorded: {name} at {check_in}")


def bulk_add(rows: List[Dict[str, str]]):
    try:
        n = int(input("How many entries do you want to add? "))
    except ValueError:
        print("Invalid number.")
        return
    for i in range(n):
        print(f"\nEntry {i+1}/{n}")
        add_single_entry(rows)


def view_all(rows: List[Dict[str, str]]):
    if not rows:
        print("No attendance records yet.")
        return
    print("\n===== Attendance Records =====")
    print(f"{'No.':<4} {'Name':<25} {'Check-in':<10} {'Recorded At'}")
    print("-" * 65)
    for i, r in enumerate(rows, 1):
        print(f"{i:<4} {r['name']:<25} {r['check_in_time']:<10} {r['recorded_at']}")
    print("-" * 65)
    print(f"Total records: {len(rows)}")


def search_entries(rows: List[Dict[str, str]]):
    q = input("Search by name (partial allowed): ").strip().lower()
    if not q:
        print("Empty query.")
        return
    found = [r for r in rows if q in r["name"].lower()]
    if not found:
        print("No matching records.")
        return
    print(f"Found {len(found)} record(s):")
    for i, r in enumerate(found, 1):
        print(f"{i}. {r['name']} — {r['check_in_time']} (recorded {r['recorded_at']})")


def edit_entry(rows: List[Dict[str, str]]):
    view_all(rows)
    if not rows:
        return
    try:
        idx = int(input("Enter record number to edit (0 to cancel): "))
    except ValueError:
        print("Invalid number.")
        return
    if idx == 0:
        return
    if not (1 <= idx <= len(rows)):
        print("Index out of range.")
        return
    rec = rows[idx - 1]
    print(f"Editing: {rec['name']} — {rec['check_in_time']}")
    new_name = input("New name (leave blank to keep): ").strip()
    if new_name:
        new_name = normalize_name(new_name)
        if name_exists([r for i, r in enumerate(rows) if i != idx - 1], new_name):
            print("Another record with this name exists. Aborting rename.")
            return
        rec["name"] = new_name
    new_time = input("New check-in time (leave blank to keep): ").strip()
    if new_time:
        try:
            rec["check_in_time"] = parse_time_input(new_time)
        except ValueError as e:
            print(e)
            return
    rec["recorded_at"] = datetime.now().strftime(DATE_FORMAT)
    save_attendance(rows)
    print("Record updated.")


def delete_entry(rows: List[Dict[str, str]]):
    view_all(rows)
    if not rows:
        return
    try:
        idx = int(input("Enter record number to delete (0 to cancel): "))
    except ValueError:
        print("Invalid number.")
        return
    if idx == 0:
        return
    if not (1 <= idx <= len(rows)):
        print("Index out of range.")
        return
    rec = rows.pop(idx - 1)
    save_attendance(rows)
    print(f"Deleted record: {rec['name']} — {rec['check_in_time']}")


def attendance_summary(rows: List[Dict[str, str]]):
    print("\n===== Attendance Summary =====")
    if not rows:
        print("No records.")
        return
    sorted_rows = sorted(rows, key=lambda r: r["recorded_at"])
    print(f"{'No.':<4} {'Name':<25} {'Check-in'}")
    print("-" * 45)
    for i, r in enumerate(sorted_rows, 1):
        print(f"{i:<4} {r['name']:<25} {r['check_in_time']}")
    print("-" * 45)
    total_present = len(sorted_rows)
    print(f"Total Students Present: {total_present}")

  
    choice = input("Do you want to compute absentees (provide class strength)? (yes/no): ").strip().lower()
    if choice in ("yes", "y"):
        try:
            total = int(input("Enter total number of students in the class: "))
            if total < total_present:
                print("Warning: Present count exceeds total students.")
            absent = max(0, total - total_present)
            print(f"Total Present: {total_present}")
            print(f"Total Absent : {absent}")
        except ValueError:
            print("Invalid number for class strength.")


def export_report(rows: List[Dict[str, str]]):
    if not rows:
        print("No records to export.")
        return
    filename = input("Enter filename for report (default: attendance_report.txt): ").strip()
    if not filename:
        filename = "attendance_report.txt"
    if not filename.lower().endswith(".txt"):
        filename += ".txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("KR Mangalam University — Attendance Report\n")
        f.write(f"Generated: {datetime.now().strftime(DATE_FORMAT)}\n")
        f.write("=" * 50 + "\n")
        f.write(f"{'Name':<30} {'Check-in':<10} {'Recorded At'}\n")
        f.write("-" * 50 + "\n")
        for r in rows:
            f.write(f"{r['name']:<30} {r['check_in_time']:<10} {r['recorded_at']}\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total Present: {len(rows)}\n")
    print(f"Report exported to '{filename}'.")


def main_menu():
    rows = load_attendance()
    while True:
        print("\n----------Attendance Tracker  -----------------------------")
        print("1. Add single entry")
        print("2. Bulk add entries")
        print("3. View all records")
        print("4. Search by name")
        print("5. Edit a record")
        print("6. Delete a record")
        print("7. Attendance summary & absentees")
        print("8. Export report to TXT")
        print("9. Backup CSV")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_single_entry(rows)
            rows = load_attendance()
        elif choice == "2":
            bulk_add(rows)
            rows = load_attendance()
        elif choice == "3":
            view_all(rows)
        elif choice == "4":
            search_entries(rows)
        elif choice == "5":
            edit_entry(rows)
            rows = load_attendance()
        elif choice == "6":
            delete_entry(rows)
            rows = load_attendance()
        elif choice == "7":
            attendance_summary(rows)
        elif choice == "8":
            export_report(rows)
        elif choice == "9":
            backup_csv()
        elif choice == "0":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main_menu()
