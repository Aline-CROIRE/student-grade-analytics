import json

import pytest

from src.grade_analytics.json_report import (
    PASSING_SCORE,
    build_grade_report,
    round_report_values,
    write_json_report,
)
from src.grade_analytics.models import Grade, Student


@pytest.fixture
def sample_grades() -> list[Grade]:
    """Provide sample grades for report tests."""
    return [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S001", "CS102", 90.0, "2026-S1"),
        Grade("S002", "CS101", 60.0, "2026-S1"),
        Grade("S002", "CS102", 70.0, "2026-S2"),
        Grade("S003", "CS101", 100.0, "2026-S2"),
    ]


def test_build_grade_report(sample_grades: list[Grade]) -> None:
    report = build_grade_report(sample_grades)

    assert report["summary"] == {
        "count": 5,
        "mean": 80.0,
        "median": 80.0,
        "minimum": 60.0,
        "maximum": 100.0,
    }
    assert report["modes"] == []
    assert report["mode_frequency"] == 1
    assert report["grade_distribution"] == {
        "A": 2,
        "B": 1,
        "C": 1,
        "D": 1,
        "F": 0,
    }
    assert report["student_performance"] == {
        "S001": {
            "average": 85.0,
            "grade_count": 2,
            "percentile_rank": pytest.approx(200 / 3),
            "rank": 2,
        },
        "S002": {
            "average": 65.0,
            "grade_count": 2,
            "percentile_rank": pytest.approx(100 / 3),
            "rank": 3,
        },
        "S003": {
            "average": 100.0,
            "grade_count": 1,
            "percentile_rank": 100.0,
            "rank": 1,
        },
    }

    trends = report["semester_trends"]
    assert len(trends) == 2
    assert trends[0]["semester"] == "2026-S1"
    assert trends[0]["average"] == pytest.approx(230 / 3)
    assert trends[0]["change"] is None
    assert trends[1]["semester"] == "2026-S2"
    assert trends[1]["average"] == 85.0
    assert trends[1]["change"] == pytest.approx(25 / 3)


def test_dataset_overview(sample_grades: list[Grade]) -> None:
    overview = build_grade_report(sample_grades)["dataset_overview"]

    assert overview == {
        "grade_records": 5,
        "unique_students": 3,
        "unique_courses": 2,
        "semesters": ["2026-S1", "2026-S2"],
    }


def test_pass_fail_metrics(sample_grades: list[Grade]) -> None:
    result = build_grade_report(sample_grades)["pass_fail"]

    assert result["passing_threshold"] == PASSING_SCORE
    assert result["passing_records"] == 5
    assert result["failing_records"] == 0
    assert result["pass_rate"] == 100.0
    assert result["fail_rate"] == 0.0
    assert result["students_meeting_average_threshold"] == 3
    assert result["students_below_average_threshold"] == 0


def test_pass_fail_metrics_include_failing_records() -> None:
    grades = [
        Grade("S001", "CS101", 59.0, "2026-S1"),
        Grade("S002", "CS101", 60.0, "2026-S1"),
    ]

    result = build_grade_report(grades)["pass_fail"]

    assert result["passing_records"] == 1
    assert result["failing_records"] == 1
    assert result["pass_rate"] == 50.0
    assert result["fail_rate"] == 50.0
    assert result["students_meeting_average_threshold"] == 1
    assert result["students_below_average_threshold"] == 1


def test_course_performance(sample_grades: list[Grade]) -> None:
    courses = build_grade_report(sample_grades)["course_performance"]

    assert courses["CS101"] == {
        "average": 80.0,
        "grade_count": 3,
        "passing_records": 3,
        "failing_records": 0,
        "pass_rate": 100.0,
    }
    assert courses["CS102"] == {
        "average": 80.0,
        "grade_count": 2,
        "passing_records": 2,
        "failing_records": 0,
        "pass_rate": 100.0,
    }


def test_insights_explain_results(sample_grades: list[Grade]) -> None:
    insights = build_grade_report(sample_grades)["insights"]

    assert any("average score is 80.00%" in item for item in insights)
    assert any("100.0%" in item for item in insights)
    assert any("Highest course average" in item for item in insights)
    assert any("in 2026-S2" in item for item in insights)


def test_build_grade_report_counts_failing_scores() -> None:
    grades = [Grade("S004", "CS101", 59.0, "2026-S1")]

    report = build_grade_report(grades)

    assert report["grade_distribution"] == {
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0,
        "F": 1,
    }
    assert report["pass_fail"]["failing_records"] == 1


