# Window Functions in PostgreSQL — Video Overview

This video from freeCodeCamp walks through SQL window functions — `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, and frame clauses — using live PostgreSQL examples.

Key takeaways:

- Window functions compute a result across a set of rows related to the current row without collapsing them into a single output row (unlike `GROUP BY`).
- The `OVER (PARTITION BY ... ORDER BY ...)` clause defines the window frame; omitting `PARTITION BY` runs the function over the entire result set.
- `LAG` and `LEAD` are the go-to tools for comparing a row to its predecessor or successor (e.g., month-over-month revenue change).
- Aggregate functions (`SUM`, `AVG`, `COUNT`) also work as window functions when paired with `OVER`, enabling running totals and moving averages.
- Understanding frame boundaries (`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`) is essential for correct running-total calculations.
