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

PASSING_SCORE = 60.0
GRADE_CATEGORIES = ("A", "B", "C", "D", "F")


class StudentPerformance(TypedDict):
    """Summarize an individual student's recorded grades."""

    average: float
    grade_count: int


class DatasetOverview(TypedDict):
    """Describe the scope of the selected grade records."""

    grade_records: int
    unique_students: int
    unique_courses: int
    semesters: list[str]


class PassFailSummary(TypedDict):
    """Summarize passing and failing records and student averages."""

    passing_threshold: float
    passing_records: int
    failing_records: int
    pass_rate: float
    fail_rate: float
    students_meeting_average_threshold: int
    students_below_average_threshold: int


class CoursePerformance(TypedDict):
    """Summarize results for one course."""

    average: float
    grade_count: int
    passing_records: int
    failing_records: int
    pass_rate: float


class GradeReport(TypedDict):
    """Describe the complete grade analytics report."""

    summary: GradeStatistics
    modes: list[float]
    grade_distribution: dict[str, int]
    student_performance: dict[str, StudentPerformance]
    semester_trends: list[SemesterTrend]
    dataset_overview: DatasetOverview
    pass_fail: PassFailSummary
    course_performance: dict[str, CoursePerformance]
    insights: list[str]


def build_grade_report(grades: list[Grade]) -> GradeReport:
    """Build a comprehensive report from grade records.

    Scores of 60 or higher count as passing by default.

    Raises:
        ValueError: If no grade records are provided.
    """
    if not grades:
        raise ValueError("at least one grade is required")

    summary = calculate_grade_statistics(grades)
    modes = calculate_grade_modes(grades)
    semester_trends = calculate_semester_trends(grades)

    distribution_counts: Counter[str] = Counter(
        _grade_category(grade.score) for grade in grades
    )
    grade_distribution = {
        category: distribution_counts.get(category, 0) for category in GRADE_CATEGORIES
    }

    scores_by_student: dict[str, list[float]] = {}
    scores_by_course: dict[str, list[float]] = {}

    for grade in grades:
        scores_by_student.setdefault(grade.student_id, []).append(grade.score)
        scores_by_course.setdefault(grade.course_id, []).append(grade.score)

    student_performance: dict[str, StudentPerformance] = {
        student_id: {
            "average": fmean(scores),
            "grade_count": len(scores),
        }
        for student_id, scores in sorted(scores_by_student.items())
    }

    passing_records = sum(grade.score >= PASSING_SCORE for grade in grades)
    failing_records = len(grades) - passing_records
    total_records = len(grades)
    pass_rate = passing_records / total_records * 100

    students_meeting_threshold = sum(
        student["average"] >= PASSING_SCORE for student in student_performance.values()
    )

    course_performance: dict[str, CoursePerformance] = {}

    for course_id, scores in sorted(scores_by_course.items()):
        course_passing = sum(score >= PASSING_SCORE for score in scores)
        course_failing = len(scores) - course_passing

        course_performance[course_id] = {
            "average": fmean(scores),
            "grade_count": len(scores),
            "passing_records": course_passing,
            "failing_records": course_failing,
            "pass_rate": course_passing / len(scores) * 100,
        }

    semesters = sorted({grade.semester for grade in grades})

    dataset_overview: DatasetOverview = {
        "grade_records": total_records,
        "unique_students": len(student_performance),
        "unique_courses": len(course_performance),
        "semesters": semesters,
    }

    pass_fail: PassFailSummary = {
        "passing_threshold": PASSING_SCORE,
        "passing_records": passing_records,
        "failing_records": failing_records,
        "pass_rate": pass_rate,
        "fail_rate": failing_records / total_records * 100,
        "students_meeting_average_threshold": students_meeting_threshold,
        "students_below_average_threshold": (
            len(student_performance) - students_meeting_threshold
        ),
    }

    report: GradeReport = {
        "summary": summary,
        "modes": modes,
        "grade_distribution": grade_distribution,
        "student_performance": student_performance,
        "semester_trends": semester_trends,
        "dataset_overview": dataset_overview,
        "pass_fail": pass_fail,
        "course_performance": course_performance,
        "insights": [],
    }
    report["insights"] = _build_insights(report)

    return report


def _build_insights(report: GradeReport) -> list[str]:
    """Explain the most important findings in a report."""
    summary = report["summary"]
    pass_fail = report["pass_fail"]
    distribution = report["grade_distribution"]
    courses = report["course_performance"]
    trends = report["semester_trends"]

    total = summary["count"]
    insights = [
        (
            f"The average score is {summary['mean']:.2f}%, "
            f"{'above' if summary['mean'] >= PASSING_SCORE else 'below'} "
            f"the {PASSING_SCORE:.0f}% passing threshold."
        ),
        (
            f"{pass_fail['passing_records']} of {total} grade records "
            f"pass ({pass_fail['pass_rate']:.1f}%); "
            f"{pass_fail['failing_records']} fail "
            f"({pass_fail['fail_rate']:.1f}%)."
        ),
        (
            f"{pass_fail['students_meeting_average_threshold']} of "
            f"{report['dataset_overview']['unique_students']} students "
            f"have an average at or above {PASSING_SCORE:.0f}%."
        ),
    ]

    largest_count = max(distribution.values())
    most_common_categories = [
        category for category, count in distribution.items() if count == largest_count
    ]
    insights.append(
        f"The most common grade category is "
        f"{', '.join(most_common_categories)} "
        f"({largest_count} record(s))."
    )

    if courses:
        highest_average = max(course["average"] for course in courses.values())
        lowest_average = min(course["average"] for course in courses.values())

        highest_courses = [
            course_id
            for course_id, course in courses.items()
            if course["average"] == highest_average
        ]
        lowest_courses = [
            course_id
            for course_id, course in courses.items()
            if course["average"] == lowest_average
        ]

        insights.append(
            f"Highest course average: {', '.join(highest_courses)} "
            f"({highest_average:.2f}%)."
        )

        if len(courses) > 1:
            insights.append(
                f"Lowest course average: {', '.join(lowest_courses)} "
                f"({lowest_average:.2f}%)."
            )

    if len(trends) >= 2:
        latest = trends[-1]
        change = latest["change"]

        if change is not None:
            if change > 0:
                direction = "increased"
            elif change < 0:
                direction = "decreased"
            else:
                direction = "stayed unchanged"

            insights.append(
                f"The average {direction} by {abs(change):.2f} "
                f"percentage points in {latest['semester']} "
                "compared with the previous recorded semester."
            )
    else:
        insights.append(
            "Trend comparison is unavailable because fewer than "
            "two semesters are represented in this analysis."
        )

    return insights


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
    if score >= PASSING_SCORE:
        return "D"
    return "F"
