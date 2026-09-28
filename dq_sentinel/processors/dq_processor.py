"""
DQProcessor — the metric computer. A pure function of (facts, df, config)
-> metrics; it does not fetch data, does not run DQEngine itself, and does
not persist anything.

Computes two kinds of output:
  - per-check metrics: rows checked/passed/failed, pass rate, status —
    derived from the boolean masks in `facts`
  - dataset-level metrics: total rows, duplicate rows, checks passed/
    failed, a composite dq_score, execution time, AND schema comparison
    (columns_expected, columns_received, missing_columns,
    unexpected_columns) — schema conformance is reported here as a metric,
    not as a separate rule class with its own pass/fail status

Called by runners/processor_stage.py, which supplies the facts (either
freshly produced by engine_stage in the same run, or reloaded from the
dq_facts collection for a standalone metrics-only recompute).
"""