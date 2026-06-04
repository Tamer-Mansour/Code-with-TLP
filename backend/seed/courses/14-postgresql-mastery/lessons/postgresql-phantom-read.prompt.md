# Transaction Isolation: Detect Phantom Read Scenario

In PostgreSQL, a **phantom read** occurs when a transaction re-executes a range query and finds new rows that were inserted by another committed transaction between its two reads. This anomaly can occur at `READ COMMITTED` isolation level but not at `SERIALIZABLE`.

## Problem

You are given a log of database events. Each event is either a `READ` range query (listing the rows seen) or an `INSERT`. Detect all phantom read occurrences: a phantom read happens when a transaction issues a **second range READ** and the result set contains rows **not present in its first READ** (because another transaction inserted them in between).

## Input Format

- First line: integer `N` (number of events)
- Each event line: `T=<txn_id> OP=<READ|INSERT> [ROWS=<comma-separated ids>]`
  - `READ` events have `ROWS=` showing what was visible to that transaction
  - `INSERT` events have `ROWS=` showing the inserted row id
  - Each transaction has **at most 2 READ events**

## Output Format

Print each transaction that experienced a phantom read as: `PHANTOM txn_id` (sorted ascending by txn_id).

If no transaction experienced a phantom read, print `NONE`.

## Example

**Input:**
```
6
T=1 OP=READ ROWS=10,20
T=2 OP=INSERT ROWS=30
T=3 OP=READ ROWS=10,20
T=1 OP=READ ROWS=10,20,30
T=3 OP=READ ROWS=10,20
T=4 OP=READ ROWS=10,20,30
```

**Output:**
```
PHANTOM 1
```

**Explanation:** Transaction 1 first saw rows `{10, 20}`, then saw `{10, 20, 30}` — row 30 appeared between its two reads (a phantom). Transaction 3 saw `{10, 20}` twice — no change. Transaction 4 only has one READ event — cannot be a phantom.

## Constraints

- `1 <= N <= 1000`
- Transaction IDs are positive integers
- `ROWS=` values are comma-separated positive integers with no spaces
- Each transaction has at most 2 READ events; only the first and second matter
- A phantom read requires rows to appear (not disappear) between reads

## Notes

At `SERIALIZABLE` isolation level, PostgreSQL uses Serializable Snapshot Isolation (SSI) to detect and prevent this scenario. At `READ COMMITTED` (the default), each statement gets a fresh snapshot, so phantom reads are possible. To prevent phantoms without full serialization, use `REPEATABLE READ` — Postgres prevents phantoms at that level too.
