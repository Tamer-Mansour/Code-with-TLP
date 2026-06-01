# JSONB-style Path Filter

Implement the Python equivalent of:

```sql
SELECT *
FROM t
WHERE payload #>> :path = :value;
```

## Input

```
N
<path>=<value>
<json doc 1>
<json doc 2>
... N docs
```

- `N` — number of JSON documents (1 ≤ N ≤ 1000).
- Line 2 is `path=value`. `path` is dot-separated (e.g. `address.country`). `value` is the literal text to compare against (string compare, never quoted).
- Each subsequent line is one JSON document on a single line.

## Output

For each document where the value at `path` equals `value`, print the document **unchanged** (as it appeared in input), in input order.

If a document is malformed JSON or the path is missing, skip it.

## Examples

Input:

```
3
address.country=DE
{"name":"Alice","address":{"country":"DE"}}
{"name":"Bob","address":{"country":"US"}}
{"name":"Carol","address":{"country":"DE"}}
```

Output:

```
{"name":"Alice","address":{"country":"DE"}}
{"name":"Carol","address":{"country":"DE"}}
```

Top-level path:

Input:

```
2
role=admin
{"role":"admin","id":1}
{"role":"user","id":2}
```

Output:

```
{"role":"admin","id":1}
```

## Notes

- Comparison is **string equality** of the value at that path, converted via Python's `str()`. So `1` matches `1` and `"1"` matches `1`.
- Paths only descend into objects (never arrays or scalars).
