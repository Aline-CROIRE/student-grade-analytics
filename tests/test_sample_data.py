import json
from pathlib import Path

import pytest

from src.grade_analytics.csv_loader import (
    load_grades_from_csv,
    load_students_from_csv,
)
from src.grade_analytics.json_report import (
    GradeReport,
    build_grade_report,
    round_report_values,
    write_json_report,
)

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
SAMPLE_CSV = DATA_DIRECTORY / "grades.csv"
SAMPLE_STUDENTS_CSV = DATA_DIRECTORY / "students.csv"


@pytest.fixture
def sample_report() -> GradeReport:
    """Build a report from the sample dataset shipped with the project."""
    return build_grade_report(load_grades_from_csv(SAMPLE_CSV))


def test_sample_csv_loads_all_records() -> None:
    grades = load_grades_from_csv(SAMPLE_CSV)

    assert len(grades) == 10
    assert {grade.student_id for grade in grades} == {
        "S001",
        "S002",
        "S003",
        "S004",
        "S005",
    }
    assert {grade.course_id for grade in grades} == {"CS101", "CS102"}


def test_sample_students_cover_every_graded_student() -> None:
    students = load_students_from_csv(SAMPLE_STUDENTS_CSV)
    grades = load_grades_from_csv(SAMPLE_CSV)

    assert len(students) == 5
    assert {student.student_id for student in students} == {
        grade.student_id for grade in grades
    }


def test_sample_summary_statistics(sample_report: GradeReport) -> None:
    assert sample_report["summary"] == {
        "count": 10,
        "mean": pytest.approx(79.8),
        "median": 82.5,
        "minimum": 55.0,
        "maximum": 100.0,
    }


def test_sample_grade_distribution(sample_report: GradeReport) -> None:
    assert sample_report["grade_distribution"] == {
        "A": 3,
        "B": 3,
        "C": 2,
        "D": 1,
        "F": 1,
    }


def test_sample_semester_trends(sample_report: GradeReport) -> None:
    trends = sample_report["semester_trends"]

    assert [trend["semester"] for trend in trends] == ["2026-S1", "2026-S2"]
    assert trends[0]["average"] == pytest.approx(76.0)
    assert trends[0]["change"] is None
    assert trends[1]["average"] == pytest.approx(83.6)
    assert trends[1]["change"] == pytest.approx(7.6)
    assert trends[0]["rolling_average"] == pytest.approx(76.0)
    assert trends[1]["rolling_average"] == pytest.approx(79.8)


def test_sample_pass_fail(sample_report: GradeReport) -> None:
    pass_fail = sample_report["pass_fail"]

    assert pass_fail["passing_records"] == 9
    assert pass_fail["failing_records"] == 1
    assert pass_fail["pass_rate"] == pytest.approx(90.0)
    assert pass_fail["students_meeting_average_threshold"] == 5
    assert pass_fail["students_below_average_threshold"] == 0


def test_sample_student_performance(sample_report: GradeReport) -> None:
    performance = sample_report["student_performance"]

    assert {
        student_id: result["average"] for student_id, result in performance.items()
    } == {
        "S001": pytest.approx(85.0),
        "S002": pytest.approx(65.0),
        "S003": pytest.approx(92.5),
        "S004": pytest.approx(65.0),
        "S005": pytest.approx(91.5),
    }
    assert performance["S003"]["percentile_rank"] == pytest.approx(100.0)
    assert performance["S005"]["percentile_rank"] == pytest.approx(80.0)
    assert performance["S002"]["percentile_rank"] == pytest.approx(40.0)
    assert performance["S004"]["percentile_rank"] == pytest.approx(40.0)

    assert {
        student_id: result["rank"] for student_id, result in performance.items()
    } == {"S003": 1, "S005": 2, "S001": 3, "S002": 4, "S004": 4}
    assert [item["student_id"] for item in sample_report["top_performers"]] == [
        "S003",
        "S005",
        "S001",
    ]


def test_sample_course_performance(sample_report: GradeReport) -> None:
    courses = sample_report["course_performance"]

    assert courses["CS101"]["average"] == pytest.approx(78.0)
    assert courses["CS101"]["failing_records"] == 1
    assert courses["CS102"]["average"] == pytest.approx(81.6)
    assert courses["CS102"]["failing_records"] == 0


def test_sample_performance_by_major_and_year() -> None:
    report = build_grade_report(
        load_grades_from_csv(SAMPLE_CSV),
        load_students_from_csv(SAMPLE_STUDENTS_CSV),
    )

    assert report["major_performance"] == {
        "Business": {"student_count": 1, "grade_count": 2, "average": 65.0},
        "Computing": {
            "student_count": 2,
            "grade_count": 4,
            "average": pytest.approx(88.75),
        },
        "Engineering": {
            "student_count": 2,
            "grade_count": 4,
            "average": pytest.approx(78.25),
        },
    }
    assert report["year_performance"] == {
        "1": {"student_count": 2, "grade_count": 4, "average": pytest.approx(65.0)},
        "2": {"student_count": 2, "grade_count": 4, "average": pytest.approx(88.25)},
        "3": {"student_count": 1, "grade_count": 2, "average": pytest.approx(92.5)},
    }


def test_sample_report_round_trips_through_json(
    tmp_path: Path,
    sample_report: GradeReport,
) -> None:
    output_path = tmp_path / "grades_report.json"

    write_json_report(sample_report, output_path)

    with output_path.open("r", encoding="utf-8") as report_file:
        loaded_report = json.load(report_file)

    assert loaded_report == round_report_values(sample_report)
    assert loaded_report["semester_trends"][1]["change"] == 7.6
