import json

import pytest

from src.grade_analytics.json_report import (
    PASSING_SCORE,
    build_grade_report,
    write_json_report,
)
from src.grade_analytics.models import Grade


@pytest.fixture
def sample_grades() -> list[Grade]:
    """Provide sample grades for report tests."""
    return [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S001", "CS102", 90.0, "2026-S1"),
        Grade("S002", "CS101", 60.0, "2026-S1"),
        Grade("S002", "CS102", 70.0, "2026-S2"),
        Grade("S003", "CS101", 100.0, "2026-S2"),
    ]


def test_build_grade_report(sample_grades: list[Grade]) -> None:
    report = build_grade_report(sample_grades)

    assert report["summary"] == {
        "count": 5,
        "mean": 80.0,
        "median": 80.0,
        "minimum": 60.0,
        "maximum": 100.0,
    }
    assert report["modes"] == [60.0, 70.0, 80.0, 90.0, 100.0]
    assert report["grade_distribution"] == {
        "A": 2,
        "B": 1,
        "C": 1,
        "D": 1,
        "F": 0,
    }
    assert report["student_performance"] == {
        "S001": {"average": 85.0, "grade_count": 2},
        "S002": {"average": 65.0, "grade_count": 2},
        "S003": {"average": 100.0, "grade_count": 1},
    }

    trends = report["semester_trends"]
    assert len(trends) == 2
    assert trends[0]["semester"] == "2026-S1"
    assert trends[0]["average"] == pytest.approx(230 / 3)
    assert trends[0]["change"] is None
    assert trends[1]["semester"] == "2026-S2"
    assert trends[1]["average"] == 85.0
    assert trends[1]["change"] == pytest.approx(25 / 3)


def test_dataset_overview(sample_grades: list[Grade]) -> None:
    overview = build_grade_report(sample_grades)["dataset_overview"]

    assert overview == {
        "grade_records": 5,
        "unique_students": 3,
        "unique_courses": 2,
        "semesters": ["2026-S1", "2026-S2"],
    }


def test_pass_fail_metrics(sample_grades: list[Grade]) -> None:
    result = build_grade_report(sample_grades)["pass_fail"]

    assert result["passing_threshold"] == PASSING_SCORE
    assert result["passing_records"] == 5
    assert result["failing_records"] == 0
    assert result["pass_rate"] == 100.0
    assert result["fail_rate"] == 0.0
    assert result["students_meeting_average_threshold"] == 3
    assert result["students_below_average_threshold"] == 0


def test_pass_fail_metrics_include_failing_records() -> None:
    grades = [
        Grade("S001", "CS101", 59.0, "2026-S1"),
        Grade("S002", "CS101", 60.0, "2026-S1"),
    ]

    result = build_grade_report(grades)["pass_fail"]

    assert result["passing_records"] == 1
    assert result["failing_records"] == 1
    assert result["pass_rate"] == 50.0
    assert result["fail_rate"] == 50.0
    assert result["students_meeting_average_threshold"] == 1
    assert result["students_below_average_threshold"] == 1


def test_course_performance(sample_grades: list[Grade]) -> None:
    courses = build_grade_report(sample_grades)["course_performance"]

    assert courses["CS101"] == {
        "average": 80.0,
        "grade_count": 3,
        "passing_records": 3,
        "failing_records": 0,
        "pass_rate": 100.0,
    }
    assert courses["CS102"] == {
        "average": 80.0,
        "grade_count": 2,
        "passing_records": 2,
        "failing_records": 0,
        "pass_rate": 100.0,
    }


def test_insights_explain_results(sample_grades: list[Grade]) -> None:
    insights = build_grade_report(sample_grades)["insights"]

    assert any("average score is 80.00%" in item for item in insights)
    assert any("100.0%" in item for item in insights)
    assert any("Highest course average" in item for item in insights)
    assert any("in 2026-S2" in item for item in insights)


def test_build_grade_report_counts_failing_scores() -> None:
    grades = [Grade("S004", "CS101", 59.0, "2026-S1")]

    report = build_grade_report(grades)

    assert report["grade_distribution"] == {
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0,
        "F": 1,
    }
    assert report["pass_fail"]["failing_records"] == 1


def test_build_grade_report_rejects_empty_grades() -> None:
    with pytest.raises(ValueError, match="at least one grade"):
        build_grade_report([])


def test_write_json_report_creates_valid_json(
    tmp_path,
    sample_grades: list[Grade],
) -> None:
    output_path = tmp_path / "reports" / "grade_report.json"
    report = build_grade_report(sample_grades)

    write_json_report(report, output_path)

    with output_path.open("r", encoding="utf-8") as report_file:
        loaded_report = json.load(report_file)

    assert loaded_report == report


def test_write_json_report_accepts_string_path(
    tmp_path,
    sample_grades: list[Grade],
) -> None:
    output_path = tmp_path / "grade_report.json"

    write_json_report(build_grade_report(sample_grades), str(output_path))

    assert output_path.exists()
