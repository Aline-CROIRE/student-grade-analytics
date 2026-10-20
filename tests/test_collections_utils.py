
from collections import Counter, OrderedDict

from src.grade_analytics.collections_utils import (
    count_grade_categories,
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
