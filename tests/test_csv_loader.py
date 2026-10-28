from collections.abc import Iterator
from pathlib import Path

import pytest

from src.grade_analytics.csv_loader import (
    iter_grades_from_csv,
    load_grades_from_csv,
    load_students_from_csv,
)
from src.grade_analytics.models import Grade, Student


def test_load_grades_from_csv(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\n"
        "S001,CS101,85,2026-S1\n"
        "S002,CS102,72.5,2026-S1\n",
        encoding="utf-8",
    )

    grades = load_grades_from_csv(csv_path)

    assert grades == [
        Grade("S001", "CS101", 85.0, "2026-S1"),
        Grade("S002", "CS102", 72.5, "2026-S1"),
    ]


def test_reject_csv_missing_required_column(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score\n" "S001,CS101,85\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Missing required CSV columns: semester",
    ):
        load_grades_from_csv(csv_path)


def test_loads_utf8_bom_csv(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "\ufeffstudent_id,course_id,score,semester\nS001,CS101,85,2026-S1\n",
        encoding="utf-8",
    )

    assert load_grades_from_csv(csv_path) == [Grade("S001", "CS101", 85.0, "2026-S1")]


def test_rejects_duplicate_headers(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,score,semester\nS001,CS101,85,86,2026-S1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate columns"):
        load_grades_from_csv(csv_path)


def test_rejects_extra_fields_on_csv_row(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\nS001,CS101,85,2026-S1,extra\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Malformed CSV row 2"):
        load_grades_from_csv(csv_path)


def test_rejects_malformed_quoted_csv_record(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        'student_id,course_id,score,semester\n"S001,CS101,85,2026-S1\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Malformed CSV data"):
        load_grades_from_csv(csv_path)


def test_rejects_invalid_semester_on_csv_row(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\nS001,CS101,85,2026-S3\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid semester on row 2"):
        load_grades_from_csv(csv_path)


def test_reject_invalid_score(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\n" "S001,CS101,not-a-number,2026-S1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid score on row 2"):
        load_grades_from_csv(csv_path)


def test_reject_empty_csv(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="CSV file is empty or missing headers",
    ):
        load_grades_from_csv(csv_path)


def test_missing_file_raises_file_not_found(tmp_path):
    csv_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_grades_from_csv(csv_path)


def test_reject_empty_student_id(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\n" ",CS101,85,2026-S1\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Required field 'student_id' is empty on row 2",
    ):
        load_grades_from_csv(csv_path)


@pytest.mark.parametrize("score", ["-1", "100.1"])
def test_reject_score_outside_valid_range(tmp_path, score):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\n" f"S001,CS101,{score},2026-S1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid score on row 2"):
        load_grades_from_csv(csv_path)


@pytest.mark.parametrize("score", ["0", "100"])
def test_accept_boundary_scores(tmp_path, score):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\n" f"S001,CS101,{score},2026-S1\n",
        encoding="utf-8",
    )

    grades = load_grades_from_csv(csv_path)

    assert grades[0].score == float(score)


def test_load_students_from_csv(tmp_path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "student_id,name,major,year\n"
        "S001, Alice ,Computing,2\n"
        "S002,Brian,Engineering,1\n",
        encoding="utf-8",
    )

    students = load_students_from_csv(csv_path)

    assert students == [
        Student("S001", "Alice", "Computing", 2),
        Student("S002", "Brian", "Engineering", 1),
    ]


def test_reject_students_csv_missing_required_column(tmp_path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text("student_id,name,year\nS001,Alice,2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required CSV columns: major"):
        load_students_from_csv(csv_path)


def test_reject_empty_student_major(tmp_path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "student_id,name,major,year\nS001,Alice,,2\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Required field 'major' is empty on row 2"):
        load_students_from_csv(csv_path)


@pytest.mark.parametrize("year", ["0", "-1", "two", "1.5", "²"])
def test_reject_invalid_student_year(tmp_path, year):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        f"student_id,name,major,year\nS001,Alice,Computing,{year}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid year on row 2"):
        load_students_from_csv(csv_path)


def test_reject_duplicate_student_id(tmp_path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "student_id,name,major,year\n"
        "S001,Alice,Computing,2\n"
        "S001,Alicia,Business,1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate student_id 'S001' on row 3"):
        load_students_from_csv(csv_path)


def test_reject_students_row_with_extra_fields(tmp_path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "student_id,name,major,year\nS001,Alice,Computing,2,extra\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="too many fields"):
        load_students_from_csv(csv_path)


def test_iter_grades_from_csv_yields_records_one_at_a_time(tmp_path):
    csv_path = tmp_path / "grades.csv"
    csv_path.write_text(
        "student_id,course_id,score,semester\n"
        "S001,CS101,85,2026-S1\n"
        "S002,CS102,not-a-score,2026-S1\n",
        encoding="utf-8",
    )

    records = iter_grades_from_csv(csv_path)

    assert isinstance(records, Iterator)
    assert next(records) == Grade("S001", "CS101", 85.0, "2026-S1")
    with pytest.raises(ValueError, match="Invalid score on row 3"):
        next(records)


def test_iter_grades_matches_list_loader_on_sample_data():
    sample_csv = Path(__file__).resolve().parent.parent / "data" / "grades.csv"

    assert list(iter_grades_from_csv(sample_csv)) == load_grades_from_csv(sample_csv)
