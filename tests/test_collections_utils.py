from collections import Counter

from src.grade_analytics.collections_utils import count_grade_categories


def test_count_grade_categories():
    result = count_grade_categories(["A", "B", "A", "C", "B", "A"])

    assert result == Counter({"A": 3, "B": 2, "C": 1})


def test_count_empty_categories():
    assert count_grade_categories([]) == Counter()