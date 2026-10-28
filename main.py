"""Interactive command-line entry point for the Student Grade Analytics tool."""

import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog

from src.grade_analytics.csv_loader import (
    load_grades_from_csv,
    load_students_from_csv,
)
from src.grade_analytics.json_report import (
    GradeReport,
    build_grade_report,
    write_json_report,
)
from src.grade_analytics.models import Grade, Student
from src.grade_analytics.semester import semester_sort_key
from src.grade_analytics.terminal_ui import (
    print_dashboard,
    print_header,
    print_workspace_menu,
    write_text_report,
)

STUDENTS_FILENAME = "students.csv"


def choose_input_file() -> Path | None:
    """Open a native file picker and return the selected CSV path."""
    root = tk.Tk()
    root.withdraw()

    try:
        root.attributes("-topmost", True)
        selected_file = filedialog.askopenfilename(
            parent=root,
            title="Choose a student grades CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
    finally:
        root.destroy()

    return Path(selected_file) if selected_file else None


def load_selected_file(path: Path) -> list[Grade] | None:
    """Load and validate a selected CSV file."""
    try:
        grades = load_grades_from_csv(path)
    except (OSError, ValueError) as error:
        print(f"\nCould not load '{path.name}': {error}")
        return None

    if not grades:
        print(f"\n'{path.name}' contains no grade records.")
        return None

    print(f"\nLoaded {len(grades)} grade records from '{path.name}'.")
    return grades


def load_student_profiles(grades_path: Path) -> list[Student] | None:
    """Load the optional students.csv stored beside the grades file.

    Returns None when the file is absent or invalid, so the analysis can
    continue without major and year groups.
    """
    students_path = grades_path.with_name(STUDENTS_FILENAME)

    if not students_path.is_file():
        return None

    try:
        students = load_students_from_csv(students_path)
    except (OSError, ValueError) as error:
        print(f"Warning: could not load '{students_path.name}': {error}")
        print("Continuing without major and year analysis.")
        return None

    print(f"Loaded {len(students)} student profiles from '{students_path.name}'.")
    return students


def choose_analysis_period(
    grades: list[Grade],
) -> tuple[str, list[Grade]] | None:
    """Choose the entire dataset, an academic year, or a semester."""
    periods: list[tuple[str, list[Grade]]] = [("Entire dataset", grades)]
    grades_by_year: defaultdict[str, list[Grade]] = defaultdict(list)
    grades_by_semester: defaultdict[str, list[Grade]] = defaultdict(list)

    for grade in grades:
        year, _ = grade.semester.split("-")
        grades_by_year[year].append(grade)
        grades_by_semester[grade.semester].append(grade)

    for year in sorted(grades_by_year, key=int):
        periods.append((f"Academic year {year}", grades_by_year[year]))

    semesters = sorted(grades_by_semester, key=semester_sort_key)

    for semester in semesters:
        periods.append((f"Semester {semester}", grades_by_semester[semester]))

    while True:
        print_header("CHOOSE ANALYSIS PERIOD")

        for index, (label, _) in enumerate(periods, start=1):
            print(f"{index:>2}. {label}")

        print(" 0. Cancel")

        choice = input("\nSelect one option: ").strip()

        if choice == "0":
            return None

        if not choice.isdigit() or not 1 <= int(choice) <= len(periods):
            print("Invalid selection. Please choose a listed option or 0 to cancel.")
            continue

        return periods[int(choice) - 1]


def show_dashboard(
    grades: list[Grade],
    period_label: str,
    students: list[Student] | None = None,
) -> GradeReport | None:
    """Generate and display the complete dashboard for a period."""
    if not grades:
        print("No grade records are available for this period.")
        return None

    report = build_grade_report(grades, students)
    print_dashboard(report, period_label)
    return report


def export_report(
    report: GradeReport,
    period_label: str,
    project_root: Path,
    source_path: Path,
) -> bool:
    """Export the current analysis to JSON and readable text."""
    period_name = period_label.lower().replace(" ", "_").replace("-", "_")
    filename = f"{source_path.stem}_{period_name}_report"
    reports_directory = project_root / "reports"

    json_path = reports_directory / f"{filename}.json"
    text_path = reports_directory / f"{filename}.txt"

    existing_paths = [path for path in (json_path, text_path) if path.exists()]

    if existing_paths:
        print("An export file already exists:")

        for path in existing_paths:
            print(f"  {path}")

        overwrite = input("Replace existing report file(s)? (y/n): ").strip().lower()

        if overwrite != "y":
            print("Export cancelled; existing files were not changed.")
            return False

    json_written = False

    try:
        write_json_report(report, json_path)
        json_written = True
        write_text_report(report, period_label, text_path)
    except OSError as error:
        print(f"Could not export reports: {error}")

        if json_written:
            print(f"JSON report was written to {json_path}; TXT export did not finish.")

        return False

    print("\nReports exported successfully.")
    print(f"JSON: {json_path}")
    print(f"Text: {text_path}")
    return True


def load_file_until_valid() -> tuple[Path, list[Grade]] | None:
    """Open the file picker until a valid file is chosen or cancelled."""
    while True:
        selected_path = choose_input_file()

        if selected_path is None:
            return None

        grades = load_selected_file(selected_path)

        if grades is not None:
            return selected_path, grades

        retry = input("Choose another file? (y/n): ").strip().lower()

        if retry != "y":
            return None


def main() -> None:
    """Run the student grade analytics application."""
    project_root = Path(__file__).resolve().parent
    selected_file = load_file_until_valid()

    if selected_file is None:
        print("No file selected. Goodbye!")
        return

    source_path, grades = selected_file
    students = load_student_profiles(source_path)

    while True:
        selected_period = choose_analysis_period(grades)

        if selected_period is None:
            print("No analysis period selected. Goodbye!")
            return

        period_label, period_grades = selected_period
        report = show_dashboard(period_grades, period_label, students)

        if report is None:
            continue

        while True:
            print_workspace_menu(source_path.name, period_label)
            choice = input("Choose an action (1-4): ").strip()

            if choice == "1":
                export_report(report, period_label, project_root, source_path)

            elif choice == "2":
                break

            elif choice == "3":
                replacement = load_file_until_valid()

                if replacement is not None:
                    source_path, grades = replacement
                    students = load_student_profiles(source_path)
                    break

            elif choice == "4":
                print("Thank you for using Student Grade Analytics!")
                return

            else:
                print("Invalid choice. Enter 1, 2, 3, or 4.")
                continue

            input("\nPress Enter to return to the dashboard workspace...")


if __name__ == "__main__":
    main()
