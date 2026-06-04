# Quiz: Schema Design and Partitioning

**Q1. You need to delete all events older than 30 days from a 2-billion-row table. The table is partitioned by month. What is the most efficient approach?**
- [ ] `DELETE FROM events WHERE created_at < now() - interval '30 days'`
- [x] `DROP TABLE events_YYYY_MM` for the old partition(s)
- [ ] `TRUNCATE events WHERE created_at < now() - interval '30 days'`
- [ ] Run `VACUUM FULL` to compact the table after deletion

**Q2. Which partition strategy is best for distributing rows of a `user_id` column evenly when `user_id` has no natural ordering or grouping?**
- [ ] RANGE on `user_id`
- [ ] LIST on `user_id`
- [x] HASH on `user_id`
- [ ] BRIN-based partitioning

**Q3. Partition pruning requires:**
- [ ] A GIN index on the partition key column
- [x] The partition key column to appear in the query's `WHERE` clause
- [ ] The `enable_partition_pruning` GUC to be set to `on` (it defaults to `off`)
- [ ] All partitions to be on separate tablespaces

**Q4. You add a `UNIQUE` constraint to a declarative partitioned table. Which column must the constraint include?**
- [ ] Any column — unique constraints work the same as on regular tables
- [ ] The primary key column only
- [x] The partition key column — Postgres cannot enforce global uniqueness without it
- [ ] There must be no partition key column in the unique constraint

**Q5. A "soft delete" pattern uses a `deleted_at timestamptz` column instead of actually removing rows. What index optimises a query that always filters `WHERE deleted_at IS NULL`?**
- [ ] A B-tree index on `deleted_at`
- [x] A partial index: `CREATE INDEX ON items (id) WHERE deleted_at IS NULL`
- [ ] A GIN index on `deleted_at`
- [ ] No index — `IS NULL` cannot be indexed in Postgres

**Q6. What is the key difference between declarative partitioning and inheritance-based partitioning in Postgres?**
- [ ] Declarative partitioning supports `RANGE` only; inheritance supports all strategies
- [x] Declarative partitioning has built-in partition pruning, automatic routing of inserts, and better planner support; inheritance requires manual maintenance
- [ ] Inheritance-based partitioning is the recommended approach since Postgres 10
- [ ] They are identical; "declarative" is just a synonym for inheritance in Postgres documentation
