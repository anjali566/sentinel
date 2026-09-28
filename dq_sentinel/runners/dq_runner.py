"""
DQRunner — composes engine_stage and processor_stage for the common case
of "run the full pipeline for one source." Owns no rule-evaluation or
metric-computation logic itself; only sequences the two stages and passes
data between them. The single entry point MultiSourceRunner calls per
source.
"""