# Partition Pruning Simulator

PostgreSQL declarative table partitioning allows the query planner to skip irrelevant partitions — called **partition pruning**. This reduces I/O and speeds up queries because only partitions whose ranges overlap with the `WHERE` clause need to be scanned.

## Problem

You are given a `RANGE`-partitioned table definition and a set of `WHERE` clause conditions. For each query, determine which partitions the planner **must scan** (those whose range overlaps with the query condition) and which are **pruned** (skipped).

Partitions are defined as `[low, high)` half-open intervals on an integer key.

## Input Format

- First line: integer `P` (number of partitions)
- Next `P` lines: `partition_name low high` (integers, half-open `[low, high)`)
- Next line: integer `Q` (number of queries)
- Next `Q` lines: `operator value` where `operator` is one of: `=`, `<`, `>`, `<=`, `>=`

## Output Format

For each query, print the names of partitions that must be scanned, **space-separated and sorted alphabetically**. If no partition matches, print `NONE`.

## Example

**Input:**
```
4
p2020 0 1000
p2021 1000 2000
p2022 2000 3000
p2023 3000 4000
3
= 1500
< 1000
>= 2000
```

**Output:**
```
p2021
p2020
p2022 p2023
```

**Explanation:**
- `= 1500`: 1500 is in `[1000, 2000)` → only `p2021`
- `< 1000`: values less than 1000 are in `[0, 1000)` → only `p2020`
- `>= 2000`: values from 2000 onward are in `[2000,3000)` and `[3000,4000)` → `p2022 p2023`

## Pruning Rules

A partition `[low, high)` is **scanned** (not pruned) when:
- `= val`: `low <= val < high`
- `< val`: `low < val` (partition may have values less than val)
- `> val`: `high - 1 > val` (equivalently: `high > val + 1`)
- `<= val`: `low <= val`
- `>= val`: `high > val`

## Constraints

- `1 <= P <= 20`
- `1 <= Q <= 20`
- Partition ranges do not overlap
- All values are non-negative integers less than 10^9
- Partition names contain no spaces
