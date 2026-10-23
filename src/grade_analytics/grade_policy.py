from math import isfinite

PASSING_SCORE = 60.0
GRADE_CATEGORIES = ("A", "B", "C", "D", "F")
GRADE_BOUNDARIES = {
    "A": 90.0,
    "B": 80.0,
    "C": 70.0,
    "D": PASSING_SCORE,
    "F": 0.0,
}


def validate_score(score: float) -> None:
    """Raise ValueError unless score is a finite numeric grade from 0 to 100."""
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise TypeError(f"Score must be an int or float; got {type(score).__name__}")

    try:
        valid = isfinite(score) and 0 <= score <= 100
    except OverflowError:
        valid = False

    if not valid:
        raise ValueError(
            f"Score must be a finite number between 0 and 100; got {score!r}"
        )


def grade_category(score: float) -> str:
    """Return a category using the project's explicit policy assumptions."""
    for category in GRADE_CATEGORIES:
        if score >= GRADE_BOUNDARIES[category]:
            return category
    raise ValueError(f"Score must be between 0 and 100; got {score!r}")
