# Schema Design, Primary and Foreign Keys

Good schema design is the foundation of every reliable backend. Before you write a single Spring Data repository, you need tables that model your data correctly, enforce integrity, and read well. In this lesson we design a small schema in MySQL 8 and use **primary keys** and **foreign keys** to keep it consistent.

## What a primary key does

A **primary key** uniquely identifies each row in a table. It must be unique and non-null, and MySQL automatically creates an index on it. Most applications use a surrogate key — a meaningless auto-incrementing integer — rather than a natural key (like an email), because surrogate keys never change and join efficiently.

```sql
CREATE TABLE author (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    name        VARCHAR(120) NOT NULL,
    email       VARCHAR(180) NOT NULL,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_author_email (email)
) ENGINE=InnoDB;
```

Note the `UNIQUE KEY` on `email`: it is *not* the primary key, but it still guarantees no two authors share an address. Use `BIGINT` for ids when you expect growth, and always use the `InnoDB` engine — it is the only MySQL engine that enforces foreign keys.

## What a foreign key does

A **foreign key** links a column in one table to the primary key of another, so the database refuses to store orphaned references. Here a `book` belongs to one `author`:

```sql
CREATE TABLE book (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    title       VARCHAR(200) NOT NULL,
    author_id   BIGINT       NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_book_author
        FOREIGN KEY (author_id) REFERENCES author (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;
```

Now `INSERT INTO book (title, author_id) VALUES ('Spring', 999)` fails if no author `999` exists. The referential action controls what happens to children when a parent changes:

| Action | Effect on child rows when parent is deleted/updated |
| --- | --- |
| `RESTRICT` / `NO ACTION` | Block the operation if children exist (safe default) |
| `CASCADE` | Delete or update the children automatically |
| `SET NULL` | Set the FK column to `NULL` (column must allow nulls) |

## Mapping it in Spring (JPA)

The same relationship in a Spring entity uses `@ManyToOne`:

```java
@Entity
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @ManyToOne(optional = false, fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Author author;
}
```

`GenerationType.IDENTITY` maps to MySQL `AUTO_INCREMENT`. Prefer `FetchType.LAZY` on `@ManyToOne` so you do not silently load related rows on every query.

## Common mistakes and best practices

- **Skipping `InnoDB`.** MyISAM ignores foreign keys entirely — integrity is silently lost.
- **Mismatched types.** The FK column and the referenced PK must have the same type (e.g., both `BIGINT`). MySQL rejects the constraint otherwise.
- **No index strategy.** MySQL auto-indexes the FK column, but you still need indexes on columns you frequently filter or join on.
- **Defaulting to `CASCADE`.** Cascading deletes can wipe data unexpectedly; start with `RESTRICT` and opt in deliberately.
- **Using natural keys as PKs.** Emails, usernames, and codes change — surrogate keys do not.
- **Wrong charset.** Use `utf8mb4` so the schema stores full Unicode (including emoji): `CREATE TABLE ... DEFAULT CHARSET=utf8mb4;`.

## Summary

Primary keys uniquely identify rows; foreign keys enforce valid links between tables. Use `BIGINT AUTO_INCREMENT` surrogate keys on `InnoDB`, choose referential actions deliberately, and mirror these relationships in JPA with `@Id`, `@GeneratedValue`, and `@ManyToOne` + `@JoinColumn`.
