"""
Completeness — checks whether required data is present in a column
(nulls, blank strings). Assumes the column itself exists; whether the
column is present at all is a schema-conformance metric, computed in
DQProcessor, not here.
"""