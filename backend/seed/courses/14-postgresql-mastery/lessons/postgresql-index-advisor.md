# Exercise: Index Selection Advisor

Practice matching PostgreSQL index types to query patterns and data characteristics.

## Background

PostgreSQL ships with five index types, and picking the right one for a workload has a significant impact on query performance. The default `CREATE INDEX` creates a B-tree; other types must be specified explicitly.

```sql
-- B-tree (default) — range and equality on scalars
CREATE INDEX ON orders (created_at);

-- GIN — containment on JSONB or arrays
CREATE INDEX ON products USING GIN (tags);
CREATE INDEX ON documents USING GIN (to_tsvector('english', body));

-- GiST — geometric or proximity-aware
CREATE INDEX ON locations USING GIST (coords);

-- BRIN — very large, physically ordered tables
CREATE INDEX ON events USING BRIN (created_at);

-- Hash — pure equality, no range
CREATE INDEX ON sessions USING HASH (token);
```

## Decision Guide

| Data type | Query pattern | Recommended |
|---|---|---|
| `integer`, `text`, `date` | equality or range | BTREE |
| `jsonb`, `array` | containment (`@>`, `?`) | GIN |
| `tsvector` | full-text (`@@`) | GIN (fast lookup) or GIST (ranking) |
| `geometry`, range types | spatial / bounding-box | GIST |
| append-only timestamp on a huge table | range | BRIN |
| any scalar | equality only, very hot | HASH |

## Key Distinctions

**GIN vs GiST for full-text search:** Both work, but GIN is faster for lookups on mostly-read workloads, while GiST supports ranking-aware proximity operators (`<->`) and is smaller to build. If your queries need `ts_rank` and proximity, lean toward GiST; for plain `@@` matching at scale, use GIN.

**BRIN trade-off:** BRIN stores only min/max per block range, so it is extremely compact but only helps when the indexed column is physically correlated with the heap order. A randomly ordered column will see BRIN ignore many blocks and fall back to a full scan.

## Reference

- [Use The Index, Luke — Index Types](https://use-the-index-luke.com/) — B-tree anatomy and when non-B-tree indexes shine
- [PostgreSQL Official Documentation — Index Types](https://www.postgresql.org/docs/current/indexes-types.html)

## Your Task

For each row in the input, apply the rules to output the correct index type. See the prompt for the full specification.
