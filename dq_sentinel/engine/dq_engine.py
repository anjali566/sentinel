"""
DQEngine — the fact producer.

Reads the rule config (column -> {rule class -> method + params}) and, for
every configured (column, class, method) triple, resolves the class via
RuleFactory and dynamically dispatches the method via DQRuleBase.execute().

Returns raw DQ facts only: a boolean pass/fail mask per check, per column.
Computes nothing else — no counts, no rates, no schema comparison. That's
entirely DQProcessor's job. Called directly by runners/engine_stage.py,
not by DQProcessor (see ADR-002 and the Phase 1 two-stage revision).
"""