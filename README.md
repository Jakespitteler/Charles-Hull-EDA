# Charles Hull EDA

Reproducible workbook exploration, developed collaboratively for Charles Hull's tailings operations. The current slice inventories all sheets and extracts daily equipment shift hours, reported totals, and validation issues. Business conclusions require real-data review.

## Setup (Windows or macOS)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), open the checkout in VS Code, and run from its root:

```text
uv sync --locked
uv run python --version
uv run pytest
```

Python must be **3.13 or newer**. `.python-version` selects 3.13 by default; uv can install it. `uv.lock` pins dependencies. Current validation is on Linux/Python 3.13.18; Windows/macOS execution remains to be verified. No shell activation is needed.

## Run on a local workbook

Keep reports in ignored `data/` or outside the checkout. Neither input reports nor generated results belong in Git.

```text
uv run python -m charles_hull_eda inspect --input "data/report.xlsx" --output "outputs/inspection"
uv run python -m charles_hull_eda analyse --input "data/report.xlsx" --output "outputs/first-pass"
```

By default results are labelled synthetic. Add `--real-data` when using actual data. This changes the label, not validation or evidence strength. Output files in the chosen directory are replaced on reruns; use a different directory to preserve a prior run.

Outputs: inventory JSON, shift-hour JSON, totals JSON, issues JSON, manifest, and a self-contained interactive HTML chart (earliest available day). JSON preserves nulls and source formulas as text. HTML contains embedded data; review before sharing. Exit codes: 0 completed without extraction errors (warnings may remain); 1 analysis contains extraction errors; 2 invalid invocation/input/output. Always read the issues.

## Notebook report

Install the VS Code Python and Jupyter extensions. Open `notebooks/01_daily_report.ipynb` and choose this project's `.venv` Python interpreter as the kernel. Set `INPUT_PATH`, `SYNTHETIC`, and optionally `REPORT_DATE` in the configuration cell, then restart the kernel and Run All. Relative paths are relative to the notebook directory; an absolute path works too. VS Code may require trusting the notebook to render the interactive HTML.

The notebook contains configuration, narrative and display calls. Extraction, validation and charts live in `src/charles_hull_eda/`. Clear notebook outputs before committing; executed output may contain real data.

## Interpretation limits

- Blanks, explicit zeros, invalid entries and missing formula caches are distinct. Incomplete shift pairs do not receive a calculated daily total.
- Reported totals remain alongside independently calculated totals. Formula reference checks do not evaluate arbitrary Excel formulas or establish correctness of the arithmetic.
- openpyxl does not recalculate formulas. Cached values may be stale; warnings are captured in the inventory. The source is never saved, and its hash is checked before/after reading.
- Unsupported equipment headers/dates produce issues rather than guessed extraction. Daily sheet names and the recognised report layout are required for this slice.
- Operating hours alone do not establish utilisation, productivity or bottlenecks. Asset labels are retained as reported, not reconciled with the equipment register yet.
- Weekly reconciliation, production, staffing/safety/weather extraction and historical analyses remain pending. Date ranges in the inventory describe date cells, not necessarily populated measurements.

See [SPEC.md](SPEC.md), [plan](tasks/plan.md), and [task status](tasks/todo.md). No environment configuration has been published by this implementation.
