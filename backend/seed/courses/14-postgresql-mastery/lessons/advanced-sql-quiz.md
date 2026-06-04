# Quiz: Advanced SQL Features

**Q1. In a recursive CTE, what terminates the recursion?**
- [ ] A `LIMIT` clause on the outer query
- [ ] The `UNION` keyword (as opposed to `UNION ALL`)
- [x] The recursive term producing zero new rows
- [ ] Reaching a maximum recursion depth set by Postgres

**Q2. What is the difference between `RANK()` and `DENSE_RANK()`?**
- [ ] `RANK()` skips ties; `DENSE_RANK()` does not count tied rows at all
- [x] `RANK()` leaves gaps after ties (1,1,3); `DENSE_RANK()` does not (1,1,2)
- [ ] They are identical; the names are aliases
- [ ] `DENSE_RANK()` partitions by an extra implicit column

**Q3. You write `LAG(amount, 1, 0) OVER (ORDER BY created_at)`. What does the third argument `0` do?**
- [ ] It offsets the window by 0 rows
- [ ] It is the partition key for the window
- [x] It is the default value returned when there is no previous row
- [ ] It sets the frame size to 1 row before the current row

**Q4. A `LATERAL` join is most useful when:**
- [ ] You need to join two tables on multiple columns simultaneously
- [x] The right-hand subquery references columns from the left-hand table
- [ ] You want Postgres to choose between a hash join and a nested loop
- [ ] You are joining more than three tables

**Q5. What does `GROUPING SETS ((a, b), (a), ())` compute in a single query?**
- [ ] Three separate queries whose results are merged with UNION ALL
- [x] Subtotals grouped by `(a, b)`, then by `(a)` alone, then a grand total row
- [ ] A cube of all possible combinations of `a` and `b`
- [ ] A rollup that only includes non-NULL values

**Q6. In Postgres 12+, a CTE written without the `MATERIALIZED` keyword is:**
- [ ] Always evaluated once and stored in a temporary table
- [ ] Always inlined as a subquery regardless of usage count
- [x] Inlined by default; use `MATERIALIZED` to force one-time evaluation
- [ ] Evaluated lazily only when the outer query references it

**Q7. With `RECURSIVE`, if a row appears in the recursive term that was already in the accumulated result, what happens by default?**
- [ ] Postgres raises an error to prevent infinite loops
- [x] The row is added again, potentially causing an infinite loop — cycle detection must be added manually
- [ ] Postgres automatically detects the cycle and stops
- [ ] The row is silently deduplicated by the engine
