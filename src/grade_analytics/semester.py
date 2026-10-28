"""Validate semester labels and sort them chronologically."""


def semester_sort_key(semester: str) -> tuple[int, int]:
    """Validate and return the chronological key for a YYYY-S1/S2 label."""
    parts = semester.split("-")
    if (
        len(parts) != 2
        or len(parts[0]) != 4
        or not parts[0].isascii()
        or not parts[0].isdigit()
        or int(parts[0]) == 0
        or parts[1] not in {"S1", "S2"}
    ):
        raise ValueError(
            f"Invalid semester {semester!r}; expected format YYYY-S1 or YYYY-S2"
        )

    return int(parts[0]), int(parts[1][1])
