# Data Types and NULL

Picking the right column type is the most consequential schema decision you make. The right type is cheaper to store, faster to query, and rejects bad data at the boundary.

## Numeric types

| Type           | Bytes | Range                         | Use for                |
|----------------|------:|-------------------------------|------------------------|
| `TINYINT`      | 1     | -128 to 127                   | Tiny enums, flags      |
| `INT`          | 4     | ~ ±2.1 billion                | IDs, counts            |
| `BIGINT`       | 8     | ~ ±9.2e18                     | Big IDs, money in cents|
| `DECIMAL(p,s)` | var   | exact, p digits, s decimals   | Money, anything exact  |
| `FLOAT`        | 4     | inexact                       | Approximations only    |
| `DOUBLE`       | 8     | inexact                       | Scientific work        |

Never store money in `FLOAT` — `0.1 + 0.2 ≠ 0.3` will haunt you. Use `DECIMAL(18,2)` or integer cents.

## Strings

| Type            | Notes                                                     |
|-----------------|-----------------------------------------------------------|
| `CHAR(n)`       | Fixed length, padded with spaces. Use for codes (`'US'`). |
| `VARCHAR(n)`    | Variable length up to n characters.                       |
| `TEXT`          | Long text. Slower than VARCHAR for indexing.              |
| `BLOB`          | Binary. Avoid in DBs if possible — use object storage.    |
| `ENUM(...)`     | Constrained to a fixed list of strings.                   |

`VARCHAR(255)` is folklore. Pick a real maximum based on the domain.

## Dates and times

| Type        | Stores                          | Range                       |
|-------------|---------------------------------|-----------------------------|
| `DATE`      | Y-M-D                           | 1000-01-01 to 9999-12-31    |
| `DATETIME`  | Y-M-D H:M:S, no time zone       | Same range as DATE          |
| `TIMESTAMP` | Same, but with UTC conversion   | 1970 to 2038                |
| `TIME`      | H:M:S                           | -838:59:59 to 838:59:59     |

Beware `TIMESTAMP`'s 2038 limit. Prefer `DATETIME` for far-future dates; use `TIMESTAMP` when you want auto-update on row change.

## JSON

```sql
CREATE TABLE prefs (
  user_id INT PRIMARY KEY,
  data    JSON
);

INSERT INTO prefs VALUES (1, '{"theme":"dark","tz":"UTC"}');
SELECT data->>'$.theme' FROM prefs WHERE user_id = 1;
```

Useful for schemaless slivers. Don't use it to dodge schema design entirely.

## NULL

`NULL` means "unknown" — not zero, not empty string. It has three big consequences:

1. **All comparisons with NULL produce NULL** (treated as false in `WHERE`).
2. **Aggregates ignore NULL** — `AVG` skips them; `COUNT(col)` doesn't count them.
3. **`UNIQUE` allows multiple NULLs** in MySQL (treated as distinct from each other).

Use `NOT NULL` by default. Reach for `NULL` only when "unknown" is genuinely meaningful (e.g., `deleted_at`).

## DEFAULTs

```sql
CREATE TABLE users (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  email       VARCHAR(200) NOT NULL,
  is_active   TINYINT(1) NOT NULL DEFAULT 1,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
              ON UPDATE CURRENT_TIMESTAMP
);
```

`ON UPDATE CURRENT_TIMESTAMP` is a MySQL gift — automatic `updated_at` columns without triggers.
