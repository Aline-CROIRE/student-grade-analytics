
# Student Grade Analytics Tool

A Python application that loads student grade records from CSV files and generates statistical reports, student rankings, course comparisons, grade distributions, and semester trends.

The application provides an interactive terminal interface and can export reports in JSON and plain-text formats.

## Features

- **Data models:** Use dataclasses and typed models to represent students, courses, and grades.
- **Advanced collections:** Apply `Counter`, `defaultdict`, `OrderedDict`, `deque`, and named tuples where appropriate.
- **CSV input:** Load grade records from a selected CSV file and validate the input.
- **Statistical analysis:** Calculate the mean, median, minimum, maximum, modes, and percentile ranks.
- **Grade distribution:** Summarize grade categories and their percentages.
- **Student rankings:** Compare student averages and handle tied rankings.
- **Course performance:** Compare course averages, record counts, and pass rates.
- **Semester trends:** Compare semester averages and identify increases or decreases.
- **Pass/fail analysis:** Summarize passing and failing records and student averages.
- **Report exports:** Save analysis results as JSON and readable TXT reports.
- **Error handling:** Validate input and handle common file and data problems.
- **Automated quality checks:** Use pytest, coverage, mypy, Ruff, and Black.

## Requirements

- Python 3.11 or later
- pip

## Setup

Clone the repository:

```bash
git clone https://github.com/Aline-CROIRE/student-grade-analytics.git
cd student-grade-analytics
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the application

Start the interactive application:

```powershell
python main.py
```

The application allows you to:

1. Select a CSV file using a file picker.
2. Choose the entire dataset, an academic year, or a semester.
3. Review the analytics dashboard.
4. Export the selected analysis to JSON and TXT.
5. Analyze another period or select another CSV file.

## Input CSV format

The CSV file must contain the following columns:

```csv
student_id,course_id,score,semester
S001,CS101,80,2026-S1
S001,CS102,90,2026-S1
S002,CS101,60,2026-S1
S002,CS102,70,2026-S2
```

Each row represents one student's grade for a course in a semester.

The application uses student IDs and course IDs because names and additional course information are not included in this format.

## Reports

The application exports two report formats:

- **JSON:** Structured analysis results suitable for further processing.
- **TXT:** A readable report containing the dashboard sections and key findings.

Generated reports are saved in the `reports/` directory.

The passing threshold is currently set to 60%. Confirm the appropriate threshold for your institution before using the results for official academic decisions.

## Run the tests

Run all tests:

```powershell
python -m pytest -v
```

Measure statement and branch coverage:

```powershell
python -m coverage run --branch -m pytest
python -m coverage report -m
```

Check type correctness:

```powershell
python -m mypy src main.py
```

Check code quality:

```powershell
python -m ruff check src tests main.py
```

Check formatting:

```powershell
python -m black --check src tests main.py
```

## Project structure

```text
student-grade-analytics/
├── data/
├── reports/
├── src/
│   └── grade_analytics/
│       ├── analytics.py
│       ├── collections_utils.py
│       ├── csv_loader.py
│       ├── json_report.py
│       ├── models.py
│       ├── semester_trends.py
│       └── terminal_ui.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## Error handling

The application validates CSV input before analysis and provides error handling for common data and file problems. Empty datasets cannot produce meaningful analytics, and report exports create their parent directories when needed.

## Learning objectives

This project demonstrates:

- Python data structures and advanced collections.
- Dataclasses, type hints, and maintainable module design.
- CSV and JSON file handling.
- Statistical analysis and data interpretation.
- Exception handling and input validation.
- Automated testing and branch coverage.
- Static type checking, linting, and code formatting.
- Git-based feature development and quality assurance.
