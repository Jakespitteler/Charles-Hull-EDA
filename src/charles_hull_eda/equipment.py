"""Extract the recognised daily equipment table; reject unfamiliar layouts."""

from datetime import date, datetime
from math import isfinite

from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import TokenizerError
from openpyxl.utils.cell import range_boundaries, get_column_letter
import pandas as pd

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
HOUR_COLUMNS = ["date", "sheet", "asset", "shift", "hours", "value_state", "cell", "raw_value", "formula", "source_sha256"]
TOTAL_COLUMNS = ["date", "sheet", "asset", "reported_hours", "reported_state", "calculated_hours", "cell", "formula", "source_sha256"]
ISSUE_COLUMNS = ["rule", "severity", "sheet", "cell", "detail"]


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def measurement(cell, cache):
    raw = cell.value
    formula = raw if cell.data_type == "f" else None
    value = cache.value if formula else raw
    if formula and value is None:
        state = "missing_formula_cache"
    elif value is None or (isinstance(value, str) and not value.strip()):
        state = "blank"
    elif number(value):
        state = "formula_zero" if formula and value == 0 else (
            "formula_numeric" if formula else "explicit_zero" if value == 0 else "numeric"
        )
    else:
        state = "not_applicable" if str(value).strip().lower() in {"n/a", "na"} else "unparseable"
    return (float(value) if number(value) else None), state, raw, formula


def references(formula: str) -> set[str] | None:
    """Recognise local cell references for scope checking, not formula evaluation."""
    result = set()
    try:
        for token in Tokenizer(formula).items:
            if token.type == "OPERAND" and token.subtype == "RANGE":
                if "!" in token.value:
                    return None
                c1, r1, c2, r2 = range_boundaries(token.value.replace("$", ""))
                if None in (c1, r1, c2, r2) or (c2-c1+1)*(r2-r1+1) > 10000:
                    return None
                result.update(f"{get_column_letter(c)}{r}" for r in range(r1, r2+1) for c in range(c1, c2+1))
        return result
    except (ValueError, TypeError, IndexError, TokenizerError):
        return None


def extract_equipment(formulas, cached, digest):
    hours, totals, issues = [], [], []

    def issue(rule, sheet, cell, detail, severity="warning"):
        issues.append(dict(rule=rule, severity=severity, sheet=sheet, cell=cell, detail=detail))

    def check_scope(cell, expected, sheet):
        if cell.data_type == "f" and references(cell.value) != expected:
            issue("formula_scope", sheet, cell.coordinate, "Formula references do not match the recognised table scope; inspect source formula.")

    for day in DAYS:
        if day not in formulas.sheetnames:
            issue("missing_daily_sheet", day, "", "Expected daily sheet is absent.")
            continue
        sheet, cache = formulas[day], cached[day]
        headers = [r[0].row for r in sheet.iter_rows() if r[0].value == "Machine"]
        if len(headers) != 1:
            issue("unsupported_layout", day, "", "Expected one Machine header.", "error")
            continue
        header = headers[0]
        expected = {"B": "D/S Hours Worked", "E": "N/S Hours Worked", "G": "Total Daily Hours"}
        if any(sheet[f"{col}{header}"].value != label for col, label in expected.items()):
            issue("unsupported_layout", day, f"A{header}", "Equipment column headings differ from supported template.", "error")
            continue
        ends = [r for r in range(header+1, sheet.max_row+1) if sheet[f"A{r}"].value == "TOTAL HOURS"]
        if len(ends) != 1:
            issue("unsupported_layout", day, f"A{header}", "Expected one TOTAL HOURS boundary.", "error")
            continue
        stamp = cache["G3"].value
        if not isinstance(stamp, (date, datetime)) or sheet["F3"].value != "DATE:":
            issue("invalid_date", day, "G3", "Date/header not recognised; section was not extracted.", "error")
            continue
        stamp = stamp.date() if isinstance(stamp, datetime) else stamp
        if stamp.strftime("%A") != day:
            issue("weekday_mismatch", day, "G3", "Date does not agree with sheet weekday.")
        end = ends[0]
        asset_rows = []
        seen = set()
        for row in range(header+1, end):
            asset = sheet[f"A{row}"].value
            if asset is None:
                if any(sheet[f"{c}{row}"].value is not None for c in ("B", "E", "G")):
                    issue("missing_asset", day, f"A{row}", "Hours exist without an asset label; row not extracted.", "error")
                continue
            if not isinstance(asset, str):
                issue("invalid_asset", day, f"A{row}", "Asset label must be text.", "error")
                continue
            if asset in seen:
                issue("duplicate_asset", day, f"A{row}", "Repeated asset label; rows retained, not merged.", "error")
            seen.add(asset)
            asset_rows.append(row)
            shift_values = []
            for col, shift in (("B", "day"), ("E", "night")):
                cell = sheet[f"{col}{row}"]
                value, state, raw, formula = measurement(cell, cache[cell.coordinate])
                shift_values.append(value)
                hours.append(dict(date=stamp.isoformat(), sheet=day, asset=asset, shift=shift,
                                  hours=value, value_state=state, cell=cell.coordinate,
                                  raw_value=raw, formula=formula, source_sha256=digest))
                if state in {"unparseable", "missing_formula_cache"} or (value is not None and value < 0):
                    issue("invalid_hours", day, cell.coordinate, f"Hours require review: {state}; negative values also flagged.")
            cell = sheet[f"G{row}"]
            reported, state, _, formula = measurement(cell, cache[cell.coordinate])
            calculated = sum(shift_values) if all(v is not None for v in shift_values) else None
            totals.append(dict(date=stamp.isoformat(), sheet=day, asset=asset, reported_hours=reported,
                               reported_state=state, calculated_hours=calculated, cell=cell.coordinate,
                               formula=formula, source_sha256=digest))
            check_scope(cell, {f"B{row}", f"E{row}"}, day)
            if state == "missing_formula_cache":
                issue(state, day, cell.coordinate, "Formula has no cached result; not recalculated.")
            if calculated is None:
                issue("incomplete_shifts", day, cell.coordinate, "A shift is missing or unparseable; calculated total withheld.")
            elif reported is not None and abs(reported-calculated) > 1e-9:
                issue("total_mismatch", day, cell.coordinate, f"Reported {reported:g} h; shift sum {calculated:g} h.")
        check_scope(sheet[f"G{end}"], {f"G{r}" for r in asset_rows}, day)
    if not hours:
        issue("no_equipment_data", "", "", "No supported equipment records were extracted.", "error")
    return (pd.DataFrame(hours, columns=HOUR_COLUMNS), pd.DataFrame(totals, columns=TOTAL_COLUMNS),
            pd.DataFrame(issues, columns=ISSUE_COLUMNS))
