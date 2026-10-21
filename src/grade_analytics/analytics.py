from statistics import fmean, median
from typing import TypedDict

from src.grade_analytics.models import Grade


class GradeStatistics(TypedDict):
    """Describe statistics calculated from grade records."""

    count: int
    mean: float
    median: float
    minimum: float
    maximum: float


def calculate_grade_statistics(
    grades: list[Grade],
) -> GradeStatistics:
    """Calculate summary statistics for a collection of grades.

    Raises:
        ValueError: If the collection contains no grades.
    """
    if not grades:
        raise ValueError("at least one grade is required")

    scores = [grade.score for grade in grades]

    return {
        "count": len(scores),
        "mean": fmean(scores),
        "median": median(scores),
        "minimum": min(scores),
        "maximum": max(scores),
    }
