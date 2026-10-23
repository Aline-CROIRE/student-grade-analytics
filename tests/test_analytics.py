import pytest

from src.grade_analytics.analytics import (
    calculate_grade_modes,
    calculate_grade_statistics,
    calculate_percentile_rank,
)
from src.grade_analytics.models import Grade


@pytest.fixture
def sample_grades() -> list[Grade]:
    """Provide sample grades for analytics tests."""
    return [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S002", "CS101", 60.0, "2026-S1"),
        Grade("S003", "CS101", 100.0, "2026-S1"),
        Grade("S004", "CS101", 70.0, "2026-S1"),
        Grade("S005", "CS101", 90.0, "2026-S1"),
    ]


def test_calculate_grade_statistics(sample_grades: list[Grade]) -> None:
    statistics = calculate_grade_statistics(sample_grades)

    assert statistics == {
        "count": 5,
        "mean": 80.0,
        "median": 80.0,
        "minimum": 60.0,
        "maximum": 100.0,
    }


def test_statistics_for_one_grade() -> None:
    grades = [Grade("S001", "CS101", 75.0, "2026-S1")]

    statistics = calculate_grade_statistics(grades)

    assert statistics == {
        "count": 1,
        "mean": 75.0,
        "median": 75.0,
        "minimum": 75.0,
        "maximum": 75.0,
    }


def test_statistics_for_even_number_of_grades() -> None:
    grades = [
        Grade("S001", "CS101", 60.0, "2026-S1"),
        Grade("S002", "CS101", 80.0, "2026-S1"),
    ]

    statistics = calculate_grade_statistics(grades)

    assert statistics["mean"] == 70.0
    assert statistics["median"] == 70.0


def test_reject_empty_grades() -> None:
    with pytest.raises(ValueError, match="at least one grade"):
        calculate_grade_statistics([])


def test_calculate_grade_mode() -> None:
    grades = [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S002", "CS101", 80.0, "2026-S1"),
        Grade("S003", "CS101", 90.0, "2026-S1"),
    ]

    assert calculate_grade_modes(grades) == [80.0]


def test_calculate_multiple_grade_modes() -> None:
    grades = [
        Grade("S001", "CS101", 70.0, "2026-S1"),
        Grade("S002", "CS101", 80.0, "2026-S1"),
        Grade("S003", "CS101", 70.0, "2026-S1"),
        Grade("S004", "CS101", 80.0, "2026-S1"),
    ]

    assert calculate_grade_modes(grades) == [70.0, 80.0]


def test_grade_modes_reject_empty_grades() -> None:
    with pytest.raises(ValueError, match="at least one grade"):
        calculate_grade_modes([])


def test_calculate_percentile_rank() -> None:
    grades = [
        Grade("S001", "CS101", 60.0, "2026-S1"),
        Grade("S002", "CS101", 70.0, "2026-S1"),
        Grade("S003", "CS101", 80.0, "2026-S1"),
        Grade("S004", "CS101", 80.0, "2026-S1"),
        Grade("S005", "CS101", 100.0, "2026-S1"),
    ]

    assert calculate_percentile_rank(80.0, grades) == 80.0


def test_percentile_rank_at_boundaries() -> None:
    grades = [
        Grade("S001", "CS101", 60.0, "2026-S1"),
        Grade("S002", "CS101", 80.0, "2026-S1"),
        Grade("S003", "CS101", 100.0, "2026-S1"),
    ]

    assert calculate_percentile_rank(50.0, grades) == 0.0
    assert calculate_percentile_rank(100.0, grades) == 100.0


def test_percentile_rank_rejects_empty_grades() -> None:
    with pytest.raises(ValueError, match="at least one grade"):
        calculate_percentile_rank(80.0, [])
