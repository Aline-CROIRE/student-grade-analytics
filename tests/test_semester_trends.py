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
            "rolling_average": 70.0,
        },
        {
            "semester": "2026-S2",
            "average": 90.0,
            "change": 20.0,
            "rolling_average": 80.0,
        },
        {
            "semester": "2027-S1",
            "average": 75.0,
            "change": -15.0,
            "rolling_average": 82.5,
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


def test_semester_ordering_across_years_and_available_values() -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2027-S2"),
        Grade("S001", "CS101", 70.0, "2025-S2"),
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S001", "CS101", 75.0, "2027-S1"),
    ]

    trends = calculate_semester_trends(grades)

    assert [trend["semester"] for trend in trends] == [
        "2025-S2",
        "2026-S1",
        "2027-S1",
        "2027-S2",
    ]


@pytest.mark.parametrize("semester", ["2026", "26-S1", "2026-S3", "2026-S10", "x-S1"])
def test_semester_trends_reject_malformed_labels(semester: str) -> None:
    with pytest.raises(ValueError, match="expected format YYYY-S1 or YYYY-S2"):
        calculate_semester_trends([Grade("S001", "CS101", 80.0, semester)])


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
            "rolling_average": 80.0,
        }
    ]


@pytest.mark.parametrize(
    ("window_size", "expected"),
    [
        (1, [70.0, 90.0, 75.0]),
        (2, [70.0, 80.0, 82.5]),
        (3, [70.0, 80.0, pytest.approx(235 / 3)]),
        (10, [70.0, 80.0, pytest.approx(235 / 3)]),
    ],
)
def test_rolling_average_respects_window_size(
    sample_grades: list[Grade],
    window_size: int,
    expected: list[float],
) -> None:
    trends = calculate_semester_trends(sample_grades, window_size=window_size)

    assert [trend["rolling_average"] for trend in trends] == expected


@pytest.mark.parametrize("window_size", [0, -1])
def test_semester_trends_reject_invalid_window_size(
    sample_grades: list[Grade],
    window_size: int,
) -> None:
    with pytest.raises(ValueError, match="Window size"):
        calculate_semester_trends(sample_grades, window_size=window_size)
