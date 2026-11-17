"""Workbook access without recalculation or source mutation."""

from contextlib import contextmanager
from datetime import date, datetime
from hashlib import file_digest
from pathlib import Path
from warnings import catch_warnings

from openpyxl import load_workbook


def fingerprint(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


@contextmanager
def read_workbook(path: str | Path):
    path = Path(path).expanduser().resolve(strict=True)
    before = fingerprint(path)
    # Capture openpyxl's unsupported-extension warnings rather than hiding them.
    # No workbook is ever saved, so source extensions remain untouched.
    with catch_warnings(record=True) as notices:
        formulas = load_workbook(path, data_only=False, keep_links=False)
        try:
            cached = load_workbook(path, data_only=True, keep_links=False)
            try:
                yield formulas, cached, before, notices
            finally:
                cached.close()
        finally:
            formulas.close()
    if fingerprint(path) != before:
        raise RuntimeError("Input changed during inspection; discard these results.")


def inventory(formulas, cached, digest: str, notices) -> dict:
    sheets = []
    for sheet in formulas:
        formula_cells = [c for row in sheet for c in row if c.data_type == "f"]
        dates = [c.value.date() if isinstance(c.value, datetime) else c.value
                 for row in cached[sheet.title] for c in row if isinstance(c.value, (date, datetime))]
        known_headers = {"Machine", "Date", "DATE", "Equipment", "Work Area", "Staff", "Description"}
        candidates = [c.coordinate for row in sheet.iter_rows(max_row=min(sheet.max_row, 75))
                      for c in row if isinstance(c.value, str) and c.value.strip() in known_headers]
        sheets.append({
            "sheet": sheet.title,
            "rows": sheet.max_row,
            "columns": sheet.max_column,
            "state": sheet.sheet_state,
            "header_candidate_cells": candidates,
            "date_cell_min": min(dates).isoformat() if dates else None,
            "date_cell_max": max(dates).isoformat() if dates else None,
            "date_coverage_note": "Date cells only; not proof of populated measurements or complete history",
            "merged_range_count": len(sheet.merged_cells.ranges),
            "formula_count": len(formula_cells),
            "missing_formula_cache_count": sum(
                cached[sheet.title][c.coordinate].value is None for c in formula_cells
            ),
            "extraction_status": "inventoried_only",
        })
    return {
        "source_sha256": digest,
        "formula_cache_freshness": "unknown; cached values are not recalculated",
        "reader_warnings": sorted({str(n.message) for n in notices}),
        "sheets": sheets,
    }


def inspect_workbook(path: str | Path) -> dict:
    with read_workbook(path) as args:
        return inventory(*args)
