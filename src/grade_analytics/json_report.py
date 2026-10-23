import json
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean, median
from typing import TypedDict

from src.grade_analytics.analytics import GradeStatistics
from src.grade_analytics.collections_utils import create_ordered_grade_report
from src.grade_analytics.grade_policy import (
    GRADE_CATEGORIES,
    PASSING_SCORE,
    grade_category,
)
from src.grade_analytics.models import Grade
from src.grade_analytics.semester import semester_sort_key
from src.grade_analytics.semester_trends import SemesterTrend


@dataclass
class _GroupAccumulator:
    total: float = 0.0
    count: int = 0
    passing_records: int = 0

    def add(self, score: float) -> None:
        self.total += score
        self.count += 1
        self.passing_records += score >= PASSING_SCORE

    @property
    def average(self) -> float:
        return self.total / self.count


class StudentPerformance(TypedDict):
    """Summarize an individual student's recorded grades."""

    average: float
    grade_count: int
    percentile_rank: float


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

    scores: list[float] = []
    frequencies: Counter[float] = Counter()
    distribution_counts: Counter[str] = Counter()

    scores_by_student: defaultdict[str, _GroupAccumulator] = defaultdict(
        _GroupAccumulator
    )
    scores_by_course: defaultdict[str, _GroupAccumulator] = defaultdict(
        _GroupAccumulator
    )
    scores_by_semester: defaultdict[str, _GroupAccumulator] = defaultdict(
        _GroupAccumulator
    )

    passing_records = 0

    for grade in grades:
        scores.append(grade.score)
        frequencies[grade.score] += 1
        distribution_counts[grade_category(grade.score)] += 1
        scores_by_student[grade.student_id].add(grade.score)
        scores_by_course[grade.course_id].add(grade.score)
        scores_by_semester[grade.semester].add(grade.score)
        passing_records += grade.score >= PASSING_SCORE

    summary: GradeStatistics = {
        "count": len(scores),
        "mean": fmean(scores),
        "median": median(scores),
        "minimum": min(scores),
        "maximum": max(scores),
    }

    highest_frequency = max(frequencies.values())
    modes = sorted(
        score
        for score, frequency in frequencies.items()
        if frequency == highest_frequency
    )

    grade_distribution = create_ordered_grade_report(
        distribution_counts,
        list(GRADE_CATEGORIES),
    )

    # Use actual calculated averages. Rounding before percentile calculation
    # can incorrectly turn distinct averages into ties.
    student_averages = sorted(
        accumulator.average for accumulator in scores_by_student.values()
    )

    student_performance: dict[str, StudentPerformance] = {
        student_id: {
            "average": accumulator.average,
            "grade_count": accumulator.count,
            "percentile_rank": (
                bisect_right(
                    student_averages,
                    accumulator.average,
                )
                / len(student_averages)
                * 100
            ),
        }
        for student_id, accumulator in sorted(scores_by_student.items())
    }

    failing_records = len(grades) - passing_records
    total_records = len(grades)
    pass_rate = passing_records / total_records * 100

    students_meeting_threshold = sum(
        student["average"] >= PASSING_SCORE for student in student_performance.values()
    )

    course_performance: dict[str, CoursePerformance] = {}

    for course_id, accumulator in sorted(scores_by_course.items()):
        course_performance[course_id] = {
            "average": accumulator.average,
            "grade_count": accumulator.count,
            "passing_records": accumulator.passing_records,
            "failing_records": accumulator.count - accumulator.passing_records,
            "pass_rate": accumulator.passing_records / accumulator.count * 100,
        }

    semester_trends: list[SemesterTrend] = []
    previous_average: float | None = None

    for semester in sorted(scores_by_semester, key=semester_sort_key):
        average = scores_by_semester[semester].average

        semester_trends.append(
            {
                "semester": semester,
                "average": average,
                "change": (
                    None if previous_average is None else average - previous_average
                ),
            }
        )

        previous_average = average

    semesters = [trend["semester"] for trend in semester_trends]

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
    """Backward-compatible private wrapper around the shared grade policy."""
    return grade_category(score)
