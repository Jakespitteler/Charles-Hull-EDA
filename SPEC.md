# Charles Hull EDA — V1 specification

Status: scope and initial slice approved by the user on 17 November 2026. Windows/macOS, uv, VS Code, Python/openpyxl/pandas, and a thin report notebook are agreed. The user approved implementation with Python >=3.13; Plotly is the initial chart library.

## Objective

Create a reproducible local workflow that reads the example report without modifying it, produces auditable analytical tables and a data-quality report, and supports a first descriptive EDA on the user's real workbook. Turn emerging patterns into questions and evidence requests for Charles Hull and Talison.

V1 is one end-to-end exploratory workflow, not a dashboard or optimisation system. Success includes establishing that some questions cannot yet be answered.

Intent: [confirmed statement](docs/intent/charles-hull-eda.md).

## Observed workbook structure

Read-only inspection of the supplied dummy workbook found 21 visible sheets:

- Seven daily reports and a Weekly Summary, with heavily merged cells.
- Five production graph sheets containing daily and monthly forecast/actual series.
- ROM Stockpile and $ Forecast.
- Fuel Usage, Fuel Usage (OLD), Fuel Graph, and Water Usage.
- Equipment List and Lists.

Sheet names can have trailing spaces. Tables have different header positions, orientations, grains, and time coverage. A filename's week is not the full extent of the historical data. Some rows/columns are totals, derived values, future dates, or template placeholders.

Daily reports include safety counts, weather, staffing counts, production movements, equipment day/night hours, delay reasons, and narrative comments. Personnel names can occur in leave/signature fields; omit them from analytical tables by default.

### Concrete validation cases

- Monday G52 is `=SUM(B51+E52)` while its row's shift hours are B52 and E52. Flag the cross-row reference; retain the supplied total and a separately computed shift sum.
- Monday G61 sums G51:G58, while the listed equipment continues through row 60. Check scope even if excluded rows currently contain zero.
- Production volumes can be formula-derived from load counts (for example, loads multiplied by 32). These are not necessarily independent volume measurements.
- Formula cells inspected have cached values, but their presence does not prove freshness. Python readers do not calculate Excel formulas.

These are example-workbook observations; no claim is made about real company reports or performance.

## Technical approach

- Python, with openpyxl for cell/formula/provenance extraction and pandas for analytical tables.
- Reusable importable modules contain extraction, validation, aggregation, and chart construction. The VS Code Jupyter notebook is a thin report front end: configuration, calls, narrative, and displayed results. It runs top to bottom without hidden state.
- Proposed: Plotly as the initial chart library for hover details and interactive exploration; add matplotlib/seaborn only if a concrete static/publication requirement warrants them. HTML exports embed data and stay local. No image-export dependency initially.
- Windows is the primary user platform; macOS must also be supported. Use uv for environment management and a committed lockfile, pathlib for paths, and platform-neutral Python entry points. Python >=3.13 is required; `.python-version` selects 3.13.
- pytest for meaningful extraction and reconciliation checks. Use ipykernel for VS Code notebook execution; specify exact dependency versions through uv.lock during implementation.
- Start with daily reports and reconciliation against Weekly Summary. Inventory every sheet, but bring historical production/fuel/water tables into analysis only after their definitions and time coverage are understood.

This initial scope makes the first result reviewable without treating all sheets as one clean dataset.

## Proposed data model and cleaning rules — approval required

- Separate tables by grain: production movement per date/route/unit; equipment per date/asset/shift; staffing counts per date/category; daily safety and weather observations; validation issues.
- Preserve file hash, sheet, cell or row reference, source label, raw value, parsed value, and relevant formula references. Keep original inputs immutable.
- Preserve reported, calculated, and reconciled values separately. Never silently replace a reported total.
- Distinguish blank, explicit zero, not applicable, unparseable, and formula-derived zero. Avoid global missing-value filling or automatic imputation.
- Preserve tonnes, m3, and bcm as distinct units. No mass/volume or loose/bank conversion without validated factors and definitions.
- Do not infer downtime duration from a reason label or infer utilisation from operating hours without scheduled/available hours.
- Parse sheet dates explicitly and flag inconsistencies with weekdays, report period, or historical series. Record local timezone/shift boundaries before any weather join.
- Map assets and work descriptions through reviewable mappings. Do not fuzzy-merge equipment identities automatically.
- Retain outliers with flags. Do not delete unusual observations just because they are extreme.
- Use weekly summaries as reconciliation targets, not additional observations. Do not concatenate overlapping historical tables or the OLD/current fuel tabs without a source-precedence rule.
- Omit names, signatures, leave details, and unrestricted narrative text from default exports. Local narratives may be useful later under an agreed handling approach.

## Proposed outputs

1. Workbook inventory: tables, date coverage, units, formulas, and extraction status, including unsupported regions.
2. Tidy tables with provenance, plus a data dictionary recording known and unresolved meanings.
3. Validation report separating extraction failures, missing information, reconciliation mismatches, and interpretive warnings.
4. Re-runnable EDA notebook with coverage/missingness, production by route and unit, equipment hours by shift, and reported delays. Add valid comparisons only where units, scope, and denominators agree.
5. Findings register: observation, evidence, alternative explanations, possible operational consequence, confidence, next team question, and additional data needed. Label synthetic demonstrations prominently.

