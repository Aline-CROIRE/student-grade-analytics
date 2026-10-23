import csv
from pathlib import Path

from src.grade_analytics.models import Grade

REQUIRED_COLUMNS = {
    "student_id",
    "course_id",
    "score",
    "semester",
}


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

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing headers")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV headers must not contain duplicate columns")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required CSV columns: {missing}")

        try:
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(f"Malformed CSV row {row_number}: too many fields")

                for column in ("student_id", "course_id", "semester", "score"):
                    if not (row.get(column) or "").strip():
                        raise ValueError(
                            f"Required field '{column}' is empty on row {row_number}"
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
