import json
from collections import Counter
from pathlib import Path
from statistics import fmean
from typing import TypedDict

from src.grade_analytics.analytics import (
    GradeStatistics,
    calculate_grade_modes,
    calculate_grade_statistics,
)
from src.grade_analytics.models import Grade
from src.grade_analytics.semester_trends import (
    SemesterTrend,
    calculate_semester_trends,
)


class StudentPerformance(TypedDict):
    """Describe an individual student's grade summary."""

    average: float
    grade_count: int


class GradeReport(TypedDict):
    """Describe the complete JSON grade report."""

    summary: GradeStatistics
    modes: list[float]
    grade_distribution: dict[str, int]
    student_performance: dict[str, StudentPerformance]
    semester_trends: list[SemesterTrend]


def build_grade_report(grades: list[Grade]) -> GradeReport:
    """Build a comprehensive report from grade records.

    Raises:
        ValueError: If no grade records are provided.
    """
    if not grades:
        raise ValueError("at least one grade is required")

    distribution: Counter[str] = Counter(
        _grade_category(grade.score) for grade in grades
    )

    grade_distribution = {
        category: distribution.get(category, 0)
        for category in ("A", "B", "C", "D", "F")
    }

    scores_by_student: dict[str, list[float]] = {}
    for grade in grades:
        scores_by_student.setdefault(grade.student_id, []).append(grade.score)

    student_performance: dict[str, StudentPerformance] = {
        student_id: {
            "average": fmean(scores),
            "grade_count": len(scores),
        }
        for student_id, scores in sorted(scores_by_student.items())
    }

    return {
        "summary": calculate_grade_statistics(grades),
        "modes": calculate_grade_modes(grades),
        "grade_distribution": grade_distribution,
        "student_performance": student_performance,
        "semester_trends": calculate_semester_trends(grades),
    }


def write_json_report(
    report: GradeReport,
    file_path: str | Path,
) -> None:
    """Write a grade report as readable JSON.

    Parent directories are created when they do not already exist.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2, allow_nan=False)
        report_file.write("\n")


def _grade_category(score: float) -> str:
    """Map a score from 0 to 100 to its grade category."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
