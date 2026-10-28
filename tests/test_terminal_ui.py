from src.grade_analytics.json_report import build_grade_report
from src.grade_analytics.models import Grade, Student
from src.grade_analytics.terminal_ui import format_report_text


def test_report_includes_all_analysis_sections() -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2026-S1"),
        Grade("S001", "CS102", 50.0, "2026-S1"),
        Grade("S002", "CS101", 80.0, "2026-S2"),
    ]

    text = format_report_text(
        build_grade_report(grades),
        "Entire dataset",
    )

    for section in (
        "DATASET OVERVIEW",
        "OVERALL PERFORMANCE",
        "PASS AND FAIL ANALYSIS",
        "GRADE DISTRIBUTION",
        "STUDENT RANKINGS",
        "COURSE PERFORMANCE",
        "SEMESTER TRENDS",
        "MOST FREQUENT SCORES",
        "KEY FINDINGS",
        "DATA AND INTERPRETATION LIMITATIONS",
    ):
        assert section in text

    assert "Passing threshold" in text
    assert "CS101" in text
    assert "percentage points" in text


def test_report_explains_single_semester_limitation() -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2026-S1"),
    ]

    text = format_report_text(
        build_grade_report(grades),
        "Semester 2026-S1",
    )

    assert "Only one semester is represented" in text
    assert "Baseline" in text


def test_near_equal_displayed_averages_receive_distinct_ranks() -> None:
    grades = [
        Grade("S001", "CS101", 0.1, "2026-S1"),
        Grade("S001", "CS102", 0.2, "2026-S1"),
        Grade("S002", "CS101", 0.15, "2026-S1"),
        Grade("S002", "CS102", 0.15, "2026-S1"),
        Grade("S003", "CS101", 0.14, "2026-S1"),
    ]

    text = format_report_text(build_grade_report(grades), "Entire dataset")
    ranking_lines = [
        line
        for line in text.splitlines()
        if any(student_id in line for student_id in ("S001", "S002", "S003"))
    ]

    s001_line = next(line for line in ranking_lines if "S001" in line)
    s002_line = next(line for line in ranking_lines if "S002" in line)
    s003_line = next(line for line in ranking_lines if "S003" in line)

    assert s001_line.startswith("1")
    assert s002_line.startswith("2")
    assert s003_line.startswith("3")

    assert f"{0.1 + 0.2:.2f}" == "0.30"


def test_equal_actual_averages_share_competition_rank() -> None:
    grades = [
        Grade("S001", "CS101", 0.1, "2026-S1"),
        Grade("S001", "CS102", 0.3, "2026-S1"),
        Grade("S002", "CS101", 0.2, "2026-S1"),
        Grade("S002", "CS102", 0.2, "2026-S1"),
        Grade("S003", "CS101", 0.1, "2026-S1"),
    ]

    text = format_report_text(build_grade_report(grades), "Entire dataset")
    ranking_lines = [
        line
        for line in text.splitlines()
        if any(student_id in line for student_id in ("S001", "S002", "S003"))
    ]

    s001_line = next(line for line in ranking_lines if "S001" in line)
    s002_line = next(line for line in ranking_lines if "S002" in line)
    s003_line = next(line for line in ranking_lines if "S003" in line)

    assert s001_line.startswith("1")
    assert s002_line.startswith("1")
    assert s003_line.startswith("3")

    assert "actual averages share a competition rank" in text


def test_report_can_be_saved_as_readable_text(tmp_path) -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2026-S1"),
    ]
    report = build_grade_report(grades)
    output_path = tmp_path / "reports" / "report.txt"

    from src.grade_analytics.terminal_ui import write_text_report

    write_text_report(report, "Entire dataset", output_path)

    saved_text = output_path.read_text(encoding="utf-8")
    assert "STUDENT GRADE ANALYTICS REPORT" in saved_text
    assert "KEY FINDINGS" in saved_text


def test_semester_trends_show_rolling_average() -> None:
    grades = [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S002", "CS101", 70.0, "2026-S1"),
        Grade("S001", "CS102", 90.0, "2026-S2"),
        Grade("S002", "CS102", 100.0, "2026-S2"),
    ]

    text = format_report_text(build_grade_report(grades), "Entire dataset")
    lines = text.splitlines()

    header = next(line for line in lines if line.startswith("Semester  "))
    s1_line = next(line for line in lines if line.startswith("2026-S1"))
    s2_line = next(line for line in lines if line.startswith("2026-S2"))

    assert "Rolling avg" in header
    assert s1_line.split()[1:3] == ["75.00%", "75.00%"]
    assert s2_line.split()[1:3] == ["95.00%", "85.00%"]
    assert "mean of the most recent 2 semester averages" in text
    assert all(len(line) <= 76 for line in (header, s1_line, s2_line))


def test_dashboard_shows_performance_by_major_and_year() -> None:
    grades = [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S002", "CS101", 70.0, "2026-S1"),
        Grade("S002", "CS102", 90.0, "2026-S2"),
    ]
    students = [
        Student("S001", "Alice", "Computing", 2),
        Student("S002", "Brian", "Engineering", 1),
    ]

    text = format_report_text(build_grade_report(grades, students), "Entire dataset")
    section = text.split("7. PERFORMANCE BY MAJOR AND YEAR")[1].split("8. ")[0]
    rows = section.splitlines()

    computing = next(row for row in rows if row.startswith("Computing"))
    engineering = next(row for row in rows if row.startswith("Engineering"))
    year_1 = next(row for row in rows if row.startswith("Year 1"))

    assert computing.split()[1:] == ["1", "1", "80.00%"]
    assert engineering.split()[1:] == ["1", "2", "80.00%"]
    assert year_1.split()[2:] == ["1", "2", "80.00%"]
    assert all(len(row) <= 76 for row in rows)


def test_dashboard_explains_missing_student_profiles() -> None:
    text = format_report_text(
        build_grade_report([Grade("S001", "CS101", 80.0, "2026-S1")]),
        "Entire dataset",
    )

    assert "No student profiles were provided" in text
