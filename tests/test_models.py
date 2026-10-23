import pytest

from src.grade_analytics.models import Course, Grade, Student


def test_course_creation():
    course = Course("CS101", "Python", 3)

    assert course.course_id == "CS101"
    assert course.name == "Python"
    assert course.credits == 3


def test_grade_creation():
    grade = Grade("S001", "CS101", 85.5, "2026-S1")

    assert grade.student_id == "S001"
    assert grade.course_id == "CS101"
    assert grade.score == 85.5


@pytest.mark.parametrize(
    "score",
    [-0.1, 100.1, float("nan"), float("inf"), 10**1000],
)
def test_grade_rejects_invalid_score(score):
    with pytest.raises(ValueError, match="finite number between 0 and 100"):
        Grade("S001", "CS101", score, "2026-S1")


@pytest.mark.parametrize("score", [True, "80"])
def test_grade_rejects_non_numeric_score_type(score):
    with pytest.raises(TypeError, match="Score must be an int or float"):
        Grade("S001", "CS101", score, "2026-S1")


def test_grade_rejects_invalid_semester():
    with pytest.raises(ValueError, match="expected format YYYY-S1 or YYYY-S2"):
        Grade("S001", "CS101", 85.5, "2026-S3")


def test_student_has_independent_grades_list():
    first = Student("S001", "Alice", "Computing", 3)
    second = Student("S002", "Bob", "Engineering", 2)

    first.grades.append(Grade("S001", "CS101", 85.5, "2026-S1"))

    assert len(first.grades) == 1
    assert second.grades == []
