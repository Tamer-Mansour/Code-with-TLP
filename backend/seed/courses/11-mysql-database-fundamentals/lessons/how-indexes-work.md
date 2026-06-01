# How Indexes Actually Work

An index is a sorted data structure that lets MySQL find rows without scanning the whole table. In InnoDB it's a **B+ tree** keyed by your indexed columns.

## The mental model

Imagine the table as a phonebook sorted by `id`:

```
[100, Alice, ...]
[101, Bob,   ...]
[102, Carol, ...]
```

Finding `id = 101` is fast — binary search, O(log n).
Finding `name = 'Bob'` is slow — you must read every page.

Build a secondary index on `name`:

```sql
CREATE INDEX ix_users_name ON users(name);
```

Now MySQL keeps a second sorted structure: `(name → primary key)`. To find Bob, it binary-searches the name index for `'Bob'`, gets `id = 101`, then jumps to the row by PK. That second hop is called a **bookmark lookup**.

## Cardinality matters

An index on a column with two distinct values (`is_active`) is nearly useless — the optimizer will skip it and scan the table. High-cardinality columns (emails, UUIDs) get the most benefit.

## Composite indexes

```sql
CREATE INDEX ix_orders_user_date ON orders(user_id, created_at);
```

This index helps:

- `WHERE user_id = 1`                          ✓
- `WHERE user_id = 1 AND created_at > '2025-...'` ✓ (perfect)
- `WHERE created_at > '2025-...'`              ✗ (must scan)

This is the **leftmost-prefix rule**: a composite index serves queries that filter on the leading columns first.

## Covering indexes

If every column you `SELECT` is in the index, MySQL never touches the table — it answers from the index alone:

```sql
SELECT user_id, created_at FROM orders WHERE user_id = 1;
```

The index `(user_id, created_at)` *covers* this query. Very fast.

## When indexes hurt

Every index:

- Slows down `INSERT`/`UPDATE`/`DELETE` slightly.
- Uses disk and memory.
- Can confuse the planner if there are too many.

A working rule: **one PK + indexes for your top-N queries + foreign-key indexes**. Don't add an index "just in case."

## Listing indexes

```sql
SHOW INDEX FROM orders;
```

## Dropping an unused index

```sql
DROP INDEX ix_orders_user_id ON orders;
```

Use `sys.schema_unused_indexes` or `performance_schema` to find indexes that haven't been touched recently — those are prime candidates for removal.

## Hash and full-text indexes

InnoDB doesn't expose a hash index type (it auto-uses an adaptive hash internally). It does support `FULLTEXT` indexes for `MATCH ... AGAINST` text search:

```sql
CREATE FULLTEXT INDEX ix_posts_body ON posts(body);
SELECT * FROM posts WHERE MATCH(body) AGAINST('mysql');
```

For serious search workloads, though, ship documents to Elasticsearch — MySQL FULLTEXT is a "good enough" tool, not a great one.
