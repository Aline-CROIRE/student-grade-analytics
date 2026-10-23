# Student Grade Analytics Tool

A Python-based command-line application for analyzing student grades, generating statistical reports, comparing academic performance across semesters, and exporting results to JSON and text files.

The project demonstrates Python's advanced collection types, data classes, type hints, file handling, error handling, testing, and clean-code practices.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Input Data Format](#input-data-format)
- [Analytics and Reports](#analytics-and-reports)
- [Advanced Collections](#advanced-collections)
- [Data Models and Type Safety](#data-models-and-type-safety)
- [File Handling and Error Handling](#file-handling-and-error-handling)
- [Testing and Code Quality](#testing-and-code-quality)
- [Performance and Complexity](#performance-and-complexity)
- [Sample Results](#sample-results)
- [Screenshot](#screenshot)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)

## Overview

The Student Grade Analytics Tool loads grade records from a CSV file and calculates useful statistics about academic performance. Users can analyze the entire dataset or select a supported academic year or semester, view results in a terminal dashboard, and export reports.

The application separates its data models, analytics functions, collection utilities, reporting logic, and terminal interface into modules to improve readability, maintainability, and testability.

## Features

- Load student grade records from CSV files.
- Calculate the mean, median, minimum, maximum, and other descriptive statistics.
- Calculate grade distributions and identify the most frequent grades.
- Calculate student averages, rankings, and percentile ranks.
- Compare academic performance across semesters and identify changes in average scores.
- Summarize pass and fail results.
- Use an interactive terminal dashboard to review analytics.
- Export reports as JSON and text files.
- Select a CSV file using the native file picker.
- Handle invalid input and file-related errors.
- Test the application using automated tests.
- Check code formatting, linting, type correctness, and test coverage.

## Technologies

- **Python 3.11+** — application logic and data processing.
- **CSV and JSON** — input data and report export.
- **`collections`** — `Counter`, `defaultdict`, `OrderedDict`, and `deque`.
- **`dataclasses` and `namedtuple`** — structured data representation.
- **`TypedDict` and type hints** — clearer data contracts and static type checking.
- **pytest** — automated testing.
- **Black** — code formatting.
- **Ruff** — linting and code-quality checks.
- **mypy** — static type checking.
- **coverage.py** — test coverage measurement.
- **Git and GitHub** — version control and project hosting.

## Project Structure

```text
student-grade-analytics/
├── data/
│   └── grades.csv
├── docs/
│   └── images/
│       └── StudentGradeAnalytics.png
├── src/
│   └── grade_analytics/
│       ├── __init__.py
│       ├── analytics.py
│       ├── collections_utils.py
│       ├── json_report.py
│       ├── models.py
│       ├── semester_trends.py
│       └── terminal_ui.py
├── tests/
│   ├── test_analytics.py
│   ├── test_collections_utils.py
│   ├── test_json_report.py
│   ├── test_models.py
│   ├── test_semester_trends.py
│   └── ...
├── main.py
├── requirements.txt
└── README.md
```

The tree above illustrates the intended organization. The exact files inside `tests/` and the documentation directory may differ as the project evolves.

### Main components

| File | Responsibility |
|---|---|
| `main.py` | Starts the application and manages the interactive workflow. |
| `models.py` | Defines structured data models for students, courses, and grades. |
| `analytics.py` | Calculates grade statistics, modes, and percentile ranks. |
| `collections_utils.py` | Provides utilities demonstrating advanced collections and grouping operations. |
| `semester_trends.py` | Calculates and compares semester-level performance. |
| `json_report.py` | Builds structured analytics reports and exports JSON. |
| `terminal_ui.py` | Displays the dashboard and generates text reports. |
| `tests/` | Contains automated tests for application behavior. |
| `data/grades.csv` | Provides sample grade records. |

## Requirements

- Python 3.11 or newer.
- pip.
- Git, if you want to clone the repository.
- A terminal such as PowerShell on Windows.
- The Python dependencies listed in `requirements.txt`.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Aline-CROIRE/student-grade-analytics.git
cd student-grade-analytics
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, consult your system's execution-policy settings or activate the environment using an alternative supported by your setup.

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you intend to run all development checks, make sure pytest, Black, Ruff, mypy, and coverage.py are installed. They may be declared in `requirements.txt` or managed separately as development dependencies.

## Running the Application

From the project root, activate the virtual environment and run:

```powershell
python main.py
```

Follow the interactive prompts to select the input CSV file and choose an analysis period.

Depending on the available dataset and selected period, the application can display analytics, export reports, analyze another period, select another CSV file, or exit.

### Exporting reports

Use the application's workspace menu to select the appropriate export option.

- **JSON export:** produces a structured report suitable for other programs to consume.
- **Text export:** produces a readable report for viewing or sharing.

The exact export location and filename depend on the application's current implementation and selected options.

## Input Data Format

The sample dataset is stored in `data/grades.csv`.

Each row represents a grade record associated with a student, course, score, and academic period. The file uses a header row.

Example:

```csv
student_id,course_id,score,semester
S001,C101,85,S1
S002,C101,65,S1
S003,C101,90,S1
S001,C102,85,S2
S002,C102,65,S2
```

This is an illustrative example of the expected data shape. Use the actual column names and accepted values defined by the CSV-loading implementation when preparing additional files.

### Data considerations

- Scores should be valid numeric values within the range supported by the application.
- Student and course identifiers should be consistent across records.
- Academic-period values should follow the format expected by the application.
- Missing, malformed, or invalid records should be handled according to the application's validation and error-handling rules.

The current sample dataset contains 10 grade records. It identifies students and courses by IDs; it does not provide student names, course names, or course credits.

## Analytics and Reports

The application provides several views of academic performance.

### Descriptive statistics

Grade statistics include:

- Mean (average).
- Median.
- Minimum score.
- Maximum score.
- Grade distribution.
- Most frequent grade categories.

### Student performance

The report can calculate student averages, rank students, and compare performance using percentile ranks.

A student's average is calculated from the available grade records for that student in the selected analysis.

### Semester trends

Semester trend analysis summarizes average scores by semester and compares each semester with the preceding recorded semester.

Changes in average scores are expressed in **percentage points**, not as relative percentage growth.

### Pass and fail analysis

The project's configured passing threshold is 60.

Grade categories use the following project-defined boundaries:

| Category | Score range |
|---|---:|
| A | 90–100 |
| B | 80–less than 90 |
| C | 70–less than 80 |
| D | 60–less than 70 |
| F | 0–less than 60 |

These boundaries are assumptions for this project, not universal academic standards.

Record-level pass rates count individual grade records. Student pass counts evaluate each student's average across the available records in the selected analysis. These are different measurements and should not be interpreted as interchangeable.

### Rankings and percentiles

Student rankings use calculated averages rather than values rounded for display. Students with equal actual averages share a competition rank; for example, ranks may be `1, 1, 3`.

Displayed averages are formatted to two decimal places.

Percentile calculations follow the implementation's less-than-or-equal convention: the percentile represents the percentage of compared values less than or equal to the value being evaluated.

## Advanced Collections

The project demonstrates Python's advanced collection types and their appropriate use cases.

### `Counter`

`Counter` counts occurrences of items in an iterable.

In this project, it is useful for summarizing grade categories and identifying frequently occurring values.

```python
from collections import Counter

grades = ["A", "B", "A", "C", "B", "A"]
distribution = Counter(grades)

print(distribution)
# Counter({'A': 3, 'B': 2, 'C': 1})
```

### `defaultdict`

`defaultdict` automatically creates a default value when a missing key is accessed.

It is useful for grouping records by student, course, or academic period without manually initializing each group.

```python
from collections import defaultdict

grades_by_student = defaultdict(list)

grades_by_student["S001"].append(85)
grades_by_student["S001"].append(90)

print(grades_by_student["S001"])
# [85, 90]
```

### `OrderedDict`

`OrderedDict` maintains insertion order and offers additional order-specific operations beyond a regular dictionary.

It can be used when a report needs an explicitly ordered mapping of results.

Modern Python dictionaries also preserve insertion order, so `OrderedDict` should be used when its additional behavior or explicit semantics are useful.

### `deque`

`deque` is a double-ended queue designed for efficient additions and removals at either end.

It is useful for maintaining a rolling window of recent values or other queue-like workflows.

```python
from collections import deque

recent_scores = deque([70, 75, 80], maxlen=3)
recent_scores.append(85)

print(recent_scores)
# deque([75, 80, 85], maxlen=3)
```

### `namedtuple`

A `namedtuple` provides tuple-like records whose fields can be accessed by name.

It is useful for lightweight, immutable record structures.

### Grouping utilities

The project also includes helper functions for grouping student objects by attributes such as major or academic year. These utilities require student objects that contain the relevant attributes; those attributes are not present in the current sample CSV schema.

## Data Models and Type Safety

### Dataclasses

Dataclasses reduce repetitive code when defining classes that primarily store data.

The project uses data models such as `Student`, `Course`, and `Grade` to represent domain entities clearly.

### Type hints

Type hints document expected inputs and outputs, making functions easier to understand and enabling static analysis.

The project uses typed collections, optional values, union types, and structured report types where appropriate.

### `TypedDict`

`TypedDict` defines the expected keys and value types of dictionary-shaped data. It is useful for describing the structure of exported reports without requiring every report to be represented by a separate class.

### Separation of responsibilities

Keeping models, analytics, reporting, collection utilities, and the terminal interface in separate modules helps make the project easier to test and maintain.

## File Handling and Error Handling

The application reads grade data from CSV files and exports reports as JSON or text.

Context managers are used for file operations so that file resources are closed reliably after use.

The report generation process uses structured dictionaries and JSON serialization rather than manually constructing JSON strings.

Error handling should give useful feedback for situations such as:

- A file cannot be found or opened.
- A CSV file is malformed.
- Input data contains invalid values.
- A report cannot be written to the selected destination.
- A user cancels file selection or chooses an unsupported input.

## Testing and Code Quality

The project uses automated tests and static quality tools to improve reliability and maintainability.

Run the following commands from the project root with the virtual environment activated.

### Run tests

```powershell
python -m pytest -q
```

For verbose output:

```powershell
python -m pytest -v
```

### Check formatting

```powershell
python -m black --check main.py src tests
```

To format files when needed:

```powershell
python -m black main.py src tests
```

### Run linting

```powershell
python -m ruff check main.py src tests
```

Apply supported automatic fixes when appropriate:

```powershell
python -m ruff check main.py src tests --fix
```

Review changes after automatic fixes.

### Run static type checking

```powershell
python -m mypy src main.py
```

### Measure test coverage

Run tests with branch coverage:

```powershell
python -m coverage run --branch -m pytest
```

Generate a coverage report:

```powershell
python -m coverage report -m
```

A coverage percentage describes which measured code was exercised by the tests. It does not, by itself, prove that every behavior is correct.

### Check whitespace and patch formatting

```powershell
git diff --check
```

Run the tests and quality checks after making changes, and review the output before committing.

## Performance and Complexity

Let:

- \(N\) be the number of grade records.
- \(S\) be the number of distinct students.
- \(C\) be the number of distinct courses.
- \(T\) be the number of academic periods.

The current application loads and retains the grade records in memory. Its report aggregation and sorting work depends on the dataset size and the number of distinct students, courses, and periods.

A useful high-level estimate for the report-processing workflow is:

\[
O(N\log N + S\log S + C\log C + T\log T)
\]

This is a high-level estimate for the implemented aggregation and sorting workflow, not a formal guarantee for every individual function. Individual operations may have different costs.

The auxiliary data structures used by the report can require memory proportional to the grade records and the distinct entities being summarized. Since the application retains the dataset, its overall memory use is not constant with respect to input size.

### Collection performance considerations

| Collection | Appropriate use | Performance consideration |
|---|---|---|
| `Counter` | Counting occurrences | Efficient frequency counting for hashable values. |
| `defaultdict` | Grouping records | Avoids repeated manual initialization of grouped values. |
| `OrderedDict` | Explicit ordered mappings | Provides order-specific operations; a regular dictionary is sufficient for many ordered mappings. |
| `deque` | Queue and rolling-window operations | Efficient additions and removals at either end; accessing arbitrary middle elements is slower than indexing a list. |
| `namedtuple` | Lightweight records | Compact, immutable, tuple-like representation. |
| `dataclass` | Domain models | Improves clarity and reduces boilerplate, though memory usage depends on its configuration and fields. |

These are qualitative comparisons rather than benchmark results. No measured runtime or memory benchmark figures are claimed here.

### Possible memory improvement

For datasets that are too large to fit comfortably in memory, a future version could process CSV records incrementally and update running aggregates instead of retaining every grade record. That approach would require carefully redesigning operations that depend on sorting, exact medians, rankings, or full-record access.

## Sample Results

For the current sample dataset of 10 grade records, the previously verified overall statistics include:

| Metric | Result |
|---|---:|
| Number of grade records | 10 |
| Overall average | 79.8 |
| Median | 82.5 |
| Highest score | 100 |
| Lowest score | 55 |

The observed grade distribution is:

| Category | Count |
|---|---:|
| A | 3 |
| B | 3 |
| C | 2 |
| D | 1 |
| F | 1 |

The previously calculated semester averages are:

| Semester | Average |
|---|---:|
| S1 | 76.0 |
| S2 | 83.6 |

The difference between the two semester averages is **+7.6 percentage points**.

These values describe the current sample dataset. Results will change when the input records or selected analysis period change.

## Screenshot

The screenshot below illustrates the application's terminal dashboard.

Save the screenshot in `docs/images/StudentGradeAnalytics.png` before publishing this section.

![Student Grade Analytics dashboard](docs/images/StudentGradeAnalytics.png)

If the image does not appear on GitHub, confirm that the file exists at that exact path and has been committed to the repository.

## Limitations

- The supplied dataset is small and intended for demonstration.
- Records use student and course IDs rather than descriptive names.
- The current CSV schema does not include student majors, academic years as student attributes, or course credits.
- The application retains grade records in memory rather than implementing a fully streaming analytics pipeline.
- Performance notes are based on algorithmic considerations, not measured benchmarks.
- Grade boundaries and pass thresholds are configurable project assumptions only if the implementation explicitly supports changing them; otherwise, they are fixed project rules.

## Future Improvements

Potential enhancements include:

- Add configurable grade boundaries and pass thresholds.
- Add student names, course names, credits, and additional academic metadata.
- Support larger datasets with incremental processing where practical.
- Add measured time and memory benchmarks for different collection strategies.
- Add more visual reporting options.
- Improve validation messages for malformed CSV input.
- Add export options for additional report formats.
- Expand analytics with weighted averages and additional trend comparisons where the input schema supports them.

## Author

**Aline NIYONIZERA**

GitHub: [Aline-CROIRE](https://github.com/Aline-CROIRE)

---

This project was developed as a practical exercise in advanced Python programming, collections, data processing, testing, and software quality practices.
