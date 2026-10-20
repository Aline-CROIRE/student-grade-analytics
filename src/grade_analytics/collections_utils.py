
from collections import Counter, OrderedDict, defaultdict
from typing import DefaultDict

from src.grade_analytics.models import Student


def count_grade_categories(
    categories: list[str],
) -> Counter[str]:
    """Count how many times each grade category occurs."""
    return Counter(categories)


def group_students_by_major(
    students: list[Student],
) -> DefaultDict[str, list[Student]]:
    """Group students by their major."""
    groups: DefaultDict[str, list[Student]] = defaultdict(list)

    for student in students:
        groups[student.major].append(student)

    return groups


def group_students_by_year(
    students: list[Student],
) -> DefaultDict[int, list[Student]]:
    """Group students by their year of study."""
    groups: DefaultDict[int, list[Student]] = defaultdict(list)

    for student in students:
        groups[student.year].append(student)

    return groups


def create_ordered_grade_report(
    distribution: Counter[str],
    grade_order: list[str],
) -> OrderedDict[str, int]:
    """Create a grade report following the requested grade order."""
    return OrderedDict(
        (grade, distribution.get(grade, 0))
        for grade in grade_order
    )
