# Schema Design Patterns in PostgreSQL

A well-designed schema catches data integrity bugs at the database layer, makes queries predictable, and leaves room to evolve without painful migrations. This lesson covers the most practical patterns for production Postgres schemas.

## Choose the right primary key type

| Choice              | Pros                                   | Cons                                    |
|---------------------|----------------------------------------|-----------------------------------------|
| `bigserial` / `bigint` | Small, sortable, human-readable IDs  | Sequential: predictable, leaks row count |
| `uuid` (random v4)  | Globally unique, safe to expose        | 16 bytes; random inserts fragment B-tree |
| `uuid` (v7 / ULID)  | Globally unique, time-ordered          | Requires `pg_uuidv7` or app generation  |

For most applications, `bigserial` primary keys with a random `uuid` column for external exposure (API IDs) is a clean compromise.

## Surrogate vs. natural keys

Use **surrogate keys** (`bigserial`) as the internal primary key. Never use mutable natural keys (email address, username) as a foreign key target — they change, and cascading updates are expensive.

```sql
CREATE TABLE users (
    id       bigserial PRIMARY KEY,
    email    text NOT NULL UNIQUE,
    username text NOT NULL UNIQUE
);

CREATE TABLE posts (
    id         bigserial PRIMARY KEY,
    author_id  bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      text NOT NULL,
    body       text NOT NULL
);
```

## Use constraints liberally

Database constraints are the last line of defence against bad data:

```sql
CREATE TABLE orders (
    id          bigserial PRIMARY KEY,
    status      text NOT NULL CHECK (status IN ('pending','paid','shipped','cancelled')),
    amount      numeric(12, 2) NOT NULL CHECK (amount > 0),
    created_at  timestamptz NOT NULL DEFAULT now(),
    shipped_at  timestamptz,
    CONSTRAINT shipped_after_created CHECK (shipped_at IS NULL OR shipped_at >= created_at)
);
```

Prefer `CHECK` constraints for value-level rules, and `UNIQUE` / `EXCLUSION` constraints for uniqueness invariants that span multiple columns.

## Normalization guidelines

- **1NF**: atomic values per column — no comma-separated lists. Use arrays (`text[]`) or a junction table instead.
- **2NF / 3NF**: avoid storing derived data in the table. Compute it in queries or, if performance demands it, in a generated column:

```sql
ALTER TABLE products
  ADD COLUMN price_with_vat numeric(12,2)
    GENERATED ALWAYS AS (price * 1.20) STORED;
```

- **Denormalize deliberately**: a `stats` JSONB blob or a materialized rollup column is fine when you've measured the query cost and it matters.

## Soft deletes

A common pattern: add `deleted_at timestamptz` instead of deleting rows. Create a partial index and a view so application code stays clean:

```sql
ALTER TABLE users ADD COLUMN deleted_at timestamptz;

CREATE INDEX ix_users_active ON users (email) WHERE deleted_at IS NULL;

-- Application queries always add: WHERE deleted_at IS NULL
-- Or use a view:
CREATE VIEW active_users AS SELECT * FROM users WHERE deleted_at IS NULL;
```

## Audit columns

Add created/updated timestamps to every entity table:

```sql
CREATE TABLE products (
    id         bigserial PRIMARY KEY,
    name       text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- Auto-update updated_at via trigger
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

## Polymorphic associations — the right way

Avoid nullable FK columns (`post_id`, `comment_id`, `video_id` all on the same row). Instead, model with a junction table per type or use table inheritance:

```sql
-- Pattern: per-type tables
CREATE TABLE comment_likes (
    user_id    bigint REFERENCES users(id),
    comment_id bigint REFERENCES comments(id),
    PRIMARY KEY (user_id, comment_id)
);

CREATE TABLE post_likes (
    user_id bigint REFERENCES users(id),
    post_id bigint REFERENCES posts(id),
    PRIMARY KEY (user_id, post_id)
);
```

Each table has full referential integrity; a single `likes` table with nullable FK columns has none.
