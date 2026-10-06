"""
RuleFactory — resolves a rule class instance purely from its string name.

Given a class name from config (e.g. "Completeness"), looks it up in
DQRuleBase.registry and returns a ready-to-use instance. The single point
of translation between "a string in a config file" and "a live Python
object" — nothing else in the codebase instantiates a rule class directly.
"""

from dq_sentinel.engine.base import DQRuleBase


class DQRuleFactory:
    @staticmethod
    def get_rule_instance(rule: str):
        rule_cls = DQRuleBase.registry.get(rule)
        if rule_cls is None:
            available = ", ".join(sorted(DQRuleBase.registry.keys()))
            raise ValueError(
                f"Unknown DQ rule class: '{rule}'. Available classes: {available}"
            )
        return rule_cls()