# Index Lookup Simulation

## Problem

Simulate a B-tree index lookup. You are given a sorted list of `(key, value)` pairs representing an index, and a list of lookup queries. For each query, use **binary search** to find the key and return its associated value, or `NOT FOUND` if the key doesn't exist.

This models the performance characteristic of `SELECT value FROM table WHERE key = ?` on an indexed column — O(log n) instead of O(n).

**Input format:**

```
N
key1 value1
key2 value2
...   (N index entries, sorted by key ascending)
Q
query1
query2
...   (Q lookup queries)
```

- First line: `N`, number of index entries
- Next N lines: each is an integer key and a string value, space-separated
- Next line: `Q`, number of queries
- Next Q lines: each is a single integer key to look up

**Output:**

For each query (in order), output the value if found, or `NOT FOUND` if not. One result per line.

## Example

**Input:**
```
5
10 Alice
20 Bob
30 Carol
40 Dave
50 Eve
4
20
35
10
99
```

**Output:**
```
Bob
NOT FOUND
Alice
NOT FOUND
```

## Constraints

- `1 <= N <= 10000`
- `1 <= Q <= 1000`
- Keys are distinct positive integers, given in **sorted ascending order**
- Values are single-word strings
- You must use binary search (or equivalent O(log n) approach) — a linear scan would defeat the purpose of the exercise
