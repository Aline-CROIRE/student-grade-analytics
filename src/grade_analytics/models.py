from dataclasses import dataclass, field

from src.grade_analytics.grade_policy import validate_score
from src.grade_analytics.semester import semester_sort_key


@dataclass
class Course:
    """Represent a university course."""

    course_id: str
    name: str
    credits: int


@dataclass
class Grade:
    """Represent a student's result in a course."""

    student_id: str
    course_id: str
    score: float
    semester: str

    def __post_init__(self) -> None:
        validate_score(self.score)
        semester_sort_key(self.semester)


@dataclass
class Student:
    """Represent a student and their course grades."""

    student_id: str
    name: str
    major: str
    year: int
    grades: list[Grade] = field(default_factory=list)
