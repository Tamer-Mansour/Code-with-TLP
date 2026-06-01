# JSONB and GIN Indexes

`JSONB` is Postgres's binary JSON type. It stores documents as a tree, supports rich indexing, and turns Postgres into a respectable hybrid relational/document database.

## JSON vs JSONB

- **`json`** — stores text as-is. Preserves whitespace and key order. Slow to query.
- **`jsonb`** — parsed and stored as a binary tree. Indexable. Loses whitespace and key order. **Use this.**

## Creating and inserting

```sql
CREATE TABLE events (
  id        bigserial PRIMARY KEY,
  payload   jsonb NOT NULL
);

INSERT INTO events (payload) VALUES
  ('{"type":"login","user":{"id":1,"name":"Alice"},"tags":["web"]}'),
  ('{"type":"purchase","user":{"id":2,"name":"Bob"},"total":99.95}');
```

## Reading

| Operator   | Result type | Meaning                            |
|------------|-------------|------------------------------------|
| `->`       | jsonb       | Get field/element as JSON          |
| `->>`      | text        | Get field/element as text          |
| `#>`       | jsonb       | Path lookup as JSON                |
| `#>>`      | text        | Path lookup as text                |

```sql
SELECT payload -> 'user' -> 'name'  AS name_json,
       payload -> 'user' ->> 'name' AS name_text,
       payload #>> '{user,name}'    AS path_text
FROM events;
```

## Containment and existence

```sql
-- Does the payload contain this subdocument?
SELECT * FROM events WHERE payload @> '{"type":"login"}';

-- Does it contain ANY of these top-level keys?
SELECT * FROM events WHERE payload ?| ARRAY['type','source'];

-- Does it contain ALL of these top-level keys?
SELECT * FROM events WHERE payload ?& ARRAY['type','user'];

-- Does this top-level key exist?
SELECT * FROM events WHERE payload ? 'type';
```

`@>` is the workhorse — it asks "is the right-hand JSON a subset of the left?" and is GIN-indexable.

## GIN indexes

A plain B-tree won't help you query inside JSONB. Use a **GIN** (Generalized Inverted Index):

```sql
CREATE INDEX ix_events_payload ON events USING gin (payload);
```

This index supports `@>`, `?`, `?|`, `?&`. Heavy on disk, but typically the right choice for ad-hoc JSONB queries.

For a more space-efficient index restricted to containment only:

```sql
CREATE INDEX ix_events_payload ON events USING gin (payload jsonb_path_ops);
```

`jsonb_path_ops` is smaller and faster for `@>` but doesn't support the `?` operators.

## Expression indexes for specific paths

If you only ever filter by `payload->>'type'`:

```sql
CREATE INDEX ix_events_type ON events ((payload->>'type'));
SELECT * FROM events WHERE payload->>'type' = 'login';
```

This is a tiny B-tree, much smaller than a full GIN, and perfectly tuned for one query shape.

## Updating JSONB

```sql
-- set a key
UPDATE events SET payload = payload || '{"reviewed": true}' WHERE id = 1;

-- remove a key
UPDATE events SET payload = payload - 'tags' WHERE id = 1;

-- update a nested value
UPDATE events SET payload = jsonb_set(payload, '{user,name}', '"Alice2"');
```

## jsonpath (Postgres 12+)

A real query language for JSONB:

```sql
SELECT *
FROM events
WHERE payload @? '$.user.id ? (@ > 5)';
```

Useful for filtering on conditions you can't easily express with `@>`.

## When to use JSONB vs columns

Use columns when:
- You always read the value.
- You filter or sort on it.
- The schema is stable.

Use JSONB when:
- The shape varies per row.
- You're storing 3rd-party payloads.
- It's truly "extra metadata" with rare access.

Pure-JSONB tables are a code smell. Hybrid (some columns + some JSONB) is usually the right answer.
