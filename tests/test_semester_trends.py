import pytest

from src.grade_analytics.models import Grade
from src.grade_analytics.semester_trends import calculate_semester_trends


@pytest.fixture
def sample_grades() -> list[Grade]:
    """Provide grades across three semesters."""
    return [
        Grade("S001", "CS101", 60.0, "2026-S1"),
        Grade("S001", "CS102", 80.0, "2026-S1"),
        Grade("S001", "CS101", 80.0, "2026-S2"),
        Grade("S001", "CS102", 100.0, "2026-S2"),
        Grade("S001", "CS101", 70.0, "2027-S1"),
        Grade("S001", "CS102", 80.0, "2027-S1"),
    ]


def test_calculate_semester_averages(
    sample_grades: list[Grade],
) -> None:
    trends = calculate_semester_trends(sample_grades)

    assert trends == [
        {
            "semester": "2026-S1",
            "average": 70.0,
            "change": None,
        },
        {
            "semester": "2026-S2",
            "average": 90.0,
            "change": 20.0,
        },
        {
            "semester": "2027-S1",
            "average": 75.0,
            "change": -15.0,
        },
    ]


def test_semesters_are_sorted_chronologically() -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2027-S1"),
        Grade("S001", "CS101", 70.0, "2026-S1"),
        Grade("S001", "CS101", 80.0, "2026-S2"),
    ]

    trends = calculate_semester_trends(grades)

    assert [item["semester"] for item in trends] == [
        "2026-S1",
        "2026-S2",
        "2027-S1",
    ]


def test_empty_grades_return_empty_trends() -> None:
    assert calculate_semester_trends([]) == []


def test_single_semester_has_no_change() -> None:
    grades = [
        Grade("S001", "CS101", 75.0, "2026-S1"),
        Grade("S001", "CS102", 85.0, "2026-S1"),
    ]

    trends = calculate_semester_trends(grades)

    assert trends == [
        {
            "semester": "2026-S1",
            "average": 80.0,
            "change": None,
        }
    ]