@pytest.mark.parametrize(
    ("score", "category"),
    [
        (59.99, "F"),
        (60.0, "D"),
        (60.01, "D"),
        (69.99, "D"),
        (70.0, "C"),
        (70.01, "C"),
        (79.99, "C"),
        (80.0, "B"),
        (80.01, "B"),
        (89.99, "B"),
        (90.0, "A"),
        (90.01, "A"),
    ],
)
def test_grade_category_boundaries(score: float, category: str) -> None:
    report = build_grade_report([Grade("S001", "CS101", score, "2026-S1")])

    assert report["grade_distribution"][category] == 1
    assert sum(report["grade_distribution"].values()) == 1


def test_student_percentile_ties_and_boundaries() -> None:
    grades = [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S002", "CS101", 70.0, "2026-S1"),
        Grade("S003", "CS101", 90.0, "2026-S1"),
        Grade("S004", "CS101", 70.0, "2026-S1"),
    ]

    performance = build_grade_report(grades)["student_performance"]

    assert performance["S001"]["percentile_rank"] == 75.0
    assert performance["S002"]["percentile_rank"] == 50.0
    assert performance["S004"]["percentile_rank"] == 50.0
    assert performance["S003"]["percentile_rank"] == 100.0


def test_near_equal_displayed_averages_keep_distinct_percentiles() -> None:
    grades = [
        Grade("S001", "CS101", 0.1, "2026-S1"),
        Grade("S001", "CS102", 0.2, "2026-S1"),
        Grade("S002", "CS101", 0.15, "2026-S1"),
        Grade("S002", "CS102", 0.15, "2026-S1"),
        Grade("S003", "CS101", 0.14, "2026-S1"),
    ]

    performance = build_grade_report(grades)["student_performance"]

    # The displayed averages are both 0.15, but floating-point calculations
    # produce distinct actual averages for S001 and S002.
    assert f"{performance['S001']['average']:.2f}" == "0.15"
    assert f"{performance['S002']['average']:.2f}" == "0.15"

    assert performance["S003"]["percentile_rank"] == pytest.approx(100 / 3)
    assert performance["S002"]["percentile_rank"] == pytest.approx(200 / 3)
    assert performance["S001"]["percentile_rank"] == 100.0


def test_equal_actual_averages_share_percentiles() -> None:
    grades = [
        Grade("S001", "CS101", 0.1, "2026-S1"),
        Grade("S001", "CS102", 0.3, "2026-S1"),
        Grade("S002", "CS101", 0.2, "2026-S1"),
        Grade("S002", "CS102", 0.2, "2026-S1"),
        Grade("S003", "CS101", 0.1, "2026-S1"),
    ]

    performance = build_grade_report(grades)["student_performance"]

    assert performance["S001"]["average"] == performance["S002"]["average"]
    assert performance["S001"]["percentile_rank"] == 100.0
    assert performance["S002"]["percentile_rank"] == 100.0
    assert performance["S003"]["percentile_rank"] == pytest.approx(100 / 3)


def test_percentile_rank_is_serialized_in_json(
    tmp_path,
    sample_grades: list[Grade],
) -> None:
    output_path = tmp_path / "report.json"
    report = build_grade_report(sample_grades)

    write_json_report(report, output_path)

    loaded_report = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded_report["student_performance"]["S001"]["percentile_rank"] == 66.67


def test_build_grade_report_rejects_empty_grades() -> None:
    with pytest.raises(ValueError, match="at least one grade"):
        build_grade_report([])


def test_write_json_report_creates_valid_json(
    tmp_path,
    sample_grades: list[Grade],
) -> None:
    output_path = tmp_path / "reports" / "grade_report.json"
    report = build_grade_report(sample_grades)

    write_json_report(report, output_path)

    with output_path.open("r", encoding="utf-8") as report_file:
        loaded_report = json.load(report_file)

    assert loaded_report == round_report_values(report)


def test_round_report_values_rounds_nested_floats_without_changing_input() -> None:
    report = {
        "average": 230 / 3,
        "trends": [{"change": 7.599999999999994}, {"change": -0.001}],
        "count": 3,
        "label": "S1",
        "missing": None,
    }

    rounded = round_report_values(report)

    assert rounded == {
        "average": 76.67,
        "trends": [{"change": 7.6}, {"change": 0.0}],
        "count": 3,
        "label": "S1",
        "missing": None,
    }
    assert json.dumps(rounded["trends"]) == '[{"change": 7.6}, {"change": 0.0}]'
    assert report["average"] == 230 / 3


def test_write_json_report_accepts_string_path(
    tmp_path,
    sample_grades: list[Grade],
) -> None:
    output_path = tmp_path / "grade_report.json"

    write_json_report(build_grade_report(sample_grades), str(output_path))

    assert output_path.exists()


