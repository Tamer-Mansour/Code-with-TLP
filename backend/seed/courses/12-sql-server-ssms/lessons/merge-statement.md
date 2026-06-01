# The MERGE Statement

`MERGE` is T-SQL's "upsert + delete" in one statement. It compares a **source** to a **target** on a join condition and runs `INSERT`/`UPDATE`/`DELETE` depending on what matched.

## Shape

```sql
MERGE dbo.target AS t
USING dbo.source AS s
   ON t.id = s.id
WHEN MATCHED AND t.value <> s.value THEN
  UPDATE SET t.value = s.value, t.updated_at = GETDATE()
WHEN NOT MATCHED BY TARGET THEN
  INSERT (id, value, created_at) VALUES (s.id, s.value, GETDATE())
WHEN NOT MATCHED BY SOURCE THEN
  DELETE;
```

Three branches:

- `MATCHED` — row exists in both. Usually `UPDATE`.
- `NOT MATCHED BY TARGET` — exists in source only. Usually `INSERT`.
- `NOT MATCHED BY SOURCE` — exists in target only. Usually `DELETE` (or skip).

## A practical upsert

```sql
MERGE dbo.users AS t
USING (VALUES (1,'alice@x.com'),(2,'bob@x.com')) AS s(id, email)
   ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.email = s.email
WHEN NOT MATCHED BY TARGET THEN INSERT (id, email) VALUES (s.id, s.email);
```

## OUTPUT clause

Want to know what `MERGE` did? Capture the changes:

```sql
MERGE dbo.users AS t
USING new_users AS s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.email = s.email
WHEN NOT MATCHED BY TARGET THEN INSERT VALUES (s.id, s.email)
OUTPUT $action, inserted.id, inserted.email;
```

`$action` is `'INSERT'`, `'UPDATE'`, or `'DELETE'`. `OUTPUT` works on plain `INSERT`/`UPDATE`/`DELETE` too — extremely useful for audit trails.

## Warnings

`MERGE` has historically had subtle bugs (notably in early SQL Server versions when used with unique indexes and concurrent writes). Aaron Bertrand's advice: **prefer a sequence of `UPDATE` + `INSERT WHERE NOT EXISTS`** for production upserts unless `MERGE` makes the code dramatically clearer. For batch ETL it's usually fine.

## Alternative: UPDATE + INSERT

```sql
BEGIN TRANSACTION;

  UPDATE t SET email = s.email
  FROM dbo.users t
  JOIN new_users s ON s.id = t.id;

  INSERT INTO dbo.users (id, email)
  SELECT s.id, s.email
  FROM new_users s
  LEFT JOIN dbo.users t ON t.id = s.id
  WHERE t.id IS NULL;

COMMIT;
```

Less elegant but bullet-proof.
