from src.grade_analytics.models import Course, Grade, Student


def test_course_creation():
    course = Course("CS101", "Python", 3)

    assert course.course_id == "CS101"
    assert course.name == "Python"
    assert course.credits == 3


def test_grade_creation():
    grade = Grade("S001", "CS101", 85.5, "Semester 1")

    assert grade.student_id == "S001"
    assert grade.course_id == "CS101"
    assert grade.score == 85.5


def test_student_has_independent_grades_list():
    first = Student("S001", "Alice", "Computing", 3)
    second = Student("S002", "Bob", "Engineering", 2)

    first.grades.append(Grade("S001", "CS101", 85.5, "Semester 1"))

    assert len(first.grades) == 1
    assert second.grades == []
