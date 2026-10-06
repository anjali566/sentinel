# dq_sentinel — A Configurable Data Quality Governance Platform

> A factory-pattern, SOLID-compliant data quality engine for trading-venue order-event feeds. Config-driven at every layer — no hardcoded rule classes, no hardcoded columns. Built as a hands-on alternative to tools like Great Expectations, to demonstrate the underlying engineering rather than just tool configuration.

---

## Table of Contents
- [Overview](#overview)
- [Requirements (as gathered)](#requirements-as-gathered)
- [Architecture Decisions](#architecture-decisions)
- [Phase 1 Architecture (current)](#phase-1-architecture-current)
- [Data Quality Dimensions Covered](#data-quality-dimensions-covered)
- [Folder Structure](#folder-structure)
- [How Configuration Works](#how-configuration-works)
- [Flow of Control](#flow-of-control)
- [Tech Stack](#tech-stack)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

dq_sentinel checks the quality of order-event data arriving from multiple trading venues, all conforming to a shared SLA-defined schema. It dynamically applies configured rules per column via a self-registering factory pattern, stores results in MongoDB, and surfaces them on a Plotly dashboard.

Built from real banking/FinTech ETL experience, and deliberately engineered rather than wrapped around an existing vendor tool — every design decision below was made explicitly, with trade-offs considered, rather than defaulted into.

## Requirements (as gathered)

**Functional:**
- Ingest order-event data from multiple trading venues, all sharing one SLA-defined schema
- Run configurable data quality checks across multiple dimensions
- Store results
- Visualize results on a dashboard

**Non-functional / clarified through requirement-gathering:**
- Schema deviations must be explicitly flagged as a DQ check, not just noted incidentally — the SLA schema is a *contract*
- New rule classes/dimensions must be addable with zero impact on existing code (Open/Closed)
- Phase 1 scope: manual trigger, MongoDB as both source and results store (a **walking skeleton** — prove the architecture end-to-end before adding automation)
- Continuous, near-real-time ingestion is a real future requirement, deferred to Phase 2 rather than built now, since it will most likely be subsumed by an orchestrator (Airflow) rather than a bespoke file-watcher

## Architecture Decisions

A lightweight ADR (Architecture Decision Record) log — the trade-offs considered and why each choice was made. See `docs/architecture_decisions.md` for the full write-up.

| Decision | Choice | Why |
|---|---|---|
| Direct-read vs. staged/snapshot | Staged (satisfied by construction) | A manually-populated Mongo DB in Phase 1 already acts as a stable snapshot — no live-write contention, fully reproducible |
| Schema handling | First-class `SchemaConformance` rule class (own file in `rules/`) | Schema is an SLA contract, checked once per dataset — not per-column like `Completeness`, and not folded into it, to keep the engine's per-column dispatch clean |
| Trigger mechanism | Manual (Phase 1) → Airflow (Phase 2) | Avoids building a custom watcher that would be replaced almost immediately once Airflow is introduced |
| Rule dispatch | Factory pattern + dynamic `getattr` dispatch | Zero hardcoding; new dimensions require no engine changes (Open/Closed, Dependency Inversion) |
| Facts vs. metrics | Split across `dq_engine.py` (facts) and `dq_processor.py` (metrics) | Keeps rule evaluation and metric computation independently testable and swappable |

## Phase 1 Architecture (current)

```
Data generator (manual, per SLA schema)
        │
        ▼
   MongoDB (source) ── acts as the snapshot
        │
        ▼
  Runner (manually invoked, one or more sources)
        │
        ▼
  Engine (facts) → Processor (metrics)
        │
        ▼
  MongoDB (results collection)
        │
        ▼
  Dashboard (Plotly, on demand)
```

Phase 2 replaces only the top of this chain (manual trigger → Airflow-scheduled/sensed trigger); everything from the Runner down is unchanged.

## Data Quality Dimensions Covered

| Dimension | Description | Status |
|---|---|---|
| Completeness | Missing values, null checks | ✅ |
| Uniqueness | Duplicate detection | ✅ |
| Validity | Format/range/enum conformance | ✅ |
| Accuracy | Value correctness against expected type/pattern | ✅ |
| Timeliness | Data freshness / latency vs SLA | ✅ |
| Integrity | Referential integrity against reference data | ✅ |
| Consistency | Cross-field agreement within a row | ✅ |

*(✅ = built and demoed with a synthetic dataset; ⬜ = designed, not yet built)*

## Folder Structure

```
 sentinel/                              <- repo root
├── README.md
├── pyproject.toml
├── .env.example                       <- NEW: template for Mongo connection details
├── .gitignore                         <- NEW: excludes .env, __pycache__, venv/
│
├── docs/
│   └── architecture_decisions.md
│
├── configs/
│   ├── schema/
│   │   └── order_schema.yaml          <- the SLA contract
│   └── rules/
│       └── source1.yaml               <- per-column DQ rules
│
├── data_generator/
│   └── generate_sample_data.py        <- writes synthetic data straight into MongoDB
│
├── dashboard/
│   └── app.py                         <- Plotly, reads from MongoDB
│
└── dq_sentinel/
    ├── __init__.py
    │
    ├── engine/
    │   ├── __init__.py
    │   ├── base.py                    # DQDimensionBase
    │   ├── rule_factory.py            # DQDimensionFactory
    │   └── dq_engine.py               # DQEngine — produces raw facts
    │
    ├── processor/
    │   ├── __init__.py
    │   └── dq_processor.py            # DQProcessor — facts -> metrics
    │
    ├── rules/
    │   ├── __init__.py
    │   ├── completeness.py
    │   ├── uniqueness.py
    │   ├── validity.py
    │   ├── accuracy.py
    │   ├── timeliness.py
    │   ├── integrity.py
    │   └── consistency.py
    │
    ├── runners/
    │   ├── __init__.py
    │   ├── dq_runner.py               # composes both stages
    │   ├── multi_source_runner.py
    │   ├── engine_stage.py            # fetch -> DQEngine -> save facts
    │   └── processor_stage.py         # load facts -> DQProcessor -> save metrics
    │
    └── sources/
        ├── __init__.py
        ├── mongo_source.py            # <- THE MONGODB PART
        └── filesystem_source.py       # Phase 2 (reserved)
```

## How Configuration Works

Two separate config concerns, deliberately not merged:

**Schema contract** (`configs/schema/order_schema.yaml`) — what shape the data must be:
```yaml
columns:
  order_id: { type: string, nullable: false }
  price: { type: float, nullable: true }
  # ...
```

**Rule config** (`configs/rules/source1.yaml`) — what quality rules apply, given the shape is correct:
```yaml
price:
  Validity:
    rule: isInRange
    params: { min_val: 0, max_val: 1000000 }
```

## Flow of Control

1. Data generator writes sample order-event data to MongoDB, matching the SLA schema
2. Runner is invoked manually for one or more sources
3. Runner fetches data via `MongoDataSource`
4. Engine evaluates every (column, rule) pair from config, dynamically resolved via the factory — produces raw pass/fail facts
5. Processor consumes those facts, computes per-check and dataset-level metrics
6. Processor's output is written back to MongoDB via the result sink
7. Dashboard reads the results collection and renders dimension scores, trends, and drill-downs — on demand

## Tech Stack

- **Python** — core engine
- **MongoDB** — source data (Phase 1) + results storage
- **Plotly** — dashboard visualizations
- **Apache Airflow** *(Phase 2)* — replaces manual triggering
- **Docker** *(Phase 2)* — packaging for "plug and play" use

## Roadmap

**Phase 1 — Walking skeleton (current)**
- [ ] `SchemaConformance` rule class
- [ ] `MongoDataSource` (fetch + save results)
- [ ] Manual data generator matching the SLA schema
- [ ] Manually-invoked Runner, single and multi-source
- [ ] Plotly dashboard (v1: radar chart + drill-down table)

**Phase 2 — Automation**
- [ ] Airflow DAG replaces manual triggering (sensors/schedule — no bespoke watcher)
- [ ] `FileSystemDataSource` activated for folder-arrival ingestion
- [ ] Docker packaging

**Phase 3 — Stretch**
- [ ] Volume anomaly detection (surge/drop vs. historical baseline)
- [ ] Group-scope checks (order lifecycle integrity, sequence gap detection)
- [ ] Cross-venue clock synchronization check

## License
<!-- TODO -->