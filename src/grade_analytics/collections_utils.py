from collections import Counter, OrderedDict, defaultdict, deque, namedtuple
from typing import TypedDict

from src.grade_analytics.models import Student

GradeSummary = namedtuple(
    "GradeSummary",
    ["student_id", "average_score", "grade_count"],
)


class GradeReport(TypedDict):
    """Define the structure of a grade report."""

    student_id: str
    average_score: float
    grade_count: int


def count_grade_categories(
    categories: list[str],
) -> Counter[str]:
    """Count how many times each grade category occurs."""
    return Counter(categories)


def group_students_by_major(
    students: list[Student],
) -> defaultdict[str, list[Student]]:
    """Group students by their major."""
    groups: defaultdict[str, list[Student]] = defaultdict(list)

    for student in students:
        groups[student.major].append(student)

    return groups


def group_students_by_year(
    students: list[Student],
) -> defaultdict[int, list[Student]]:
    """Group students by their year of study."""
    groups: defaultdict[int, list[Student]] = defaultdict(list)

    for student in students:
        groups[student.year].append(student)

    return groups


def create_ordered_grade_report(
    distribution: Counter[str],
    grade_order: list[str],
) -> OrderedDict[str, int]:
    """Create a grade report following the requested grade order."""
    return OrderedDict((grade, distribution.get(grade, 0)) for grade in grade_order)


class RollingAverage:
    """Calculate averages over the most recent scores."""

    def __init__(self, window_size: int) -> None:
        if window_size <= 0:
            raise ValueError("Window size must be greater than zero.")

        self._scores: deque[float] = deque(maxlen=window_size)

    def add_score(self, score: float) -> float:
        """Add a score and return the current rolling average."""
        self._scores.append(score)
        return sum(self._scores) / len(self._scores)

    def current_average(self) -> float | None:
        """Return the current average, or None if there are no scores."""
        if not self._scores:
            return None

        return sum(self._scores) / len(self._scores)


def create_grade_summary(
    student_id: str,
    scores: list[float],
) -> GradeSummary:
    """Create a compact summary using a namedtuple."""
    average = sum(scores) / len(scores) if scores else 0.0

    return GradeSummary(
        student_id=student_id,
        average_score=average,
        grade_count=len(scores),
    )


def create_grade_report(
    student_id: str,
    scores: list[float],
) -> GradeReport:
    """Create a dictionary report with a defined structure."""
    average = sum(scores) / len(scores) if scores else 0.0

    return {
        "student_id": student_id,
        "average_score": average,
        "grade_count": len(scores),
    }
