# Reading Execution Plans in SSMS

An execution plan is the optimizer's strategy for running a query. SSMS shows it graphically and is the right tool for diagnosing slow T-SQL.

## Estimated vs actual plan

- **Estimated** (`Ctrl + L`): optimizer's plan based on statistics. Cheap — no query runs.
- **Actual** (`Ctrl + M` toggles capture, then `F5`): real plan plus per-operator row counts and timings. Use this when investigating.

## Reading the graph

Plans flow **right to left** and **bottom to top**. Each box is an **operator** — scan, seek, join, sort, etc. Arrows represent rows flowing between operators; thicker arrow = more rows.

## Operators you'll see often

| Operator              | What it means                                    | When to worry              |
|-----------------------|--------------------------------------------------|----------------------------|
| Clustered Index Scan  | Reads the whole table (clustered index = table). | Big table + no WHERE filter |
| Clustered Index Seek  | Direct lookup using the clustered index.         | Fine.                      |
| Index Seek            | Uses a nonclustered index.                       | Fine.                      |
| Key Lookup            | Nonclustered hit + fetch from clustered.         | Many → add INCLUDE.        |
| Nested Loops Join     | Cheap when one side is tiny.                     | Bad if both sides large.   |
| Hash Match (Join)     | Builds a hash from one side, probes from other.  | Fine for large unsorted.   |
| Merge Join            | Both sides sorted on join key.                   | Fine, but needs sort/index.|
| Sort                  | Explicit sort step.                              | Expensive — try to index it away. |
| Hash Aggregate        | GROUP BY via hash table.                         | OK; spills to tempdb if huge. |

## Spotting problems quickly

Look for:

- **Big arrows entering small results** — the planner read way more than it returned.
- **Yellow warning triangles** on operators — implicit conversions, missing stats, tempdb spills.
- **Estimated vs actual rows mismatch >10x** — statistics are stale; `UPDATE STATISTICS dbo.foo`.
- **A Sort operator on a column you have an index on** — query isn't using the index's order.

## SET STATISTICS IO/TIME

Numbers, not pictures:

```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

SELECT * FROM dbo.orders WHERE customer_email = '...';
```

Messages tab reports **logical reads** per table — your most reliable proxy for "this query touches too much data."

## Force a plan with hints (sparingly)

```sql
SELECT * FROM dbo.orders WITH (INDEX(ix_orders_email))
WHERE customer_email = '...';
```

Use only when the planner is provably wrong. If a hint is your only fix, file a bug with yourself: update stats, examine parameter sniffing, restructure the query before reaching for `OPTION (...)` long-term.

## Query Store (SQL Server 2016+)

Turn it on once:

```sql
ALTER DATABASE shop SET QUERY_STORE = ON;
```

It records the top queries, all their plans, and execution stats — then lets you **force** a known-good plan if the optimizer regresses. This is the modern way to manage plan stability in production.
