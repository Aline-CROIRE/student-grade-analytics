"""Summary statistics, modes, and percentile ranks for grade records."""

from collections import Counter
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


def calculate_grade_modes(grades: list[Grade]) -> list[float]:
    """Return all scores that occur most frequently.

    Raises:
        ValueError: If the collection contains no grades.
    """
    if not grades:
        raise ValueError("at least one grade is required")

    frequencies = Counter(grade.score for grade in grades)
    highest_frequency = max(frequencies.values())

    return sorted(
        score
        for score, frequency in frequencies.items()
        if frequency == highest_frequency
    )


def calculate_percentile_rank(
    score: float,
    grades: list[Grade],
) -> float:
    """Return the percentage of recorded scores less than or equal to score.

    A score below every recorded score has rank 0.0.
    A score at or above every recorded score has rank 100.0.

    Raises:
        ValueError: If the collection contains no grades.
    """
    if not grades:
        raise ValueError("at least one grade is required")

    scores_at_or_below = sum(grade.score <= score for grade in grades)

    return scores_at_or_below / len(grades) * 100
