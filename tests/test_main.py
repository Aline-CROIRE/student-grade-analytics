import builtins
import json

import main as application


def test_native_picker_returns_selected_path_and_always_closes_root(
    monkeypatch,
    tmp_path,
):
    class FakeRoot:
        destroyed = False

        def withdraw(self):
            pass

        def attributes(self, *_args):
            pass

        def destroy(self):
            self.destroyed = True

    root = FakeRoot()
    monkeypatch.setattr(application.tk, "Tk", lambda: root)
    monkeypatch.setattr(
        application.filedialog,
        "askopenfilename",
        lambda **_kwargs: str(tmp_path / "grades.csv"),
    )

    assert application.choose_input_file() == tmp_path / "grades.csv"
    assert root.destroyed


def test_native_picker_cancellation_returns_none_and_closes_root(monkeypatch):
    class FakeRoot:
        destroyed = False

        def withdraw(self):
            pass

        def attributes(self, *_args):
            pass

        def destroy(self):
            self.destroyed = True

    root = FakeRoot()
    monkeypatch.setattr(application.tk, "Tk", lambda: root)
    monkeypatch.setattr(
        application.filedialog,
        "askopenfilename",
        lambda **_kwargs: "",
    )

    assert application.choose_input_file() is None
    assert root.destroyed


def write_csv(path, records):
    path.write_text(
        "student_id,course_id,score,semester\n" + records,
        encoding="utf-8",
    )
    return path


