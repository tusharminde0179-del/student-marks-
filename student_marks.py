"""
MINI PROJECT: Student Marks Management System (Python)
Concepts : LIST   -> ranking / sorted results, topper lists
           TUPLE  -> fixed subject names, (roll, name, total, percent) result records
           DICT   -> students {roll: {"name": ..., "marks": {subject: mark}}}
           FILES  -> CSV file read/write, plus a text report file
Run      : python student_marks.py
"""

import csv
import os

DATA_FILE = "students.csv"
REPORT_FILE = "report.txt"

# TUPLE: fixed, unchangeable set of subjects
SUBJECTS = ("Maths", "Physics", "Chemistry", "Programming", "English")
MAX_MARKS = 100
PASS_MARKS = 40

# DICT of DICTs:
# students = {
#    40: {"name": "Nikhil", "marks": {"Maths": 80, "Physics": 70, ...}},
# }
students = {}


# ---------- File processing ----------
def load_data():
    """Read students.csv into the dictionary."""
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)                      # skip header row
            for row in reader:
                if len(row) != 2 + len(SUBJECTS):
                    continue                         # skip damaged lines
                roll = int(row[0])
                marks = {sub: int(m) for sub, m in zip(SUBJECTS, row[2:])}
                students[roll] = {"name": row[1], "marks": marks}
    except (OSError, ValueError):
        print("Warning: data file is damaged. Some records may be missing.")


def save_data():
    """Write the dictionary back to students.csv."""
    try:
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(("Roll", "Name") + SUBJECTS)   # tuple + tuple
            for roll in sorted(students):
                s = students[roll]
                writer.writerow([roll, s["name"]] + [s["marks"][sub] for sub in SUBJECTS])
    except OSError:
        print("Error: could not write to file.")


# ---------- Input helpers ----------
def read_int(prompt, low=None, high=None):
    while True:
        try:
            v = int(input(prompt))
            if (low is not None and v < low) or (high is not None and v > high):
                print(f"Enter a value between {low} and {high}.")
                continue
            return v
        except ValueError:
            print("Invalid input. Enter a whole number.")


def read_marks():
    marks = {}
    for sub in SUBJECTS:
        marks[sub] = read_int(f"  Marks in {sub} (0-{MAX_MARKS}): ", 0, MAX_MARKS)
    return marks


# ---------- Calculations ----------
def calc_result(roll):
    """Return a TUPLE: (roll, name, total, percentage, grade, status)."""
    s = students[roll]
    total = sum(s["marks"].values())
    percent = total / (MAX_MARKS * len(SUBJECTS)) * 100
    status = "PASS" if all(m >= PASS_MARKS for m in s["marks"].values()) else "FAIL"
    return (roll, s["name"], total, round(percent, 2), grade_of(percent, status), status)


def grade_of(percent, status):
    if status == "FAIL":
        return "F"
    if percent >= 85: return "A+"
    if percent >= 75: return "A"
    if percent >= 65: return "B"
    if percent >= 55: return "C"
    return "D"


