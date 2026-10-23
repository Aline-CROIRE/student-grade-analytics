# Student Grade Analytics Tool

A Python application for loading, organizing, and analyzing student grades. The project uses Python data models, advanced collections, CSV processing, statistical calculations, and semester trend analysis.

## Features

- **Data models:** Represent students, courses, and grades.
- **Collection utilities:** Count grade categories, group students, create ordered reports, and calculate rolling averages.
- **CSV loading:** Read grade data from CSV files and validate required columns, student IDs, and score ranges.
- **Statistical analysis:** Calculate grade statistics, including the mean, median, and standard deviation.
- **Semester trends:** Calculate semester averages, sort semesters chronologically, and analyze changes between semesters.
- **Automated testing:** Test normal cases, edge cases, invalid inputs, and error handling.

## Requirements

- Python 3.11 or later
- pip

The project uses the following development tools:

- pytest — automated testing
- coverage — test coverage measurement
- mypy — static type checking
- Ruff — linting
- Black — code formatting

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

## Run the Tests

Run the complete test suite:

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
python -m mypy src
```

Check code quality:

```powershell
python -m ruff check src tests
```

Check code formatting:

```powershell
python -m black --check src tests
```

## Project Structure

```text
student-grade-analytics/
├── src/
│   └── grade_analytics/
│       ├── analytics.py
│       ├── collections_utils.py
│       ├── csv_loader.py
│       ├── models.py
│       └── semester_trends.py
├── tests/
│   ├── test_analytics.py
│   ├── test_collections_utils.py
│   ├── test_csv_loader.py
│   ├── test_models.py
│   └── test_semester_trends.py
├── data/
├── reports/
├── requirements.txt
└── README.md
```

## Quality Assurance

The project is tested with pytest and checked with coverage, mypy, Ruff, and Black. These tools help verify functionality, identify potential issues, maintain code quality, and keep formatting consistent.

## Learning Objectives

This project demonstrates the practical use of Python data structures, object-oriented programming, file handling, statistical calculations, automated testing, type checking, and code quality tools.