"""Exercise the installed command interface with real generated workbooks."""

import json
from pathlib import Path
import subprocess
import sys

from openpyxl import Workbook

from test_equipment import example


def run_cli(command: str, source: Path, output: Path):
    return subprocess.run(
        [sys.executable, "-m", "charles_hull_eda", command,
         "--input", str(source), "--output", str(output)],
        capture_output=True, text=True, check=False,
    )


def test_cli_generates_auditable_equipment_outputs(tmp_path):
    source = tmp_path / "daily report.xlsx"
    example(source)
    output = tmp_path / "local results"
    result = run_cli("analyse", source, output)
    assert result.returncode == 0, result.stderr
    assert len(json.loads((output / "equipment-hours.json").read_text())) == 4
    assert json.loads((output / "manifest.json").read_text())["synthetic"] is True


def test_cli_marks_unextractable_workbook_as_failure_but_saves_issues(tmp_path):
    source = tmp_path / "other.xlsx"
    Workbook().save(source)
    output = tmp_path / "results"
    result = run_cli("analyse", source, output)
    assert result.returncode == 1
    issues = json.loads((output / "issues.json").read_text())
    assert any(issue["rule"] == "no_equipment_data" for issue in issues)


def test_cli_reports_invalid_input_without_success_artifacts(tmp_path):
    source = tmp_path / "invalid.xlsx"
    source.write_text("Not an Excel workbook", encoding="utf-8")
    output = tmp_path / "results"
    result = run_cli("inspect", source, output)
    assert result.returncode == 2
    assert "Unable to complete" in result.stderr
    assert not output.exists()
