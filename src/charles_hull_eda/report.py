"""One analysis entry point shared by CLI and notebook."""

from dataclasses import dataclass
import json
from pathlib import Path

import pandas as pd

from .equipment import extract_equipment
from .workbook import inventory, read_workbook


@dataclass
class EquipmentReport:
    inventory: dict
    hours: pd.DataFrame
    totals: pd.DataFrame
    issues: pd.DataFrame
    synthetic: bool


def analyse_workbook(path: str | Path, *, synthetic: bool = True) -> EquipmentReport:
    with read_workbook(path) as (formulas, cached, digest, notices):
        tables = extract_equipment(formulas, cached, digest)
        info = inventory(formulas, cached, digest, notices)
        extracted = set(tables[0]["sheet"])
        for sheet in info["sheets"]:
            if sheet["sheet"] in extracted:
                sheet["extraction_status"] = "equipment_section_only"
        return EquipmentReport(info, *tables, synthetic)


def export_report(report: EquipmentReport, output: str | Path) -> None:
    """Export local analytical artifacts; JSON preserves missingness and formulas as text."""
    from .charts import equipment_hours_figure

    output = Path(output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "inventory.json": json.dumps(report.inventory, indent=2),
        "equipment-hours.json": report.hours.to_json(orient="records", indent=2),
        "equipment-totals.json": report.totals.to_json(orient="records", indent=2),
        "issues.json": report.issues.to_json(orient="records", indent=2),
        "manifest.json": json.dumps({"synthetic": report.synthetic,
                                      "source_sha256": report.inventory["source_sha256"],
                                      "scope": "equipment sections only; other sections unextracted"}, indent=2),
    }
    # Do not follow existing artifact symlinks to unrelated files.
    targets = [output / name for name in [*artifacts, "equipment-hours.html"]]
    if any(p.is_symlink() for p in targets):
        raise ValueError("Output artifacts must not be symlinks.")
    for name, content in artifacts.items():
        (output / name).write_text(content, encoding="utf-8")
    equipment_hours_figure(report).write_html(output / "equipment-hours.html", include_plotlyjs=True)
