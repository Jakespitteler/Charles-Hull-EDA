from hashlib import sha256
from datetime import datetime

from openpyxl import Workbook

from charles_hull_eda.workbook import inspect_workbook


def test_inventory_retains_formulas_without_exposing_cell_contents(tmp_path):
    path = tmp_path / "report.xlsx"
    book = Workbook()
    sheet = book.active
    sheet.title = "Monday"
    sheet["A1"] = "PRIVATE NAME"
    sheet["B1"] = "=1+2"
    sheet["A3"] = datetime(2026, 11, 16)
    sheet.merge_cells("A2:B2")
    book.save(path)
    before = sha256(path.read_bytes()).hexdigest()

    result = inspect_workbook(path)

    assert result["source_sha256"] == before
    assert sha256(path.read_bytes()).hexdigest() == before
    assert "PRIVATE NAME" not in str(result)
    assert result["sheets"][0]["formula_count"] == 1
    assert result["sheets"][0]["missing_formula_cache_count"] == 1
    assert result["sheets"][0]["merged_range_count"] == 1
    assert result["sheets"][0]["date_cell_min"] == "2026-11-16"
