"""
Importing this package registers every rule class with DQRuleBase.registry.
Adding a new dimension means: write the file, add one import line here.
Nothing in dq_engine.py, rule_factory.py, or any existing rule class needs
to change.

Note: schema conformance is NOT a rule class here — it's computed as a
metric directly in DQProcessor. See processor/dq_processor.py.
"""