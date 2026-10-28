"""Make the project root importable so tests can import the src package.

pytest adds the directory of a root-level conftest.py to sys.path, which lets
both ``pytest`` and ``python -m pytest`` resolve ``src.grade_analytics``.
"""
