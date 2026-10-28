import json
from bisect import bisect_right
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, TypeVar

from src.grade_analytics.analytics import (
    GradeStatistics,
    calculate_grade_modes,
    calculate_grade_statistics,
)
from src.grade_analytics.collections_utils import (
    create_ordered_grade_report,
    group_students_by_major,
    group_students_by_year,
)
from src.grade_analytics.grade_policy import (
    GRADE_CATEGORIES,
    PASSING_SCORE,
    grade_category,
)
from src.grade_analytics.models import Grade, Student
from src.grade_analytics.semester_trends import (
    SemesterTrend,
    calculate_semester_trends,
)


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


TOP_PERFORMER_LIMIT = 3


class StudentPerformance(TypedDict):
    """Summarize an individual student's recorded grades."""

    average: float
    grade_count: int
    percentile_rank: float
    rank: int


class TopPerformer(TypedDict):
    """Identify one of the highest-ranked students."""

    student_id: str
    average: float
    rank: int


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


class GroupPerformance(TypedDict):
    """Summarize the grades of a group of students, such as a major or year."""

    student_count: int
    grade_count: int
    average: float


class GradeReport(TypedDict):
    """Describe the complete grade analytics report."""

    summary: GradeStatistics
    modes: list[float]
    mode_frequency: int
    grade_distribution: dict[str, int]
    student_performance: dict[str, StudentPerformance]
    top_performers: list[TopPerformer]
    semester_trends: list[SemesterTrend]
    dataset_overview: DatasetOverview
    pass_fail: PassFailSummary
    course_performance: dict[str, CoursePerformance]
    major_performance: dict[str, GroupPerformance]
    year_performance: dict[str, GroupPerformance]
    insights: list[str]


GroupKey = TypeVar("GroupKey", str, int)


def _competition_ranks(
    scores_by_student: Mapping[str, _GroupAccumulator],
) -> dict[str, int]:
    """Rank students by actual average, highest first.

    Students with equal averages share a competition rank, so three students
    with averages 90, 90 and 80 are ranked 1, 1 and 3. Ties are listed by
    student ID. The returned dictionary is in rank order.
    """
    ranked_students = sorted(
        scores_by_student.items(),
        key=lambda item: (-item[1].average, item[0]),
    )

    ranks: dict[str, int] = {}
    previous_average: float | None = None
    previous_rank = 0

    for position, (student_id, accumulator) in enumerate(ranked_students, start=1):
        rank = previous_rank if accumulator.average == previous_average else position
        ranks[student_id] = rank
        previous_average = accumulator.average
        previous_rank = rank

    return ranks


def _summarize_student_groups(
    groups: Mapping[GroupKey, list[Student]],
    scores_by_student: Mapping[str, _GroupAccumulator],
) -> dict[str, GroupPerformance]:
    """Combine per-student scores into one summary per student group.

    Only students with grades in the analysed records are counted, and groups
    without any such students are left out. The average is taken over all of
    the group's grade records.
    """
    performance: dict[str, GroupPerformance] = {}

    for key in sorted(groups):
        members = [
            scores_by_student[student.student_id]
            for student in groups[key]
            if student.student_id in scores_by_student
        ]

        if not members:
            continue

        grade_count = sum(member.count for member in members)
        performance[str(key)] = {
            "student_count": len(members),
            "grade_count": grade_count,
            "average": sum(member.total for member in members) / grade_count,
        }

    return performance


def build_grade_report(
    grades: list[Grade],
    students: list[Student] | None = None,
) -> GradeReport:
    """Build a comprehensive report from grade records.

    Scores of 60 or higher count as passing by default. When student profiles
    are provided, the report also summarizes performance by major and by year
    of study; otherwise those sections are empty.

    Raises:
        ValueError: If no grade records are provided.
    """
    if not grades:
        raise ValueError("at least one grade is required")

    distribution_counts: Counter[str] = Counter()

    scores_by_student: defaultdict[str, _GroupAccumulator] = defaultdict(
        _GroupAccumulator
    )
    scores_by_course: defaultdict[str, _GroupAccumulator] = defaultdict(
        _GroupAccumulator
    )

    passing_records = 0

    for grade in grades:
        distribution_counts[grade_category(grade.score)] += 1
        scores_by_student[grade.student_id].add(grade.score)
        scores_by_course[grade.course_id].add(grade.score)
        passing_records += grade.score >= PASSING_SCORE

    summary: GradeStatistics = calculate_grade_statistics(grades)
    modes = calculate_grade_modes(grades)
    mode_frequency = sum(grade.score == modes[0] for grade in grades)

    # When no score repeats, every score would tie as a mode; report none.
    if mode_frequency == 1:
        modes = []

    grade_distribution = create_ordered_grade_report(
        distribution_counts,
        list(GRADE_CATEGORIES),
    )

    # Use actual calculated averages. Rounding before percentile calculation
    # can incorrectly turn distinct averages into ties.
    student_averages = sorted(
        accumulator.average for accumulator in scores_by_student.values()
    )
    ranks = _competition_ranks(scores_by_student)

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
            "rank": ranks[student_id],
        }
        for student_id, accumulator in sorted(scores_by_student.items())
    }

    top_performers: list[TopPerformer] = [
        {
            "student_id": student_id,
            "average": scores_by_student[student_id].average,
            "rank": rank,
        }
        for student_id, rank in ranks.items()
        if rank <= TOP_PERFORMER_LIMIT
    ]

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

    profiles = students or []
    major_performance = _summarize_student_groups(
        group_students_by_major(profiles),
        scores_by_student,
    )
    year_performance = _summarize_student_groups(
        group_students_by_year(profiles),
        scores_by_student,
    )

    semester_trends = calculate_semester_trends(grades)
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
        "mode_frequency": mode_frequency,
        "grade_distribution": grade_distribution,
        "student_performance": student_performance,
        "top_performers": top_performers,
        "semester_trends": semester_trends,
        "dataset_overview": dataset_overview,
        "pass_fail": pass_fail,
        "course_performance": course_performance,
        "major_performance": major_performance,
        "year_performance": year_performance,
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

    leaders = [item for item in report["top_performers"] if item["rank"] == 1]
    label = "Top performer" if len(leaders) == 1 else "Top performers"
    insights.append(
        f"{label}: {', '.join(item['student_id'] for item in leaders)} "
        f"with a {leaders[0]['average']:.2f}% average."
    )

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