Default exports must remain local and excluded from version control. Shareable summaries require user review; dummy data is not proof that every identifying field has been removed.

## Analysis strategy

Begin with measurement validity and coverage. Establish the process meaning of each quantity before interpreting variability. For real data, distinguish planned work, shutdowns, work mix, and reporting effects from unexplained changes.

Daily asset hours can be explored descriptively, but route productivity needs a valid mapping between assets, hours, and that route. Aggregate staff counts do not establish labour hours. Fuel issued may differ from fuel consumed. Water use does not alone establish water scarcity. Safety activity counts lack the exposure and context required for risk comparisons.

One week gives at most seven daily observations for the daily-report section. Avoid significance hunting, complex predictive models, and causal claims. Historical tabs may offer more observations, subject to verification of provenance and completeness.

For promising signals, ask what downstream outcome would change if the issue improved. Estimate value only with defensible cost, throughput, quality, or delay information. Record safety implications and whether the apparent constraint could move elsewhere.

Weather enrichment is deferred until actual dates/site and a mechanism are confirmed. Consider onsite versus public observations, station distance/elevation, missingness, shift alignment, antecedent rainfall, and confounding by material, route, maintenance, and staffing. Dummy dates must not be joined to weather and interpreted operationally.

## Commands and project structure

Inventory and equipment-only analysis commands below are implemented. Dependencies are locked in uv.lock; tests and dummy-workbook execution have been validated on Linux/Python 3.13.18. Full V1 analysis, Windows/macOS validation, and real-data checks remain pending.

From the repository root, on Windows or macOS:

```text
uv sync --locked
uv run python -m charles_hull_eda inspect --input "<path-to-report.xlsx>" --output "outputs/inspection"
uv run python -m charles_hull_eda analyse --input "<path-to-report.xlsx>" --output "outputs/first-pass"
uv run pytest
```

Use VS Code's notebook kernel picker to select the uv-managed `.venv`. The notebook accepts an explicit input path; it must not depend on the attachment path in this cloud machine. Notebook automation and lint tooling will be proposed if needed rather than added implicitly.

Proposed structure: `src/charles_hull_eda/` for reusable extraction/validation; `notebooks/` for exploration; `tests/` for targeted checks; `docs/` for definitions, findings, and interview notes. Raw data and generated outputs live in an agreed ignored local location or outside the checkout.

## Code conventions and testing

Proposed conventions: explicit units, snake_case names, typed function boundaries, no notebook-only parsing logic, and no hidden mutation of input tables. There is no existing application code from which to derive a style example; agree that convention with the first implementation slice.

Verify selected cell-to-record mappings against the dummy workbook; verify formula mismatch detection, merged-header handling, blank versus zero preservation, mixed units, duplicate detection, and exclusion of summary rows. Test repeat runs for deterministic tables. Do not use dummy distributions to set production thresholds. No arbitrary coverage target is proposed.

The user validates execution and sampled results on real data. Keep that verification distinct from tests in this environment.

## Boundaries

- Always: preserve source files, record cleaning decisions and evidence, surface assumptions, and label unresolved interpretations.
- Discuss before implementation: dependencies/runtime, model/grain, cleaning policies, analytical methods, exports, new data sources, and changes in scope.
- Never: commit real reports or personal information, silently repair source data, equate missing with zero, or present dummy-data patterns as business findings.

## Acceptance criteria

- The original workbook remains byte-for-byte unchanged.
- All 21 sheets are inventoried; selected regions are extracted or explicitly marked unsupported.
- Selected records can be traced to source cells, and extracted samples agree with those cells.
- Known example formula/scope issues are surfaced without overwriting reported figures.
- Blanks/zeros, mixed units, summaries, duplicate records, and unmatched identifiers are handled transparently.
- A clean restart runs the agreed workflow and produces the same analytical tables from the same input.
- Outputs distinguish data-quality observations, synthetic demonstrations, and findings validated on real data.
- Team questions emerge from observed gaps/signals, without requiring an optimisation opportunity to exist.

## Deferred

Public weather ingestion; multi-workbook deduplication; OCR/Take 5 automation; dashboards; predictive modelling; optimisation algorithms; cost-benefit estimates without necessary inputs; company-wide conclusions from a single site report. Revisit as evidence and data arrive.

## Decisions and open questions

Agreed: Windows with macOS compatibility, uv in VS Code, reusable Python modules with a thin report notebook, and daily-report extraction/weekly reconciliation before historical table analysis.

Approved implementation baseline: Python >=3.13, Plotly, CLI entry points above, and ignored local data/output directories. The notebook is a report front end. Review the first equipment slice before extending extraction to other sections.

Operational definitions (e.g. loads, BCM, scheduled hours, fuel units, and report completion status) can be investigated alongside development rather than guessed.
