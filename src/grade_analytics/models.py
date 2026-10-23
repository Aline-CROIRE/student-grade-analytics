from dataclasses import dataclass, field


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


@dataclass
class Student:
    """Represent a student and their course grades."""

    student_id: str
    name: str
    major: str
    year: int
    grades: list[Grade] = field(default_factory=list)
