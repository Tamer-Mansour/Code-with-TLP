# Write-Through vs Cache-Aside Consistency

Simulate both a write-through cache and a cache-aside cache operating against the same shared in-memory database.

## Input

Commands one per line:

- `WRITE key value` — writes `value` to the database. Write-through cache is updated immediately. Cache-aside cache entry is deleted (invalidated).
- `READ_WT key` — read using the write-through cache.
- `READ_CA key` — read using the cache-aside cache.

Both caches start empty. On a cache miss for either pattern, fetch from the database and populate the cache (if the key exists in the database).

## Output

For each `READ_WT` or `READ_CA`, print one line:

- `WT: HIT <value>` or `WT: MISS <value>` (for `READ_WT`)
- `CA: HIT <value>` or `CA: MISS <value>` (for `READ_CA`)

If a key does not exist in the database, the value is `None`.

`WRITE` commands produce no output.

## Example

Input:
```
WRITE user:1 alice
READ_WT user:1
READ_CA user:1
WRITE user:1 bob
READ_WT user:1
READ_CA user:1
READ_CA user:2
READ_WT user:2
```

Output:
```
WT: HIT alice
CA: MISS alice
WT: HIT bob
CA: MISS bob
CA: MISS None
WT: MISS None
```
