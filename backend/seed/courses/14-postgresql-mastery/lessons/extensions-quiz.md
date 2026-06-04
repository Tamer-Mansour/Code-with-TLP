# Quiz: Extensions and Ecosystem

**Q1. You want to find the top 10 slowest queries executed on your Postgres instance over the past hour. Which extension provides this data?**
- [ ] `pg_trgm`
- [ ] `pgcrypto`
- [x] `pg_stat_statements`
- [ ] `uuid-ossp`

**Q2. `pg_trgm` enables which type of query?**
- [ ] Geospatial bounding-box lookups
- [x] Fuzzy text search using trigram similarity (e.g., `LIKE '%foo%'` with an index, or `%` operator)
- [ ] Full-text search using `tsvector` and `tsquery`
- [ ] Encrypted storage of sensitive columns

**Q3. The `gen_random_uuid()` function is available without any extension in Postgres:**
- [x] True — it is built into Postgres 13+ core via `pgcrypto`-compatible functions; `uuid-ossp` is only needed for older versions or `uuid_generate_v1()`
- [ ] False — you must always install `uuid-ossp` to generate UUIDs
- [ ] False — UUID generation requires the `pgcrypto` extension to be explicitly installed
- [ ] True — but only if the `pg_stat_statements` extension is also loaded

**Q4. A Foreign Data Wrapper (FDW) created with `postgres_fdw` lets you:**
- [ ] Share indexes between two tables in the same database
- [x] Query tables in a remote PostgreSQL database as if they were local tables
- [ ] Automatically replicate writes to a secondary Postgres instance
- [ ] Cache results of expensive queries in a foreign memory store

**Q5. PostGIS adds which capability to PostgreSQL?**
- [ ] Time-series compression for numerical sensor data
- [ ] Full-text search in over 50 languages
- [x] Geospatial data types (geometry, geography), spatial indexes, and functions for distance, intersection, and coordinate transforms
- [ ] Column-level encryption for GDPR compliance

**Q6. To reset accumulated statistics in `pg_stat_statements`, you run:**
- [ ] `DROP EXTENSION pg_stat_statements CASCADE;`
- [ ] `VACUUM ANALYZE;`
- [x] `SELECT pg_stat_statements_reset();`
- [ ] `ALTER SYSTEM RESET pg_stat_statements.max;`