def test_choose_analysis_period_reprompts_and_orders_periods(monkeypatch, capsys):
    from src.grade_analytics.models import Grade

    choices = iter(["invalid", "2"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(choices))

    selected = application.choose_analysis_period(
        [
            Grade("S001", "CS101", 80, "2027-S1"),
            Grade("S002", "CS101", 70, "2026-S2"),
        ]
    )

    assert selected is not None
    assert selected[0] == "Academic year 2026"
    assert len(selected[1]) == 1
    assert "Invalid selection" in capsys.readouterr().out


def test_main_loads_csv_selects_period_and_exports_real_reports(
    tmp_path,
    monkeypatch,
    capsys,
):
    csv_path = write_csv(
        tmp_path / "grades.csv",
        "S001,CS101,80,2026-S1\n" "S002,CS101,70,2026-S1\n" "S003,CS102,90,2026-S2\n",
    )
    monkeypatch.setattr(application, "__file__", str(tmp_path / "main.py"))
    monkeypatch.setattr(application, "choose_input_file", lambda: csv_path)
    choices = iter(["3", "1", "", "4"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(choices))

    application.main()

    report_path = tmp_path / "reports" / "grades_semester_2026_s1_report.json"
    text_path = tmp_path / "reports" / "grades_semester_2026_s1_report.txt"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    text = text_path.read_text(encoding="utf-8")

    assert report["summary"]["count"] == 2
    assert report["dataset_overview"]["semesters"] == ["2026-S1"]
    assert "Semester 2026-S1" in text
    assert "Percentile" in text
    assert "Reports exported successfully." in capsys.readouterr().out


def test_main_analyzes_a_second_period_without_stale_report_data(
    tmp_path,
    monkeypatch,
    capsys,
):
    csv_path = write_csv(
        tmp_path / "grades.csv",
        "S001,CS101,80,2026-S1\nS002,CS102,40,2026-S2\n",
    )
    monkeypatch.setattr(application, "__file__", str(tmp_path / "main.py"))
    monkeypatch.setattr(application, "choose_input_file", lambda: csv_path)
    choices = iter(["3", "2", "4", "1", "", "4"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(choices))

    application.main()

    report_path = tmp_path / "reports" / "grades_semester_2026_s2_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["count"] == 1
    assert report["summary"]["mean"] == 40.0
    assert report["pass_fail"]["failing_records"] == 1
    assert "Reports exported successfully." in capsys.readouterr().out


def test_main_recovers_from_invalid_csv_and_allows_period_cancellation(
    tmp_path,
    monkeypatch,
    capsys,
):
    invalid_path = write_csv(
        tmp_path / "invalid.csv",
        "S001,CS101,80,2026-S3\n",
    )
    valid_path = write_csv(
        tmp_path / "valid.csv",
        "S001,CS101,80,2026-S1\n",
    )
    paths = iter([invalid_path, valid_path])
    monkeypatch.setattr(application, "choose_input_file", lambda: next(paths))
    choices = iter(["y", "0"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(choices))

    application.main()

    output = capsys.readouterr().out
    assert "Invalid semester on row 2" in output
    assert "Loaded 1 grade records from 'valid.csv'." in output
    assert "No analysis period selected. Goodbye!" in output


def test_file_picker_cancellation_exits_without_prompting(monkeypatch, capsys):
    monkeypatch.setattr(application, "choose_input_file", lambda: None)

    def unexpected_input(_prompt):
        raise AssertionError("input must not be requested after picker cancellation")

    monkeypatch.setattr(builtins, "input", unexpected_input)

    application.main()

    assert "No file selected. Goodbye!" in capsys.readouterr().out


def test_switching_csv_uses_new_file_for_following_report(
    tmp_path,
    monkeypatch,
    capsys,
):
    first_path = write_csv(tmp_path / "first.csv", "S001,CS101,90,2026-S1\n")
    second_path = write_csv(tmp_path / "second.csv", "S002,CS102,55,2027-S2\n")
    paths = iter([first_path, second_path])
    monkeypatch.setattr(application, "choose_input_file", lambda: next(paths))
    monkeypatch.setattr(application, "__file__", str(tmp_path / "main.py"))
    choices = iter(["1", "3", "1", "1", "", "4"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(choices))

    application.main()

    report_path = tmp_path / "reports" / "second_entire_dataset_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["count"] == 1
    assert report["summary"]["mean"] == 55.0
    assert "Reports exported successfully." in capsys.readouterr().out


def test_export_refuses_to_overwrite_existing_report(
    tmp_path,
    monkeypatch,
    capsys,
):
    from src.grade_analytics.json_report import build_grade_report
    from src.grade_analytics.models import Grade

    source = tmp_path / "grades.csv"
    reports = tmp_path / "reports"
    reports.mkdir()
    existing = reports / "grades_entire_dataset_report.json"
    existing.write_text("preserve", encoding="utf-8")
    monkeypatch.setattr(builtins, "input", lambda _prompt: "n")
    report = build_grade_report([Grade("S001", "CS101", 80, "2026-S1")])

    exported = application.export_report(
        report,
        "Entire dataset",
        tmp_path,
        source,
    )

    assert exported is False
    assert existing.read_text(encoding="utf-8") == "preserve"
    assert "Export cancelled" in capsys.readouterr().out


def test_export_overwrites_after_user_confirmation(
    tmp_path,
    monkeypatch,
    capsys,
):
    from src.grade_analytics.json_report import build_grade_report
    from src.grade_analytics.models import Grade

    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "grades_entire_dataset_report.json").write_text(
        "old data",
        encoding="utf-8",
    )
    monkeypatch.setattr(builtins, "input", lambda _prompt: "y")
    report = build_grade_report([Grade("S001", "CS101", 80, "2026-S1")])

    exported = application.export_report(
        report,
        "Entire dataset",
        tmp_path,
        tmp_path / "grades.csv",
    )

    assert exported is True
    saved = json.loads(
        (reports / "grades_entire_dataset_report.json").read_text(encoding="utf-8")
    )
    assert saved["summary"]["mean"] == 80.0
    assert (reports / "grades_entire_dataset_report.txt").exists()
    assert "Reports exported successfully." in capsys.readouterr().out


def test_export_reports_partial_failure_without_success_message(
    tmp_path,
    monkeypatch,
    capsys,
):
    from src.grade_analytics.json_report import build_grade_report
    from src.grade_analytics.models import Grade

    def fail_text_write(*_args, **_kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr(application, "write_text_report", fail_text_write)
    report = build_grade_report([Grade("S001", "CS101", 80, "2026-S1")])

    exported = application.export_report(
        report,
        "Entire dataset",
        tmp_path,
        tmp_path / "grades.csv",
    )

    output = capsys.readouterr().out
    assert exported is False
    assert (tmp_path / "reports" / "grades_entire_dataset_report.json").exists()
    assert "JSON report was written" in output
    assert "Reports exported successfully." not in output


def test_export_json_write_failure_is_reported(
    tmp_path,
    monkeypatch,
    capsys,
):
    from src.grade_analytics.json_report import build_grade_report
    from src.grade_analytics.models import Grade

    def fail_json_write(*_args, **_kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr(application, "write_json_report", fail_json_write)
    report = build_grade_report([Grade("S001", "CS101", 80, "2026-S1")])

    exported = application.export_report(
        report,
        "Entire dataset",
        tmp_path,
        tmp_path / "grades.csv",
    )

    output = capsys.readouterr().out
    assert exported is False
    assert "Could not export reports: permission denied" in output
    assert "Reports exported successfully." not in output
