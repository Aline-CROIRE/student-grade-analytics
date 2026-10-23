from collections import defaultdict
from typing import TypedDict

from src.grade_analytics.models import Grade
from src.grade_analytics.semester import semester_sort_key


class SemesterTrend(TypedDict):
    """Represent a semester's average score and change."""

    semester: str
    average: float
    change: float | None


def calculate_semester_trends(
    grades: list[Grade],
) -> list[SemesterTrend]:
    """Calculate semester averages and changes from the previous semester.

    Semesters are expected to use the YYYY-S1 or YYYY-S2 format.
    An empty grade list returns an empty list.
    """
    totals_by_semester: defaultdict[str, tuple[float, int]] = defaultdict(
        lambda: (0.0, 0)
    )

    for grade in grades:
        semester_sort_key(grade.semester)
        total, count = totals_by_semester[grade.semester]
        totals_by_semester[grade.semester] = (total + grade.score, count + 1)

    trends: list[SemesterTrend] = []
    previous_average: float | None = None

    for semester in sorted(totals_by_semester, key=semester_sort_key):
        total, count = totals_by_semester[semester]
        average = total / count
        change = None if previous_average is None else average - previous_average

        trends.append(
            {
                "semester": semester,
                "average": average,
                "change": change,
            }
        )

        previous_average = average

    return trends
