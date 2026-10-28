"""Measure the memory used by different ways of holding grade data.

Run from the project root:

    python -m src.grade_analytics.memory_comparison
"""

import platform
import tracemalloc
from collections import deque, namedtuple
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict

DEFAULT_RECORD_COUNT = 100_000
DEFAULT_WINDOW_SIZE = 5

RecordValues = tuple[str, str, float, str]

GradeTuple = namedtuple(
    "GradeTuple",
    ["student_id", "course_id", "score", "semester"],
)


@dataclass
class GradeRecord:
    """Grade record stored as a regular dataclass."""

    student_id: str
    course_id: str
    score: float
    semester: str


@dataclass(slots=True)
class SlottedGradeRecord:
    """Grade record stored as a dataclass with __slots__."""

    student_id: str
    course_id: str
    score: float
    semester: str


class MemoryResult(TypedDict):
    """Memory measured for one storage approach."""

    approach: str
    total_bytes: int
    bytes_per_item: float


def measure_allocated_bytes(build: Callable[[], object]) -> int:
    """Return the bytes still allocated by the object that build() creates."""
    tracemalloc.start()

    try:
        before, _ = tracemalloc.get_traced_memory()
        data = build()
        after, _ = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    del data
    return after - before


def _sample_values(count: int) -> list[RecordValues]:
    """Create field values shared by every approach, so only containers differ."""
    student_ids = [f"S{number:04d}" for number in range(500)]
    course_ids = [f"CS{number:03d}" for number in range(20)]
    scores = [float(score) for score in range(101)]

    return [
        (
            student_ids[index % len(student_ids)],
            course_ids[index % len(course_ids)],
            scores[index % len(scores)],
            "2026-S1",
        )
        for index in range(count)
    ]


def _result(approach: str, total_bytes: int, item_count: int) -> MemoryResult:
    return {
        "approach": approach,
        "total_bytes": total_bytes,
        "bytes_per_item": total_bytes / item_count,
    }


def compare_record_memory(
    count: int = DEFAULT_RECORD_COUNT,
) -> list[MemoryResult]:
    """Compare memory for a list of grade records stored five different ways.

    Results are sorted from the smallest to the largest total.
    """
    values = _sample_values(count)

    approaches: dict[str, Callable[[], object]] = {
        "dict": lambda: [
            {"student_id": s, "course_id": c, "score": g, "semester": t}
            for s, c, g, t in values
        ],
        "tuple": lambda: [(s, c, g, t) for s, c, g, t in values],
        "namedtuple": lambda: [GradeTuple(s, c, g, t) for s, c, g, t in values],
        "dataclass": lambda: [GradeRecord(s, c, g, t) for s, c, g, t in values],
        "dataclass(slots=True)": lambda: [
            SlottedGradeRecord(s, c, g, t) for s, c, g, t in values
        ],
    }

    results = [
        _result(name, measure_allocated_bytes(build), count)
        for name, build in approaches.items()
    ]
    return sorted(results, key=lambda result: result["total_bytes"])


def compare_rolling_window_memory(
    count: int = DEFAULT_RECORD_COUNT,
    window_size: int = DEFAULT_WINDOW_SIZE,
) -> list[MemoryResult]:
    """Compare keeping every score in a list with a bounded deque window.

    Both containers receive the same scores; a rolling average only needs the
    most recent window_size of them. bytes_per_item is per score received.
    """
    scores = [float(index % 101) for index in range(count)]

    results = [
        _result(
            "list (keeps every score)",
            measure_allocated_bytes(lambda: list(scores)),
            count,
        ),
        _result(
            f"deque(maxlen={window_size})",
            measure_allocated_bytes(lambda: deque(scores, maxlen=window_size)),
            count,
        ),
    ]
    return sorted(results, key=lambda result: result["total_bytes"])


def format_results(title: str, results: list[MemoryResult]) -> str:
    """Format measured results as a plain-text table."""
    lines = [
        title,
        f"{'Approach':<28}{'Total (KiB)':>14}{'Bytes per item':>18}",
    ]

    for result in results:
        lines.append(
            f"{result['approach']:<28}"
            f"{result['total_bytes'] / 1024:>14,.1f}"
            f"{result['bytes_per_item']:>18.2f}"
        )

    return "\n".join(lines)


def main() -> None:
    """Print both memory comparisons."""
    print(
        f"Python {platform.python_version()} on {platform.system()}; "
        f"{DEFAULT_RECORD_COUNT:,} items measured with tracemalloc.\n"
    )
    print(format_results("Storing grade records", compare_record_memory()))
    print()
    print(
        format_results(
            "Keeping scores for a rolling average",
            compare_rolling_window_memory(),
        )
    )


if __name__ == "__main__":
    main()
