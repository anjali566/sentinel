"""
Defines DQRuleBase, the parent class every DQ dimension inherits from.

Two responsibilities live here, and only these two:
  1. Self-registration — __init_subclass__ automatically adds every subclass
     to a shared registry, keyed by class name, the moment it's defined.
  2. Dynamic dispatch — execute() resolves a rule method by string name via
     getattr() and calls it, so the engine never hardcodes which method
     belongs to which class.

This file carries zero domain logic — that lives entirely in the
subclasses under rules/.
"""