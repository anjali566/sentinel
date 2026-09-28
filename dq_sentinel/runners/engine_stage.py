"""
engine_stage — first pipeline stage: fetch -> run DQEngine -> save facts.

Fetches source data via a configured data source (e.g. MongoDataSource),
runs DQEngine to produce raw facts, then serializes and saves those facts
(as failing-row identifiers per check, not full boolean masks — see
ADR log) to the dq_facts collection via the source's save_facts().

Independently callable/rerunnable — a future orchestrator can schedule
this stage on its own, separate from processor_stage.
"""