import json

import pytest

from src.grade_analytics.json_report import (
    build_grade_report,
    write_json_report,
)
from src.grade_analytics.models import Grade


@pytest.fixture
def sample_grades() -> list[Grade]:
    """Provide sample grades for JSON report tests."""
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

    semester_trends = report["semester_trends"]

    assert len(semester_trends) == 2
    assert semester_trends[0]["semester"] == "2026-S1"
    assert semester_trends[0]["average"] == pytest.approx(230 / 3)
    assert semester_trends[0]["change"] is None

    assert semester_trends[1]["semester"] == "2026-S2"
    assert semester_trends[1]["average"] == 85.0
    assert semester_trends[1]["change"] == pytest.approx(25 / 3)


def test_build_grade_report_counts_failing_scores() -> None:
    grades = [
        Grade("S004", "CS101", 59.0, "2026-S1"),
    ]

    report = build_grade_report(grades)

    assert report["grade_distribution"] == {
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0,
        "F": 1,
    }


def test_build_grade_report_rejects_empty_grades() -> None:
    with pytest.raises(ValueError, match="at least one grade"):
        build_grade_report([])


def test_write_json_report_creates_valid_json(
    tmp_path, sample_grades: list[Grade]
) -> None:
    output_path = tmp_path / "reports" / "grade_report.json"
    report = build_grade_report(sample_grades)

    write_json_report(report, output_path)

    with output_path.open("r", encoding="utf-8") as report_file:
        loaded_report = json.load(report_file)

    assert loaded_report == report


def test_write_json_report_accepts_string_path(
    tmp_path, sample_grades: list[Grade]
) -> None:
    output_path = tmp_path / "grade_report.json"
    report = build_grade_report(sample_grades)

    write_json_report(report, str(output_path))

    assert output_path.exists()
