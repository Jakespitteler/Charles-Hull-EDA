# First-slice tasks

Status: plan approved with Python >=3.13. Tasks 1–3 implemented and automated checks passed; user review of the first slice remains pending. Tasks 4–6 are not started.

## Task 1: Read-only workbook inventory

- [x] Implement minimal package/CLI inventory with explicit input/output paths and uv setup.
- Acceptance: list all sheets, dimensions, header candidates, formulas/cache availability, and unsupported sections; never output unrestricted cell contents in inventory. Preserve source hash. Local inputs/outputs are ignored.
- Verify: `uv sync --locked`; `uv run python -m charles_hull_eda inspect --input "<dummy workbook>" --output "outputs/inspection"`; targeted reader tests. Commands are implemented.
- Dependencies: none.
- Likely files (scope medium): `pyproject.toml`, `uv.lock`, `.gitignore`, `src/charles_hull_eda/__main__.py`, `tests/test_inventory.py`. Further modules only if needed and discussed.

## Task 2: Equipment hours with provenance

- [x] Extract daily asset/shift hours and compare reported daily totals with independently calculated sums.
- Acceptance: preserve blanks/zeros and source cells; detect Monday G52 cross-row reference and G61 coverage issue; flag unrecognised headers rather than misread them.
- Verify: focused synthetic-workbook tests plus direct comparison of selected dummy records/formulas; source hash unchanged.
- Dependencies: 1.
- Likely files (scope medium): reader/CLI refactor if needed, `src/charles_hull_eda/equipment.py`, `src/charles_hull_eda/validation.py`, `tests/test_equipment.py` (up to five files).

## Task 3: Thin equipment report

- [x] Add Plotly equipment-hour figures, issue summaries, and a notebook that calls modules.
- Acceptance: notebook contains configuration, narrative, module calls and display only; distinguish reported/calculated totals; keep synthetic status and missingness visible. No utilisation claims.
- Verify: focused summary/figure checks, clean-kernel run on dummy workbook, repeat-run table equality, manual chart inspection.
- Dependencies: 2.
- Likely files (scope medium): `src/charles_hull_eda/report.py`, `src/charles_hull_eda/charts.py`, `notebooks/01_daily_report.ipynb`, `tests/test_report.py`, CLI integration.

### Checkpoint 1

- [ ] User reviews table grain, cleaning decisions, chart/report experience, and Windows execution before the next sections.

## Task 4: Production movement report

- [ ] Extract daily movements/load counts with separate quantity units and measured/derived provenance; extend report.
- Acceptance: no summed tonnes/m3/bcm; blank template rows remain distinguishable from explicit zero observations; derived loads-to-volume factors are surfaced rather than validated as physical truth.
- Verify: synthetic tests for mixed units/blank rows, selected cell comparisons, clean report execution.
- Dependencies: 3.
- Likely files (scope medium): `src/charles_hull_eda/production.py`, `tests/test_production.py`, report/charts modules, notebook.

## Task 5: Daily context and weekly reconciliation

- [ ] Extract aggregate staffing, safety and weather fields; compare supported daily sections against Weekly Summary with explicit aggregation rules.
- Acceptance: no employee/leave/signature data in default tables; parse missingness and units transparently; distinguish sums from end-of-period counters and unmatched summary scopes.
- Verify: targeted extraction/reconciliation tests; manually sample each section on dummy workbook; no safety-risk ranking from activity counts.
- Dependencies: 4.
- Likely files (scope medium): `src/charles_hull_eda/context.py`, `src/charles_hull_eda/reconciliation.py`, `tests/test_context.py`, `tests/test_reconciliation.py`, report integration. Notebook presentation follows in Task 6.

### Checkpoint 2

- [ ] User reviews field meanings, reconciliation rules, and real-data validation output. Unknown definitions remain explicit.

## Task 6: First-pass report and handoff

- [ ] Complete notebook, data dictionary, findings/questions register, and Windows/macOS uv instructions.
- Acceptance: report presents coverage and limitations before patterns; includes evidence/alternative-explanation/next-question fields; user can supply a local path and run without editing parsing code. Mark untested platforms and real-data results honestly.
- Verify: `uv run pytest`; clean-kernel end-to-end dummy report; repeat-run consistency; source hash unchanged; review Git status for data/output leakage. User verifies Windows run separately.
- Dependencies: 5.
- Likely files (scope medium): notebook, `README.md`, `docs/data-dictionary.md`, `docs/findings.md`, report integration.

### Completion checkpoint

- [ ] Spec acceptance criteria checked; no unsupported claims about company performance.
- [ ] Decide with user which historical tables or new datasets warrant the next slice.
