"""
RuleFactory — resolves a rule class instance purely from its string name.

Given a class name from config (e.g. "Completeness"), looks it up in
DQRuleBase.registry and returns a ready-to-use instance. The single point
of translation between "a string in a config file" and "a live Python
object" — nothing else in the codebase instantiates a rule class directly.
"""