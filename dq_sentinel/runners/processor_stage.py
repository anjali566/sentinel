"""
processor_stage — second pipeline stage: load facts -> run DQProcessor ->
save metrics.

Normally receives facts directly in-memory from engine_stage within the
same DQRunner.run() call. Can also reload previously-saved facts from the
dq_facts collection by run_id, to support recomputing metrics alone (e.g.
after changing how dq_score is weighted) without re-fetching data or
re-running rule checks.

Saves its output to the dq_results collection via the source's
save_metrics().
"""