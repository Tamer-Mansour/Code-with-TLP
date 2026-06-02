# Simulate MongoDB Query Filtering

You are given a small in-memory "collection" of documents and a single-field filter condition. Output the documents that match the filter, in original order.

## Input

```
N
field op value
doc1_field1:val1 doc1_field2:val2 ...
...
```

- `N` — number of documents (1 ≤ N ≤ 100).
- Filter line: `field op value` where `op` ∈ {eq, gt, lt, gte, lte} and `value` is an integer.
- Each of the next `N` lines is a document: space-separated `key:value` pairs, all values integers.

## Output

Print each matching document on its own line (fields in original order). Print `none` if nothing matches.

## Example

**Input:**
```
3
age gt 25
name:Alice age:30
name:Bob age:20
name:Carol age:35
```

**Output:**
```
name:Alice age:30
name:Carol age:35
```
