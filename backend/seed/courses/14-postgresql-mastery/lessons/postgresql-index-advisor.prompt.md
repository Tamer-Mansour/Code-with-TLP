# Index Selection Advisor

PostgreSQL supports multiple index types, each optimised for different data characteristics and query patterns. Choosing the wrong index type results in either no index usage or unnecessary overhead.

## Problem

Given a description of a column's data type and query pattern, determine the optimal PostgreSQL index type.

**Rules:**
- `BTREE`: equality and range queries on scalar types (integers, text, dates) — the default index type
- `GIN`: containment queries on JSONB, arrays, or full-text search (tsvector columns)
- `GIST`: geometric data, range types, or full-text search with ranking/proximity
- `BRIN`: very large tables where data is physically ordered by a column (e.g., append-only timestamp columns)
- `HASH`: equality-only queries (no range); slightly faster than B-tree for pure equality

## Input Format

- First line: integer `N` (number of queries to classify)
- Each subsequent line: `data_type query_pattern`
  - `data_type`: one of `jsonb`, `array`, `tsvector`, `timestamp_sequential`, `geometry`, `integer`, `text`
  - `query_pattern`: one of `equality`, `range`, `containment`, `fulltext`, `geometric`

## Output Format

For each query, print the recommended index type on its own line.

## Example

**Input:**
```
6
jsonb containment
timestamp_sequential range
integer equality
tsvector fulltext
geometry geometric
text range
```

**Output:**
```
GIN
BRIN
BTREE
GIN
GIST
BTREE
```

## Constraints

- `1 <= N <= 100`
- Input values are always one of the listed types and patterns
- Apply the rules exactly as described above; do not infer beyond them

## Notes

In production, `EXPLAIN (ANALYZE, BUFFERS)` tells you whether Postgres chose your index. If it did not, the cost model may prefer a sequential scan for small tables — indexes become beneficial as data grows.
