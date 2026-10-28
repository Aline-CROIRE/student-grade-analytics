import json
from pathlib import Path

import pytest

from src.grade_analytics.csv_loader import load_grades_from_csv
from src.grade_analytics.json_report import (
    GradeReport,
    build_grade_report,
    write_json_report,
)

SAMPLE_CSV = Path(__file__).resolve().parent.parent / "data" / "grades.csv"


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

    top_student = max(performance, key=lambda student: performance[student]["average"])
    assert top_student == "S003"


def test_sample_course_performance(sample_report: GradeReport) -> None:
    courses = sample_report["course_performance"]

    assert courses["CS101"]["average"] == pytest.approx(78.0)
    assert courses["CS101"]["failing_records"] == 1
    assert courses["CS102"]["average"] == pytest.approx(81.6)
    assert courses["CS102"]["failing_records"] == 0


def test_sample_report_round_trips_through_json(
    tmp_path: Path,
    sample_report: GradeReport,
) -> None:
    output_path = tmp_path / "grades_report.json"

    write_json_report(sample_report, output_path)

    with output_path.open("r", encoding="utf-8") as report_file:
        assert json.load(report_file) == sample_report
