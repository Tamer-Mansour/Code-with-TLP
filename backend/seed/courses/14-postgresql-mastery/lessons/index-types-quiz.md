# Quiz: PostgreSQL Index Types

**Q1. Which index type does Postgres use by default when you run `CREATE INDEX`?**
- [ ] GIN
- [ ] GiST
- [x] B-tree
- [ ] BRIN

**Q2. You have a `tags text[]` array column and need to find rows where the array contains a specific tag efficiently. Which index type is most appropriate?**
- [ ] B-tree
- [x] GIN
- [ ] BRIN
- [ ] Hash

**Q3. A table stores sensor readings for 10,000 physical sensors, inserted in timestamp order. Each query filters by a range of timestamps. The table has 500 million rows. Which index minimises storage while still accelerating range scans?**
- [ ] GIN
- [ ] B-tree on each sensor_id
- [x] BRIN
- [ ] GiST

**Q4. You create a GiST index on a `geometry` column using PostGIS. What kind of queries does it accelerate?**
- [ ] Equality lookups on text
- [x] Nearest-neighbor and bounding-box spatial queries
- [ ] Full-text search
- [ ] Sorting large result sets

**Q5. A partial index is defined as:**
```sql
CREATE INDEX ix_orders_unpaid ON orders (customer_id)
WHERE status = 'unpaid';
```
Which statement is TRUE?
- [ ] The index contains all rows; the WHERE clause is just a hint.
- [x] The index only stores rows where `status = 'unpaid'`, making it smaller and faster for that filter.
- [ ] Partial indexes cannot be used with WHERE clauses in queries.
- [ ] This syntax is invalid in PostgreSQL.

**Q6. An index-only scan is possible when:**
- [ ] The index is a GIN index.
- [ ] There are no `NULL` values in the indexed column.
- [x] All columns requested by the query are included in the index, and the visibility map shows the page is all-visible.
- [ ] The table has fewer than 1,000 rows.
