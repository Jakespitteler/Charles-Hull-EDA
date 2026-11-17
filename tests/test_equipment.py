from datetime import datetime

import pandas as pd
from openpyxl import Workbook

from charles_hull_eda.report import analyse_workbook


def example(path):
    book = Workbook()
    sheet = book.active
    sheet.title = "Monday"
    sheet["F3"] = "DATE:"
    sheet["G3"] = datetime(2026, 11, 16)
    for cell, value in {
        "A10": "Machine", "B10": "D/S Hours Worked", "E10": "N/S Hours Worked",
        "G10": "Total Daily Hours", "A11": "Screen - TEST1", "B11": 7,
        "E11": 7, "G11": "=SUM(B12+E11)", "A12": "Stacker - TEST2",
        "B12": 0, "A13": "TOTAL HOURS", "G13": "=SUM(G11:G11)",
    }.items():
        sheet[cell] = value
    book.save(path)


def test_shift_missingness_and_formula_scope_are_auditable(tmp_path):
    path = tmp_path / "example.xlsx"
    example(path)
    report = analyse_workbook(path)
    hours = report.hours
    assert len(hours) == 4
    blank = hours.loc[(hours.asset == "Stacker - TEST2") & (hours["shift"] == "night")].iloc[0]
    assert blank.value_state == "blank"
    assert pd.isna(blank.hours)
    zero = hours.loc[(hours.asset == "Stacker - TEST2") & (hours["shift"] == "day")].iloc[0]
    assert zero.hours == 0 and zero.value_state == "explicit_zero"
    assert report.totals.iloc[0].calculated_hours == 14
    assert pd.isna(report.totals.iloc[1].calculated_hours)
    rules = set(report.issues.rule)
    assert {"formula_scope", "missing_formula_cache", "incomplete_shifts"} <= rules
    assert "G13" in set(report.issues.cell)
    assert "G11" in set(report.issues.cell)
    assert report.hours.equals(analyse_workbook(path).hours)


def test_unsupported_layout_is_an_issue_not_silent_success(tmp_path):
    path = tmp_path / "example.xlsx"
    example(path)
    from openpyxl import load_workbook
    book = load_workbook(path)
    book["Monday"]["B10"] = "UNRECOGNISED HOURS"
    book.save(path)
    report = analyse_workbook(path)
    assert report.hours.empty
    assert "unsupported_layout" in set(report.issues.rule)


def test_reported_total_is_not_replaced_by_calculated_total(tmp_path):
    from openpyxl import load_workbook
    path = tmp_path / "example.xlsx"
    example(path)
    book = load_workbook(path)
    book["Monday"]["G11"] = 3
    book.save(path)
    report = analyse_workbook(path)
    assert report.totals.iloc[0].reported_hours == 3
    assert report.totals.iloc[0].calculated_hours == 14
    assert "total_mismatch" in set(report.issues.rule)


def test_unrelated_workbook_cannot_look_like_successful_extraction(tmp_path):
    path = tmp_path / "unrelated.xlsx"
    Workbook().save(path)
    report = analyse_workbook(path)
    assert report.hours.empty
    assert "error" in set(report.issues.severity)
