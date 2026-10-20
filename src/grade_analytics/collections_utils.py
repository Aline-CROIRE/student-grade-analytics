from collections import Counter


def count_grade_categories(
    categories: list[str],
) -> Counter[str]:
    """Count how many times each grade category occurs."""
    return Counter(categories)