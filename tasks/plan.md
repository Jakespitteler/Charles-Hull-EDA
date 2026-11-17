# Implementation plan: first workbook EDA slice

Status: approved with Python >=3.13. Steps 1–3 implemented; first user review checkpoint pending.
Source: [SPEC.md](../SPEC.md). Tasks: [todo.md](todo.md).

## Deliverable

A local, uv-managed Python package that inventories the workbook, extracts the daily sections, reconciles reported totals, and feeds a thin notebook report. Test on the dummy workbook; the user runs the same workflow on real data. Historical tables are inventoried but not silently combined with daily records.

## Architecture and dependency direction

`workbook reader → section extraction → validation/reconciliation → summaries/charts → CLI or notebook`

- openpyxl reads original formulas and cached values separately, without saving the input. Missing caches become issues, not invented results.
- pandas tables retain provenance and missingness semantics. A validation issue has a rule ID, severity, source reference, expected/reported values where appropriate, and explanation.
- A small orchestrator returns tables and issues to both interfaces. Neither interface owns business logic; no notebook-to-package imports.
- Plotly chart functions accept prepared tables and return figures. Charts identify units, source period, missing coverage, and synthetic status. Avoid dual axes and mixing units without a clear reason.
- uv.lock provides reproducibility. Required baseline: Python >=3.13; runtime dependencies openpyxl, pandas, plotly, ipykernel; development dependency pytest. Do not add other packages without discussion.
- Inputs can live outside the checkout. Ignore local `data/`, `outputs/`, `.venv/`, caches, and notebook checkpoints; commit notebooks without executed outputs. Never bundle the supplied workbook as a test fixture without review. Generate small synthetic workbooks in tests instead.

## Build order and checkpoints

1. Minimal workbook inspection command, locked environment, and safe local storage conventions.
2. Equipment-hours extraction and reconciliation, including the observed formula issue.
3. Thin notebook showing those tables, issues, and an interactive Plotly chart.
4. Production movement extraction and unit-safe summaries; extend the report.
5. Staffing/safety/weather counts and weekly reconciliation; extend the report.
6. Complete first-pass interpretation notes, user questions, and local execution guide.

Review with the user after steps 2–3 and 4–5. Each step is a working, tested slice. Detailed file/schema choices are presented before implementing the affected slice. Do not install the entire backlog in step 1.

## Verification

Use targeted synthetic workbook tests for extraction failure modes; read-only integration checks on the supplied dummy attachment remain local. Compare selected records directly with cells. Check source hashes before/after, repeat-run table equality, issue stability, and known mismatch detection. Keep automated checks separate from manual chart review and user execution on real data.

Linux cloud checks do not prove Windows/macOS compatibility. Design for both, then have the user verify Windows setup/kernel selection and record macOS validation as pending until actually tested. Do not claim real-data or cross-platform validation prematurely.

## Risks and mitigations

| Risk | Response |
|---|---|
| Template row positions change | Validate section labels/header signatures; stop unsupported extraction with source references rather than guessing |
| Blank inputs become formula zeros | Retain formula/raw/cache metadata; mark uncertain measurements |
| Report totals include different scopes | Reconcile explicitly by section/date/unit and flag unmatched rows |
| Unknown shift lengths/measurement definitions | Use descriptive hours/counts; defer utilisation/productivity ratios |
| Notebook shows stale results | Modules own logic; rerun from clean kernel; exclude saved outputs from Git |
| Identifier/narrative leakage | Default analytical tables exclude names/leave/signatures; unrestricted narratives need separate discussion |
| Dummy workbook suggests false patterns | Synthetic labels on report; operational findings only from real-data review |

## Deferred decisions

No public weather fetches, persistent database, bulk workbook ingestion, OCR, automated outlier deletion, optimisation solver, or publication/export service. Revisit when questions and data justify them.

## Review requested

Review the first equipment slice on real data and Windows before steps 4–6. Detailed extraction rules stay reviewable at each checkpoint.

## First-slice verification record (17 November 2026)

- Python 3.13.18; uv locked environment sync succeeded. Nine pytest tests passed with DeprecationWarning and FutureWarning treated as errors.
- All six notebook code cells executed in a fresh ipykernel using the supplied dummy workbook. The committed notebook has no saved outputs. This validates execution, not a visual review in VS Code.
- Example extraction: 21 sheets inventoried, 140 shift observations, 70 asset-day totals; 75 warnings (66 incomplete shift pairs, eight formula-scope issues, one numeric mismatch), zero extraction errors. Original file preserved.
- Interactive appearance in VS Code, Windows/macOS execution, and real-data validation await user review. No business findings are inferred from the example values.

## PR preparation verification

Three additional command-line integration tests cover generated workbook exports, explicit failure for unrelated layouts, and malformed input. A temporary inversion of the shift-completeness condition was rejected by the equipment tests; the source was restored before the final suite. No uploaded workbooks or generated results are included in the PR.
