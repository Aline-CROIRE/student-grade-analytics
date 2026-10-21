from statistics import fmean
from typing import TypedDict

from src.grade_analytics.models import Grade


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
    scores_by_semester: dict[str, list[float]] = {}

    for grade in grades:
        scores_by_semester.setdefault(grade.semester, []).append(grade.score)

    trends: list[SemesterTrend] = []
    previous_average: float | None = None

    for semester in sorted(scores_by_semester):
        average = fmean(scores_by_semester[semester])
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
