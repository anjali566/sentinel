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


import pandas as pd
from dq_sentinel.engine.dimension_factory import DQDimensionFactory


class DQEngine:
    def __init__(self, config: dict, df: pd.DataFrame):
        self.config = config
        self.df = df

    def run(self) -> dict:
        """
        Returns raw facts, keyed by check_id:

            {
              "<column>_<method>_check": {
                  "column": str,
                  "dimension": str,
                  "rule": str,
                  "mask": pd.Series[bool] | None,   # None only on a missing-column error
                  "error": str | None,               # set only when the check couldn't run
              },
              ...
            }
        """
        facts = {}

        for column, dimension_specs in self.config.items():
            if column not in self.df.columns:
                # column expected by config but missing from the data -> record the
                # fact that the check couldn't run, don't silently skip or crash
                for dimension, spec in dimension_specs.items():
                    rule, _ = self._parse_spec(spec)
                    check_id = f"check_{column}_{rule}".lower()
                    facts[check_id] = self._missing_column_fact(column, dimension, rule)
                continue

            for dimension, spec in dimension_specs.items():
                rule, params = self._parse_spec(spec)
                params = self._resolve_column_params(params)

                instance = DQDimensionFactory.get_dimension_instance(dimension)
                mask = instance.execute(rule, self.df[column], **params)

                check_id = f"check_{column}_{rule}".lower()
                facts[check_id] = {
                    "column": column,
                    "dimension": dimension,
                    "rule": rule,
                    "mask": mask,
                    "error": None,
                }

        return facts

    def _resolve_column_params(self, params: dict) -> dict:
        """
        Lets config reference another column by name (e.g. for Consistency checks)
        via `compare_column`, which the engine resolves into an actual Series
        before calling the rule method.
        """
        params = dict(params)
        # TODO: Validate and handle compare_column
        # if "compare_column" in params:l;
        #     compare_col = params.pop("compare_column")
        #     params["compare_series"] = self.df[compare_col]
        return params

    def _missing_column_fact(self, column, dimension, rule) -> dict:
        return {
            "column": column,
            "dimension": dimension,
            "rule": rule,
            "mask": None,
            "error": "column_missing_from_dataset",
        }

    @staticmethod
    def _parse_spec(spec):
        if isinstance(spec, str):
            return spec, {}
        return spec["rule"], spec.get("params", {})