# Quiz: Indexes and Query Optimization

**Q1. What data structure does InnoDB use for its default indexes?**
- [ ] Hash table
- [x] B-tree (balanced tree)
- [ ] Skip list
- [ ] Red-black tree

**Q2. In InnoDB, the primary key is also the:**
- [ ] Secondary index
- [ ] Covering index
- [x] Clustered index (rows are stored in PK order)
- [ ] Hash index

**Q3. You run `EXPLAIN SELECT * FROM orders WHERE user_id = 5`. The `type` column shows `ALL`. This means:**
- [x] MySQL is doing a full table scan — no useful index was used
- [ ] MySQL used a composite index
- [ ] MySQL used an index range scan
- [ ] The query returns all columns

**Q4. Which of these correctly creates a composite index on `(last_name, first_name)`?**
- [ ] `CREATE INDEX ON users (last_name), (first_name);`
- [x] `CREATE INDEX ix_users_name ON users (last_name, first_name);`
- [ ] `CREATE COMPOSITE INDEX ix ON users.last_name, users.first_name;`
- [ ] `ALTER TABLE users INDEX (last_name, first_name);`

**Q5. You add an index to every column in a 10-million-row table. What is the main downside?**
- [ ] SELECT queries become slower
- [x] INSERT, UPDATE, and DELETE operations become slower because each index must be maintained
- [ ] The primary key stops working
- [ ] MySQL ignores indexes on large tables

**Q6. A covering index is one that:**
- [ ] Covers the entire table with a single index
- [x] Contains all columns needed by a query so MySQL can answer it from the index alone, without reading table rows
- [ ] Is used automatically for all queries
- [ ] Only works on VARCHAR columns

**Q7. Which EXPLAIN column tells you roughly how many rows MySQL expects to examine?**
- [ ] `type`
- [ ] `key`
- [x] `rows`
- [ ] `Extra`

**Q8. An index on `(status, created_at)` can efficiently answer which query?**
- [x] `WHERE status = 'active' AND created_at > '2025-01-01'`
- [ ] `WHERE created_at > '2025-01-01'` (without filtering on status)
- [ ] `WHERE created_at > '2025-01-01' AND status = 'active'` only in that exact column order in the query
- [ ] Both A and C are correct
