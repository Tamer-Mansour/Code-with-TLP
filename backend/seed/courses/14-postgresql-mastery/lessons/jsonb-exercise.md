# Filter JSONB Records

Simulate this Postgres query in Python:

```sql
SELECT *
FROM records
WHERE payload #>> '{address,country}' = 'DE';
```

Read JSON documents from stdin, descend a dotted path, and print every document whose value at that path equals the target.

See the prompt for the exact I/O contract.
