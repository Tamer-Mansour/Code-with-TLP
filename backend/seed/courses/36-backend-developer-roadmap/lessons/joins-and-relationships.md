# JOINs and Relationships

Real applications almost never store everything in one table. Instead, data is split into related tables and connected with **foreign keys**. A `JOIN` lets you recombine those tables in a single query so you can answer questions that span them.

## Modeling relationships

In MySQL you express relationships using a `FOREIGN KEY` that points at the primary key of another table.

```sql
CREATE TABLE authors (
  id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL
);

CREATE TABLE books (
  id        BIGINT PRIMARY KEY AUTO_INCREMENT,
  title     VARCHAR(200) NOT NULL,
  author_id BIGINT,
  CONSTRAINT fk_book_author
    FOREIGN KEY (author_id) REFERENCES authors(id)
);
```

The three classic relationship types:

| Relationship | Example | How it's modeled |
|--------------|---------|------------------|
| One-to-many  | one author has many books | FK on the "many" side (`books.author_id`) |
| One-to-one   | a user has one profile | FK + `UNIQUE` constraint |
| Many-to-many | students ↔ courses | a join table (`enrollments`) with two FKs |

## The main JOIN types

Given `authors` and `books`, here is how each join behaves:

```sql
-- INNER JOIN: only rows that match on both sides
SELECT a.name, b.title
FROM authors a
INNER JOIN books b ON b.author_id = a.id;

-- LEFT JOIN: every author, even those with no books (book columns become NULL)
SELECT a.name, b.title
FROM authors a
LEFT JOIN books b ON b.author_id = a.id;
```

| Join type   | Returns |
|-------------|---------|
| `INNER JOIN` | rows present in **both** tables |
| `LEFT JOIN`  | **all** left rows + matched right rows (else NULL) |
| `RIGHT JOIN` | all right rows + matched left rows (else NULL) |
| `CROSS JOIN` | every combination (Cartesian product) |

MySQL has no `FULL OUTER JOIN`; emulate it by `UNION`-ing a `LEFT JOIN` and a `RIGHT JOIN`.

## Worked example: many-to-many

```sql
CREATE TABLE students   (id BIGINT PRIMARY KEY, name VARCHAR(100));
CREATE TABLE courses    (id BIGINT PRIMARY KEY, title VARCHAR(100));
CREATE TABLE enrollments (
  student_id BIGINT,
  course_id  BIGINT,
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES students(id),
  FOREIGN KEY (course_id)  REFERENCES courses(id)
);

-- All courses a given student is enrolled in
SELECT s.name, c.title
FROM students s
JOIN enrollments e ON e.student_id = s.id
JOIN courses c     ON c.id = e.course_id
WHERE s.id = 1;
```

The `enrollments` join table bridges the two sides. To count books per author, combine a `LEFT JOIN` with aggregation:

```sql
SELECT a.name, COUNT(b.id) AS book_count
FROM authors a
LEFT JOIN books b ON b.author_id = a.id
GROUP BY a.id, a.name;
```

Using `LEFT JOIN` here ensures authors with zero books still appear (with `book_count = 0`).

## Common mistakes and best practices

- **Forgetting the `ON` condition** turns a join into an accidental `CROSS JOIN`, exploding row counts.
- **Filtering an outer join in `WHERE`** silently converts it to an inner join. To keep unmatched rows, put the extra condition in the `ON` clause: `LEFT JOIN books b ON b.author_id = a.id AND b.title LIKE 'A%'`.
- **Always index foreign-key columns.** MySQL/InnoDB indexes them automatically when a FK constraint exists, which keeps joins fast.
- **Qualify columns with aliases** (`a.id`, `b.id`) to avoid ambiguous-column errors.
- Choose `ON ColumnName` only when both columns share the same name and you accept its merge behavior; prefer an explicit `ON a.id = b.author_id` for clarity.

## Summary

Relationships are defined with foreign keys; JOINs reassemble related tables at query time. Reach for `INNER JOIN` to keep only matches, `LEFT JOIN` to preserve every row from the primary table, and a join table for many-to-many links.
