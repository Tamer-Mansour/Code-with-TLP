# B-tree, GIN, GiST, BRIN

Postgres has five general-purpose index types. Picking the right one is half the optimization battle.

## B-tree (default)

What you get with `CREATE INDEX ix_foo ON t (col)`. Ordered tree, supports `=`, `<`, `>`, `BETWEEN`, `IN`, `IS NULL`, `LIKE 'prefix%'`, and `ORDER BY`.

Use for: most columns. **Default choice.**

## Hash

```sql
CREATE INDEX ix_foo_h ON t USING hash (col);
```

Only supports `=`. Slightly smaller than B-tree for `=`. Rarely worth using — B-tree is almost as fast and far more flexible.

## GIN — Generalized Inverted

Maps each "term" (word, array element, JSONB key/value) to the list of rows that contain it.

Use for:
- JSONB containment and key queries.
- `tsvector` (full-text search).
- Array containment (`arr @> ARRAY[1,2]`).
- Trigram search via `pg_trgm`.

```sql
CREATE INDEX ix_docs_tsv ON docs USING gin (to_tsvector('english', body));
CREATE INDEX ix_orders_tags ON orders USING gin (tags);    -- tags is text[]
```

Pros: extremely fast for "find rows containing X". Cons: large; expensive to maintain on heavy writes (mitigated by `fastupdate`).

## GiST — Generalized Search Tree

A pluggable index framework. Use for:
- **Geometry / Geography** (PostGIS).
- **Range types** — `tstzrange`, `int4range`.
- **Exclusion constraints** ("no two reservations may overlap").

```sql
CREATE INDEX ix_meetings ON meetings USING gist (time_range);
ALTER TABLE meetings
  ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (room WITH =, time_range WITH &&);
```

The exclusion constraint above prevents two rows from sharing a room and an overlapping time range — atomic, in-database scheduling conflict detection.

## SP-GiST

Specialized variant for partitioned data: prefix trees, k-d trees. Niche but useful for hierarchical or geographic data.

## BRIN — Block Range Index

Tiny indexes for **append-only, naturally-ordered** data (timestamps, sequence IDs):

```sql
CREATE INDEX ix_logs_ts ON logs USING brin (ts);
```

Stores one entry per block range (default 128 pages). On a billion-row log table it might be **megabytes** vs gigabytes for a B-tree, while still letting time-range queries skip irrelevant pages.

Use when: the column is correlated with physical order. Don't use on random / UUID columns.

## Partial indexes

A B-tree (or any type) that only covers some rows:

```sql
CREATE INDEX ix_orders_pending ON orders (created_at) WHERE status = 'pending';
```

Smaller and faster than a full index when most queries hit a small subset.

## Expression indexes

Index a computed value:

```sql
CREATE INDEX ix_users_email_lower ON users ((LOWER(email)));
SELECT * FROM users WHERE LOWER(email) = LOWER('a@b.com');
```

The query must use the *same* expression for the index to apply.

## Multicolumn vs multiple indexes

- A composite `(a, b, c)` can serve queries on `a`, `(a,b)`, `(a,b,c)`. Leftmost-prefix rule.
- Two separate indexes on `a` and `b` can be combined by the planner via **bitmap heap scan** — sometimes faster, sometimes not.

If your top queries always filter both columns together, prefer a composite.

## A decision shortcut

| Workload                         | Index type        |
|----------------------------------|-------------------|
| Most everyday columns            | B-tree            |
| JSONB or array search            | GIN               |
| Full-text search                 | GIN on tsvector   |
| Geometric / spatial              | GiST              |
| Range types with overlap rules   | GiST + EXCLUDE    |
| Append-only time-series          | BRIN              |
| Often filter on `LOWER(col)`     | B-tree expression |
| Tiny "live" subset of big table  | Partial           |
