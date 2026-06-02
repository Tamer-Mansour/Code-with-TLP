# Essential PostgreSQL Extensions

PostgreSQL's extension system lets you load new data types, functions, operators, and index methods without patching the server. Most production deployments use a handful of battle-tested extensions that solve problems the core engine deliberately leaves out.

## Enabling extensions

```sql
-- List available extensions
SELECT name, default_version, comment FROM pg_available_extensions ORDER BY name;

-- Install into the current database
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Check what's installed
SELECT extname, extversion FROM pg_extension;
```

Extensions are per-database, not per-server.

## pg_stat_statements — query performance tracking

The single most important monitoring extension. It accumulates statistics for every distinct SQL query the server has executed.

```sql
CREATE EXTENSION pg_stat_statements;

-- Top 10 slowest queries by total time
SELECT
    round(total_exec_time::numeric, 2) AS total_ms,
    calls,
    round((total_exec_time / calls)::numeric, 2) AS avg_ms,
    round(rows / calls) AS avg_rows,
    left(query, 80) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

Add `pg_stat_statements` to `postgresql.conf`:

```
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
```

## uuid-ossp / pgcrypto — UUID generation

```sql
CREATE EXTENSION "uuid-ossp";

-- v4 random UUID
SELECT uuid_generate_v4();

-- v1 time-based UUID (leaks MAC address — prefer v4)
SELECT uuid_generate_v1();
```

For Postgres 13+ with `gen_random_uuid()` built in, you may not need the extension:

```sql
SELECT gen_random_uuid();   -- no extension needed
```

## pg_trgm — trigram similarity search

Enables fast LIKE/ILIKE and fuzzy text search using GIN or GiST indexes:

```sql
CREATE EXTENSION pg_trgm;

CREATE INDEX ix_products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- Fast wildcard search (even with leading wildcard)
SELECT * FROM products WHERE name ILIKE '%espresso%';

-- Similarity score
SELECT name, similarity(name, 'cofee') AS sim
FROM products
WHERE similarity(name, 'cofee') > 0.3
ORDER BY sim DESC;
```

Without `pg_trgm`, `ILIKE '%term%'` forces a sequential scan regardless of indexes.

## hstore — key-value pairs

A lightweight alternative to JSONB for flat string-to-string maps:

```sql
CREATE EXTENSION hstore;

CREATE TABLE configs (
    id   bigserial PRIMARY KEY,
    data hstore
);

INSERT INTO configs (data) VALUES ('host => localhost, port => 5432');
SELECT data -> 'host' FROM configs;
```

For new work, prefer `jsonb` — it supports nested structures and has richer operator support.

## PostGIS — geospatial data

The gold standard for spatial data in Postgres:

```sql
CREATE EXTENSION postgis;

ALTER TABLE locations ADD COLUMN geom geometry(Point, 4326);

-- Insert a point (longitude, latitude)
UPDATE locations SET geom = ST_SetSRID(ST_MakePoint(-73.9857, 40.7484), 4326) WHERE id = 1;

-- Find locations within 5 km of a point
SELECT name FROM locations
WHERE ST_DWithin(
    geom::geography,
    ST_MakePoint(-73.9857, 40.7484)::geography,
    5000   -- meters
);
```

PostGIS adds hundreds of geometry/geography functions, GiST spatial indexes, and coordinate system support.

## pg_partman — partition management

Automates creation and maintenance of time-based and serial partitions:

```sql
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
    p_parent_table => 'public.events',
    p_control      => 'created_at',
    p_type         => 'range',
    p_interval     => 'monthly'
);
```

`pg_partman` creates a background maintenance function that generates future partitions and, optionally, drops old ones according to a retention policy.

## Summary

| Extension             | Use case                                  |
|-----------------------|-------------------------------------------|
| `pg_stat_statements`  | Query performance monitoring              |
| `uuid-ossp`           | UUID generation (pre-Postgres 13)         |
| `pg_trgm`             | Fuzzy text search, fast LIKE              |
| `hstore`              | Flat key-value pairs                      |
| `PostGIS`             | Geospatial types, functions, indexes      |
| `pg_partman`          | Automated partition lifecycle management  |
| `pgcrypto`            | Cryptographic functions, password hashing |
