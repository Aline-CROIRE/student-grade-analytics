from src.grade_analytics.memory_comparison import (
    compare_record_memory,
    compare_rolling_window_memory,
    format_results,
    main,
    measure_allocated_bytes,
)

SMALL_COUNT = 2_000


def test_measure_allocated_bytes_counts_retained_objects() -> None:
    small = measure_allocated_bytes(lambda: [0.5] * 10)
    large = measure_allocated_bytes(lambda: [0.5] * 10_000)

    assert 0 < small < large


def test_record_memory_covers_every_approach_smallest_first() -> None:
    results = compare_record_memory(SMALL_COUNT)
    totals = {result["approach"]: result["total_bytes"] for result in results}

    assert set(totals) == {
        "dict",
        "tuple",
        "namedtuple",
        "dataclass",
        "dataclass(slots=True)",
    }
    assert all(total > 0 for total in totals.values())
    assert [result["total_bytes"] for result in results] == sorted(totals.values())
    assert totals["dataclass(slots=True)"] < totals["dataclass"]
    assert totals["namedtuple"] < totals["dict"]


def test_bounded_deque_uses_less_memory_than_full_list() -> None:
    results = compare_rolling_window_memory(SMALL_COUNT, window_size=5)
    totals = {result["approach"]: result["total_bytes"] for result in results}

    assert totals["deque(maxlen=5)"] < totals["list (keeps every score)"]


def test_format_results_shows_each_approach() -> None:
    text = format_results("Storing grade records", compare_record_memory(SMALL_COUNT))

    assert text.splitlines()[0] == "Storing grade records"
    assert "Bytes per item" in text
    assert "dataclass(slots=True)" in text


def test_main_prints_both_comparisons(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "src.grade_analytics.memory_comparison.DEFAULT_RECORD_COUNT",
        SMALL_COUNT,
    )

    main()

    output = capsys.readouterr().out
    assert "Storing grade records" in output
    assert "Keeping scores for a rolling average" in output
