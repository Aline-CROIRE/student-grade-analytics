import csv
from collections.abc import Sequence
from pathlib import Path

from src.grade_analytics.models import Grade, Student

REQUIRED_COLUMNS = {
    "student_id",
    "course_id",
    "score",
    "semester",
}

STUDENT_COLUMNS = ("student_id", "name", "major", "year")


def _validate_headers(
    fieldnames: Sequence[str] | None,
    required_columns: set[str],
) -> None:
    """Raise ValueError if CSV headers are missing, duplicated, or incomplete."""
    if not fieldnames:
        raise ValueError("CSV file is empty or missing headers")

    if len(fieldnames) != len(set(fieldnames)):
        raise ValueError("CSV headers must not contain duplicate columns")

    missing_columns = required_columns - set(fieldnames)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required CSV columns: {missing}")


def _validate_row_fields(
    row: dict[str | None, str | None],
    row_number: int,
    columns: Sequence[str],
) -> None:
    """Raise ValueError if a row has extra fields or empty required values."""
    if None in row:
        raise ValueError(f"Malformed CSV row {row_number}: too many fields")

    for column in columns:
        if not (row.get(column) or "").strip():
            raise ValueError(f"Required field '{column}' is empty on row {row_number}")


def load_grades_from_csv(file_path: str | Path) -> list[Grade]:
    """Load and validate grade records from a CSV file.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Validated grade records as Grade objects.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If headers or row data are invalid.
    """
    grades: list[Grade] = []
    path = Path(file_path)

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, strict=True)
        _validate_headers(reader.fieldnames, REQUIRED_COLUMNS)

        try:
            for row_number, row in enumerate(reader, start=2):
                _validate_row_fields(
                    row,
                    row_number,
                    ("student_id", "course_id", "semester", "score"),
                )

                raw_score = row["score"].strip()
                try:
                    score = float(raw_score)
                except ValueError as error:
                    raise ValueError(
                        f"Invalid score on row {row_number}: "
                        f"{raw_score!r} is not a number"
                    ) from error

                semester = row["semester"].strip()
                try:
                    grade = Grade(
                        student_id=row["student_id"].strip(),
                        course_id=row["course_id"].strip(),
                        score=score,
                        semester=semester,
                    )
                except ValueError as error:
                    kind = "score" if str(error).startswith("Score") else "semester"
                    raise ValueError(
                        f"Invalid {kind} on row {row_number}: {error}"
                    ) from error

                grades.append(grade)
        except csv.Error as error:
            raise ValueError(f"Malformed CSV data: {error}") from error

    return grades


def load_students_from_csv(file_path: str | Path) -> list[Student]:
    """Load and validate student profiles from a CSV file.

    The file must contain student_id, name, major, and year columns, with one
    row per student.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Validated student profiles as Student objects.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If headers or row data are invalid, or a student_id
            appears more than once.
    """
    students: list[Student] = []
    seen_ids: set[str] = set()
    path = Path(file_path)

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, strict=True)
        _validate_headers(reader.fieldnames, set(STUDENT_COLUMNS))

        try:
            for row_number, row in enumerate(reader, start=2):
                _validate_row_fields(row, row_number, STUDENT_COLUMNS)

                student_id = row["student_id"].strip()
                if student_id in seen_ids:
                    raise ValueError(
                        f"Duplicate student_id {student_id!r} on row {row_number}"
                    )

                raw_year = row["year"].strip()
                if not (raw_year.isascii() and raw_year.isdigit()) or int(raw_year) < 1:
                    raise ValueError(
                        f"Invalid year on row {row_number}: "
                        f"{raw_year!r} is not a positive whole number"
                    )

                seen_ids.add(student_id)
                students.append(
                    Student(
                        student_id=student_id,
                        name=row["name"].strip(),
                        major=row["major"].strip(),
                        year=int(raw_year),
                    )
                )
        except csv.Error as error:
            raise ValueError(f"Malformed CSV data: {error}") from error

    return students
