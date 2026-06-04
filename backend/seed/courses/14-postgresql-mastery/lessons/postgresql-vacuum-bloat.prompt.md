# Simulate VACUUM: Identify Dead Tuple Bloat

PostgreSQL's MVCC model means `UPDATE` creates a **new row version** and marks the old one as a "dead tuple". `VACUUM` reclaims space by removing dead tuples and making that space reusable for future inserts.

## Problem

You are given a sequence of `INSERT` and `UPDATE` operations on a table with a single integer key. Simulate the tuple heap: each `UPDATE` on an existing key creates a new live version and marks the previous version dead. At the end, report:

1. The count of live tuples
2. The count of dead tuples
3. The dead tuple bloat percentage (`dead / total * 100`), rounded to **1 decimal place**

## Input Format

- First line: integer `N` (number of operations)
- Next `N` lines: either `INSERT key` or `UPDATE key`

Assume:
- `INSERT` always inserts a new key (no duplicate inserts)
- `UPDATE` always targets an existing key

## Output Format

Three lines, exactly as shown:

```
live: X
dead: Y
bloat: Z%
```

Where `Z` is rounded to 1 decimal place.

## Example

**Input:**
```
7
INSERT 1
INSERT 2
INSERT 3
UPDATE 1
UPDATE 2
UPDATE 1
INSERT 4
```

**Output:**
```
live: 4
dead: 3
bloat: 42.9%
```

**Explanation:** Three updates each created one dead tuple. Live = 4 keys still in the table. Total = 4 + 3 = 7. Bloat = 3/7 * 100 = 42.857... ≈ 42.9%.

## Constraints

- `1 <= N <= 10000`
- Keys are positive integers
- All `UPDATE` operations target a key that was previously inserted
- Use Python's built-in `round()` for rounding

## Notes

In a real Postgres table, you can observe this with:

```sql
SELECT n_live_tup, n_dead_tup,
       round(n_dead_tup::numeric / nullif(n_live_tup + n_dead_tup, 0) * 100, 1) AS bloat_pct
FROM pg_stat_user_tables
WHERE relname = 'your_table';
```
