from pathlib import Path

from src.grade_analytics.json_report import GradeReport

WIDTH = 76


def print_header(title: str, subtitle: str = "") -> None:
    """Print a simple, centered application heading."""
    print()
    print(title.center(WIDTH))
    if subtitle:
        print(subtitle.center(WIDTH))
    print()


def print_workspace_menu(source_name: str, period_label: str) -> None:
    """Display actions for the current file and analysis period."""
    print_header("ANALYSIS WORKSPACE", f"{source_name} | {period_label}")
    print("Choose an action:")
    print("  1. Export this analysis to JSON and TXT")
    print("  2. Analyze another period in this file")
    print("  3. Choose another CSV file")
    print("  4. Exit")
    print()


def format_report_text(report: GradeReport, period_label: str) -> str:
    """Format the analytics report with results and explanations."""
    summary = report["summary"]
    overview = report["dataset_overview"]
    pass_fail = report["pass_fail"]
    distribution = report["grade_distribution"]
    courses = report["course_performance"]
    total = summary["count"]

    lines = [
        "",
        "STUDENT GRADE ANALYTICS REPORT".center(WIDTH),
        period_label.center(WIDTH),
        "",
        "1. DATASET OVERVIEW",
        f"{'Source period':<34}{period_label:>42}",
        f"{'Grade records analyzed':<34}{overview['grade_records']:>42}",
        f"{'Unique students':<34}{overview['unique_students']:>42}",
        f"{'Unique courses':<34}{overview['unique_courses']:>42}",
        f"{'Semesters represented':<34}{len(overview['semesters']):>42}",
        f"{'Semester list':<34}{', '.join(overview['semesters']):>42}",
        "",
        "2. OVERALL PERFORMANCE",
        f"{'Average score (mean)':<34}{summary['mean']:>38.2f}%",
        f"{'Median score':<34}{summary['median']:>38.2f}%",
        f"{'Highest score':<34}{summary['maximum']:>38.2f}%",
        f"{'Lowest score':<34}{summary['minimum']:>38.2f}%",
        "",
        "3. PASS AND FAIL ANALYSIS",
        f"{'Passing threshold':<34}{pass_fail['passing_threshold']:>38.2f}%",
        (
            f"{'Passing grade records':<34}"
            f"{pass_fail['passing_records']:>27}"
            f" ({pass_fail['pass_rate']:.1f}%)"
        ),
        (
            f"{'Failing grade records':<34}"
            f"{pass_fail['failing_records']:>27}"
            f" ({pass_fail['fail_rate']:.1f}%)"
        ),
        (
            f"{'Students averaging at least threshold':<34}"
            f"{pass_fail['students_meeting_average_threshold']:>42}"
        ),
        (
            f"{'Students averaging below threshold':<34}"
            f"{pass_fail['students_below_average_threshold']:>42}"
        ),
        "",
        "Interpretation: record pass rates count individual grades. Student",
        "average results count each student's average across their available",
        "records. These measures are related but are not interchangeable.",
        "",
        "4. GRADE DISTRIBUTION",
        f"{'Grade':<10}{'Count':>10}{'Percentage':>16}  Distribution",
    ]

    for category, count in distribution.items():
        percentage = count / total * 100
        bar_length = round(percentage / 100 * 24)
        bar = "#" * bar_length
        lines.append(f"{category:<10}{count:>10}{percentage:>15.2f}%  {bar}")

    largest_count = max(distribution.values())
    most_common = [
        category for category, count in distribution.items() if count == largest_count
    ]

    lines.extend(
        [
            "",
            (
                f"Most common category: {', '.join(most_common)} "
                f"({largest_count} record(s))."
            ),
            "",
            "5. STUDENT RANKINGS",
            (
                f"{'Rank':<8}{'Student ID':<20}{'Average':>12}"
                f"{'Percentile':>14}{'Grades':>10}"
            ),
        ]
    )

    ranked_students = sorted(
        report["student_performance"].items(),
        key=lambda item: (-item[1]["average"], item[0]),
    )

    previous_average: float | None = None
    previous_rank = 0

    for position, (student_id, performance) in enumerate(
        ranked_students,
        start=1,
    ):
        average = performance["average"]
        rank = previous_rank if previous_average == average else position

        lines.append(
            f"{rank:<8}{student_id:<20}{average:>11.2f}%"
            f"{performance['percentile_rank']:>13.2f}%"
            f"{performance['grade_count']:>10}"
        )

        previous_average = average
        previous_rank = rank

    lines.extend(
        [
            "",
            "Note: students with equal actual averages share a competition rank.",
            "Percentiles are the percentage of student averages less than or equal",
            "to each student's actual average; equal averages share percentile rank.",
            "",
            "6. COURSE PERFORMANCE",
            (
                f"{'Course ID':<18}{'Average':>12}{'Records':>12}"
                f"{'Pass rate':>14}{'Failing':>12}"
            ),
        ]
    )

    ranked_courses = sorted(
        courses.items(),
        key=lambda item: (-item[1]["average"], item[0]),
    )

    for course_id, course_result in ranked_courses:
        lines.append(
            f"{course_id:<18}"
            f"{course_result['average']:>11.2f}%"
            f"{course_result['grade_count']:>12}"
            f"{course_result['pass_rate']:>13.1f}%"
            f"{course_result['failing_records']:>12}"
        )

    lines.extend(["", "7. SEMESTER TRENDS"])

    if report["semester_trends"]:
        lines.append(f"{'Semester':<18}{'Average':>14}{'Change':>16}{'Direction':>18}")

        for trend in report["semester_trends"]:
            change = trend["change"]

            if change is None:
                change_text = "N/A"
                direction = "Baseline"
            elif change > 0:
                change_text = f"{change:+.2f} pp"
                direction = "Improved"
            elif change < 0:
                change_text = f"{change:+.2f} pp"
                direction = "Declined"
            else:
                change_text = "0.00 pp"
                direction = "Unchanged"

            lines.append(
                f"{trend['semester']:<18}"
                f"{trend['average']:>13.2f}%"
                f"{change_text:>16}"
                f"{direction:>18}"
            )

        if len(report["semester_trends"]) == 1:
            lines.append(
                "Only one semester is represented; a trend comparison "
                "is not available."
            )
        else:
            lines.append(
                "Change is measured in percentage points against the "
                "previous recorded semester."
            )
    else:
        lines.append("No semester trend data is available.")

    lines.extend(["", "8. MOST FREQUENT SCORES"])

    modes = report["modes"]

    if len(modes) == total:
        lines.append(
            "Every score occurs once; all scores tie for the highest frequency."
        )
    else:
        lines.append(
            "Most frequent score(s): " + ", ".join(f"{score:g}" for score in modes)
        )

    lines.extend(["", "9. KEY FINDINGS"])
    lines.extend(f"- {insight}" for insight in report["insights"])

    lines.extend(
        [
            "",
            "10. DATA AND INTERPRETATION LIMITATIONS",
            "- Results describe only the records in the selected CSV and period.",
            "- Missing records or unequal course loads may affect comparisons.",
            "- Course IDs are shown because course names are not provided.",
            "- Association and change do not establish the cause of performance.",
            (
                f"- Passing is defined here as a score of at least "
                f"{pass_fail['passing_threshold']:.0f}%; confirm this matches "
                "your institution's policy."
            ),
            "",
        ]
    )

    return "\n".join(lines) + "\n"


def print_dashboard(report: GradeReport, period_label: str) -> None:
    """Display the complete analytics dashboard."""
    print(format_report_text(report, period_label))


def write_text_report(
    report: GradeReport,
    period_label: str,
    file_path: str | Path,
) -> None:
    """Save a readable report, creating parent directories if needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        format_report_text(report, period_label),
        encoding="utf-8",
    )
