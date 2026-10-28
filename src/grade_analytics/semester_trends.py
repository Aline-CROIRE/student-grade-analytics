from collections import defaultdict
from typing import TypedDict

from src.grade_analytics.collections_utils import RollingAverage
from src.grade_analytics.models import Grade
from src.grade_analytics.semester import semester_sort_key

DEFAULT_TREND_WINDOW = 2


class SemesterTrend(TypedDict):
    """Represent a semester's average score, change, and rolling average."""

    semester: str
    average: float
    change: float | None
    rolling_average: float


def calculate_semester_trends(
    grades: list[Grade],
    window_size: int = DEFAULT_TREND_WINDOW,
) -> list[SemesterTrend]:
    """Calculate semester averages, changes, and rolling averages.

    Semester averages are fed in chronological order into a deque-based
    RollingAverage, so each semester's rolling average is the mean of the
    most recent ``window_size`` semester averages. The default window of two
    semesters covers one academic year.

    Semesters are expected to use the YYYY-S1 or YYYY-S2 format.
    An empty grade list returns an empty list.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    rolling_average = RollingAverage(window_size)
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
                "rolling_average": rolling_average.add_score(average),
            }
        )

        previous_average = average

    return trends