def test_report_modes_list_repeated_scores_with_their_frequency() -> None:
    grades = [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S002", "CS101", 80.0, "2026-S1"),
        Grade("S003", "CS101", 70.0, "2026-S1"),
        Grade("S004", "CS101", 70.0, "2026-S1"),
        Grade("S005", "CS101", 90.0, "2026-S1"),
    ]

    report = build_grade_report(grades)

    assert report["modes"] == [70.0, 80.0]
    assert report["mode_frequency"] == 2


def test_insights_name_the_top_performer(sample_grades: list[Grade]) -> None:
    insights = build_grade_report(sample_grades)["insights"]

    assert "Top performer: S003 with a 100.00% average." in insights


def test_insights_name_every_student_tied_for_first() -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2026-S1"),
        Grade("S002", "CS101", 90.0, "2026-S1"),
    ]

    insights = build_grade_report(grades)["insights"]

    assert "Top performers: S001, S002 with a 90.00% average." in insights


def test_students_with_equal_averages_share_a_competition_rank() -> None:
    grades = [
        Grade("S001", "CS101", 90.0, "2026-S1"),
        Grade("S002", "CS101", 90.0, "2026-S1"),
        Grade("S003", "CS101", 80.0, "2026-S1"),
    ]

    performance = build_grade_report(grades)["student_performance"]

    assert [performance[s]["rank"] for s in ("S001", "S002", "S003")] == [1, 1, 3]


def test_top_performers_lists_the_three_highest_ranked_students() -> None:
    grades = [
        Grade("S001", "CS101", 70.0, "2026-S1"),
        Grade("S002", "CS101", 95.0, "2026-S1"),
        Grade("S003", "CS101", 85.0, "2026-S1"),
        Grade("S004", "CS101", 90.0, "2026-S1"),
    ]

    assert build_grade_report(grades)["top_performers"] == [
        {"student_id": "S002", "average": 95.0, "rank": 1},
        {"student_id": "S004", "average": 90.0, "rank": 2},
        {"student_id": "S003", "average": 85.0, "rank": 3},
    ]


def test_top_performers_include_students_tied_at_the_cut_off() -> None:
    grades = [
        Grade("S001", "CS101", 95.0, "2026-S1"),
        Grade("S002", "CS101", 90.0, "2026-S1"),
        Grade("S003", "CS101", 80.0, "2026-S1"),
        Grade("S004", "CS101", 80.0, "2026-S1"),
        Grade("S005", "CS101", 70.0, "2026-S1"),
    ]

    top_performers = build_grade_report(grades)["top_performers"]

    assert [(item["student_id"], item["rank"]) for item in top_performers] == [
        ("S001", 1),
        ("S002", 2),
        ("S003", 3),
        ("S004", 3),
    ]


def test_group_sections_are_empty_without_student_profiles(
    sample_grades: list[Grade],
) -> None:
    report = build_grade_report(sample_grades)

    assert report["major_performance"] == {}
    assert report["year_performance"] == {}


def test_report_groups_students_by_major_and_year(
    sample_grades: list[Grade],
) -> None:
    students = [
        Student("S001", "Alice", "Computing", 2),
        Student("S002", "Brian", "Engineering", 2),
        Student("S003", "Chloe", "Computing", 10),
    ]

    report = build_grade_report(sample_grades, students)

    assert report["major_performance"] == {
        "Computing": {"student_count": 2, "grade_count": 3, "average": 90.0},
        "Engineering": {"student_count": 1, "grade_count": 2, "average": 65.0},
    }
    assert report["year_performance"] == {
        "2": {"student_count": 2, "grade_count": 4, "average": 75.0},
        "10": {"student_count": 1, "grade_count": 1, "average": 100.0},
    }
    assert list(report["year_performance"]) == ["2", "10"]


def test_group_sections_only_count_students_with_selected_grades() -> None:
    grades = [Grade("S001", "CS101", 80.0, "2026-S1")]
    students = [
        Student("S001", "Alice", "Computing", 2),
        Student("S002", "Brian", "Engineering", 1),
    ]

    report = build_grade_report(grades, students)

    assert report["major_performance"] == {
        "Computing": {"student_count": 1, "grade_count": 1, "average": 80.0},
    }
    assert report["year_performance"] == {
        "2": {"student_count": 1, "grade_count": 1, "average": 80.0},
    }


def test_grades_without_a_student_profile_are_left_out_of_groups() -> None:
    grades = [
        Grade("S001", "CS101", 80.0, "2026-S1"),
        Grade("S999", "CS101", 40.0, "2026-S1"),
    ]

    report = build_grade_report(grades, [Student("S001", "Alice", "Computing", 2)])

    assert report["major_performance"]["Computing"]["average"] == 80.0
    assert report["summary"]["count"] == 2
