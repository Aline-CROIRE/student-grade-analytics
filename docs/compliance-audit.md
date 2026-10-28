# Compliance Audit and Remediation Tracker

This document records the findings of a compliance audit of the project
against the [original assignment brief](assignment-brief.md), and tracks how
each finding is resolved. Each remediation phase is delivered on its own
branch and merged into `develop` through a pull request.

## Baseline (before remediation)

Recorded on the `chore/repository-baseline` branch, created from `develop`
at commit `ecc2e0c`, using Python 3.14.8.

| Check | Command | Result |
|---|---|---|
| Tests | `python -m pytest -q` | 110 passed |
| Tests (plain runner) | `pytest -q` | 8 collection errors: `ModuleNotFoundError: No module named 'src'` |
| Linting | `python -m ruff check .` | All checks passed |
| Formatting | `python -m black --check .` | All files unchanged |
| Type checking | `python -m mypy src main.py` | No issues found |
| Coverage | `python -m coverage run --branch -m pytest`, then `python -m coverage report --include="src/*,main.py"` | 94% of application code (branch coverage) |

The sample dataset (`data/grades.csv`) produces correct results: mean 79.8,
median 82.5, distribution A3/B3/C2/D1/F1, semester averages 2026-S1 = 76.0
and 2026-S2 = 83.6. No calculation defects were found.

## Findings

Classification: **Mandatory** findings map directly to the brief or its
submission requirements. **Recommended** findings affect quality or output
marks but are not explicit requirements.

| ID | Finding | Requirement | Class | Phase | Status |
|---|---|---|---|---|---|
| C1 | README has no JSON report example | Submission: "JSON report examples" | Mandatory | 9 | Open |
| C2 | Plain `pytest` fails because `src` is not importable | Testing & Validation | Recommended | 2 | Resolved |
| C3 | README CSV example is rejected by the loader (`S1` instead of `YYYY-S1`); semester labels in sample output are wrong; placeholder text; outdated project tree | Submission: "Sample input/output"; Documentation | Mandatory | 9 | Open |
| C4 | Uncommitted deletion of a duplicate screenshot (`docs/working screenshoot.png`) | Repository hygiene | Recommended | 1 | Resolved |
| H1 | No measured comparison of memory usage between collection approaches; performance notes are qualitative only | Memory Efficiency: "Compare memory usage of different collection approaches" | Mandatory | 7 | Open |
| H2 | `deque` is not used to track semester trends; `RollingAverage` is not used by the application | Statistical Processing: "Track grade trends over semesters using deque" | Mandatory | 4 | Resolved |
| H3 | Grouping students by major/year is only exercised in unit tests; the sample data has no major/year, and `Student`/`Course` are unused by the application | Data Structures: "Use defaultdict for grouping students by major/year" | Mandatory | 5 | Resolved (`Course` is still defined but not used by the application) |
| H4 | No test uses the shipped `data/grades.csv` | Testing & Validation: "sample data tests" | Mandatory | 2 | Resolved |
| H5 | The application requires the Tkinter file picker; no command-line path option; Tkinter requirement undocumented | Setup instructions | Recommended | 8, 9 | Open |
| M1 | JSON report has no rank or top-performer data | Description: "insights like top performers"; Milestone: "implement ranking algorithm" | Recommended | 6 | Open |
| M2 | JSON floats are not rounded (e.g. `7.599999999999994`); `modes` lists every score when none repeat | Final Integration: "JSON formatting" | Recommended | 6 | Open |
| M3 | `build_grade_report` duplicates logic from `analytics.py` and `semester_trends.py`; unused `_grade_category`; two TypedDicts named `GradeReport` | Code Quality & Structure | Recommended | 3 | Resolved |
| M4 | CSV loader does not use a generator | Memory Efficiency: generators (bonus) | Optional | 7 | Open |
| M5 | Duplicate CSV rows are accepted silently | Error handling | Optional | 8 | Open |

## Remediation phases

| Phase | Branch | Findings |
|---|---|---|
| 1 | `chore/repository-baseline` | C4; adds this tracker and the brief |
| 2 | `test/sample-data-baseline` | C2, H4 |
| 3 | `refactor/report-reuses-analytics` | M3 |
| 4 | `feat/deque-semester-trends` | H2 |
| 5 | `feat/major-year-grouping` | H3 |
| 6 | `feat/json-rankings-rounding` | M1, M2 |
| 7 | `perf/memory-comparison` | H1, M4 |
| 8 | `feat/cli-path-and-validation` | H5, M5 |
| 9 | `docs/readme-compliance` | C1, C3, H5 (documentation) |
| 10 | Release PR `develop` → `main` | Final verification |
