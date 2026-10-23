from collections import Counter, OrderedDict

import pytest

from src.grade_analytics.collections_utils import (
    RollingAverage,
    count_grade_categories,
    create_grade_report,
    create_grade_summary,
    create_ordered_grade_report,
    group_students_by_major,
    group_students_by_year,
)
from src.grade_analytics.models import Student


def test_count_grade_categories():
    result = count_grade_categories(["A", "B", "A", "C", "B", "A"])

    assert result == Counter({"A": 3, "B": 2, "C": 1})


def test_count_empty_categories():
    assert count_grade_categories([]) == Counter()


def test_group_students_by_major():
    alice = Student("S001", "Alice", "Computing", 3)
    bob = Student("S002", "Bob", "Engineering", 2)
    david = Student("S003", "David", "Computing", 4)

    groups = group_students_by_major([alice, bob, david])

    assert groups["Computing"] == [alice, david]
    assert groups["Engineering"] == [bob]


def test_group_students_by_year():
    alice = Student("S001", "Alice", "Computing", 3)
    bob = Student("S002", "Bob", "Engineering", 2)
    david = Student("S003", "David", "Computing", 3)

    groups = group_students_by_year([alice, bob, david])

    assert groups[3] == [alice, david]
    assert groups[2] == [bob]


def test_create_ordered_grade_report():
    distribution = Counter({"B": 2, "A": 3, "C": 1})

    report = create_ordered_grade_report(
        distribution,
        ["A", "B", "C", "D", "F"],
    )

    assert isinstance(report, OrderedDict)
    assert list(report.keys()) == ["A", "B", "C", "D", "F"]
    assert list(report.values()) == [3, 2, 1, 0, 0]


def test_rolling_average_uses_recent_scores():
    rolling = RollingAverage(window_size=3)

    assert rolling.add_score(70) == 70
    assert rolling.add_score(80) == 75
    assert rolling.add_score(90) == 80
    assert rolling.add_score(100) == 90


def test_rolling_average_empty():
    rolling = RollingAverage(window_size=3)

    assert rolling.current_average() is None


def test_rolling_average_current_average_with_scores():
    rolling = RollingAverage(window_size=3)
    rolling.add_score(70)
    rolling.add_score(80)
    rolling.add_score(90)

    assert rolling.current_average() == 80


@pytest.mark.parametrize("window_size", [0, -1, 1.5, True])
def test_rolling_average_rejects_invalid_window_size(window_size):
    with pytest.raises(ValueError, match="greater than zero"):
        RollingAverage(window_size=window_size)


@pytest.mark.parametrize("score", [-1, 101, float("nan"), float("inf")])
def test_rolling_average_rejects_invalid_score(score):
    rolling = RollingAverage(window_size=2)
    rolling.add_score(70)

    with pytest.raises(ValueError, match="finite number between 0 and 100"):
        rolling.add_score(score)

    assert rolling.current_average() == 70


def test_rolling_average_rejects_non_numeric_score_type():
    rolling = RollingAverage(window_size=2)

    with pytest.raises(TypeError, match="Score must be an int or float"):
        rolling.add_score(True)


def test_rolling_average_repeated_evictions_remain_correct():
    rolling = RollingAverage(window_size=2)

    assert rolling.add_score(10) == 10
    assert rolling.add_score(20) == 15
    assert rolling.add_score(30) == 25
    assert rolling.add_score(40) == 35


def test_create_grade_summary():
    summary = create_grade_summary("S001", [70, 80, 90])

    assert summary.student_id == "S001"
    assert summary.average_score == 80
    assert summary.grade_count == 3


def test_create_grade_report():
    report = create_grade_report("S001", [70, 80, 90])

    assert report == {
        "student_id": "S001",
        "average_score": 80,
        "grade_count": 3,
    }


def test_empty_grade_summary():
    summary = create_grade_summary("S001", [])

    assert summary.average_score == 0.0
    assert summary.grade_count == 0
