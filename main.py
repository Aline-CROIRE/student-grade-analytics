import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from src.grade_analytics.csv_loader import load_grades_from_csv
from src.grade_analytics.json_report import (
    GradeReport,
    build_grade_report,
    write_json_report,
)
from src.grade_analytics.models import Grade
from src.grade_analytics.terminal_ui import (
    print_dashboard,
    print_header,
    print_workspace_menu,
    write_text_report,
)


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


def choose_analysis_period(
    grades: list[Grade],
) -> tuple[str, list[Grade]] | None:
    """Choose the entire dataset, an academic year, or a semester."""
    periods: list[tuple[str, list[Grade]]] = [("Entire dataset", grades)]

    years = sorted({grade.semester.split("-")[0] for grade in grades})

    for year in years:
        year_grades = [
            grade for grade in grades if grade.semester.startswith(f"{year}-")
        ]
        periods.append((f"Academic year {year}", year_grades))

    semesters = sorted({grade.semester for grade in grades})

    for semester in semesters:
        semester_grades = [grade for grade in grades if grade.semester == semester]
        periods.append((f"Semester {semester}", semester_grades))

    print_header("CHOOSE ANALYSIS PERIOD")
    for index, (label, _) in enumerate(periods, start=1):
        print(f"{index:>2}. {label}")
    print(" 0. Cancel")

    choice = input("\nSelect one option: ").strip()

    if choice == "0":
        return None

    if not choice.isdigit() or not 1 <= int(choice) <= len(periods):
        print("Invalid selection.")
        return None

    return periods[int(choice) - 1]


def show_dashboard(
    grades: list[Grade],
    period_label: str,
) -> GradeReport | None:
    """Generate and display the complete dashboard for a period."""
    if not grades:
        print("No grade records are available for this period.")
        return None

    report = build_grade_report(grades)
    print_dashboard(report, period_label)
    return report


def export_report(
    report: GradeReport,
    period_label: str,
    project_root: Path,
    source_path: Path,
) -> None:
    """Export the current analysis to JSON and readable text."""
    period_name = period_label.lower().replace(" ", "_").replace("-", "_")
    filename = f"{source_path.stem}_{period_name}_report"
    reports_directory = project_root / "reports"

    json_path = reports_directory / f"{filename}.json"
    text_path = reports_directory / f"{filename}.txt"

    write_json_report(report, json_path)
    write_text_report(report, period_label, text_path)

    print("\nReports exported successfully.")
    print(f"JSON: {json_path}")
    print(f"Text: {text_path}")


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

    while True:
        selected_period = choose_analysis_period(grades)

        if selected_period is None:
            print("No analysis period selected. Goodbye!")
            return

        period_label, period_grades = selected_period
        report = show_dashboard(period_grades, period_label)

        if report is None:
            continue

        while True:
            print_workspace_menu(source_path.name, period_label)
            choice = input("Choose an action (1-4): ").strip()

            if choice == "1":
                try:
                    export_report(
                        report,
                        period_label,
                        project_root,
                        source_path,
                    )
                except OSError as error:
                    print(f"Could not export reports: {error}")

            elif choice == "2":
                break

            elif choice == "3":
                replacement = load_file_until_valid()
                if replacement is not None:
                    source_path, grades = replacement
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