# ---------- Operations ----------
def add_student():
    roll = read_int("Enter Roll No: ", 1)
    if roll in students:
        print("Roll number already exists.")
        return
    name = input("Enter Name   : ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    print("Enter marks:")
    students[roll] = {"name": name, "marks": read_marks()}
    save_data()
    print("Student added successfully.")


def view_all():
    if not students:
        print("No records found.")
        return
    header = f"\n{'Roll':<6}{'Name':<18}" + "".join(f"{s[:6]:<8}" for s in SUBJECTS) + f"{'Total':<7}{'%':<8}{'Grade':<6}"
    print(header)
    print("-" * len(header))
    for roll in sorted(students):
        s = students[roll]
        _, _, total, pct, grade, _ = calc_result(roll)       # tuple unpacking
        marks_str = "".join(f"{s['marks'][sub]:<8}" for sub in SUBJECTS)
        print(f"{roll:<6}{s['name'][:16]:<18}{marks_str}{total:<7}{pct:<8.2f}{grade:<6}")


def search_student():
    roll = read_int("Enter Roll No to search: ")
    if roll not in students:
        print("Student not found.")
        return
    r, name, total, pct, grade, status = calc_result(roll)
    print(f"\nRoll: {r}   Name: {name}")
    for sub, m in students[roll]["marks"].items():
        print(f"  {sub:<12}: {m}")
    print(f"  Total: {total}/{MAX_MARKS * len(SUBJECTS)}   Percentage: {pct}%   Grade: {grade}   Result: {status}")


def update_marks():
    roll = read_int("Enter Roll No to update: ")
    if roll not in students:
        print("Student not found.")
        return
    print("Enter new marks:")
    students[roll]["marks"] = read_marks()
    save_data()
    print("Marks updated.")


def delete_student():
    roll = read_int("Enter Roll No to delete: ")
    if students.pop(roll, None) is None:
        print("Student not found.")
        return
    save_data()
    print("Record deleted.")


def rank_list():
    if not students:
        print("No records found.")
        return
    # LIST of tuples, sorted by total marks (highest first)
    results = [calc_result(roll) for roll in students]
    results.sort(key=lambda r: r[2], reverse=True)
    print(f"\n{'Rank':<6}{'Roll':<6}{'Name':<18}{'Total':<8}{'%':<8}{'Grade':<6}")
    print("-" * 52)
    for rank, (roll, name, total, pct, grade, _) in enumerate(results, start=1):
        print(f"{rank:<6}{roll:<6}{name[:16]:<18}{total:<8}{pct:<8.2f}{grade:<6}")


def subject_analysis():
    if not students:
        print("No records found.")
        return
    print(f"\n{'Subject':<14}{'Average':<10}{'Highest':<18}{'Lowest':<8}")
    print("-" * 50)
    for sub in SUBJECTS:
        scores = [(s["marks"][sub], s["name"]) for s in students.values()]  # list of tuples
        avg = sum(m for m, _ in scores) / len(scores)
        high = max(scores)
        low = min(scores)
        print(f"{sub:<14}{avg:<10.2f}{high[1][:10] + ' (' + str(high[0]) + ')':<18}{low[0]:<8}")
    passed = sum(1 for r in students if calc_result(r)[5] == "PASS")
    print(f"\nPass: {passed}   Fail: {len(students) - passed}   "
          f"Pass %: {passed / len(students) * 100:.1f}")


def export_report():
    if not students:
        print("No records to export.")
        return
    results = sorted((calc_result(r) for r in students), key=lambda r: r[2], reverse=True)
    try:
        with open(REPORT_FILE, "w") as f:
            f.write("STUDENT MARKS REPORT\n")
            f.write("=" * 52 + "\n")
            f.write(f"{'Rank':<6}{'Roll':<6}{'Name':<18}{'Total':<8}{'%':<8}{'Result':<6}\n")
            for rank, (roll, name, total, pct, grade, status) in enumerate(results, 1):
                f.write(f"{rank:<6}{roll:<6}{name[:16]:<18}{total:<8}{pct:<8.2f}{status:<6}\n")
        print(f"Report written to {REPORT_FILE}")
    except OSError:
        print("Error: could not write report.")


# ---------- Main ----------
def main():
    load_data()
    menu = {1: add_student, 2: view_all, 3: search_student, 4: update_marks,
            5: delete_student, 6: rank_list, 7: subject_analysis, 8: export_report}
    while True:
        print("\n===== STUDENT MARKS MANAGEMENT =====")
        print("1. Add Student\n2. View All\n3. Search Student\n4. Update Marks")
        print("5. Delete Student\n6. Rank List\n7. Subject Analysis\n8. Export Report\n0. Exit")
        choice = read_int("Enter choice: ")
        if choice == 0:
            save_data()
            print("Data saved. Goodbye!")
            break
        action = menu.get(choice)
        action() if action else print("Invalid choice.")


if __name__ == "__main__":
    main()
