from src.grade_analytics.json_report import build_grade_report
from src.grade_analytics.models import Grade
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
