# The Relational Model

The relational model is the mathematical foundation that every relational database — including MySQL — is built on. Introduced by Edgar F. Codd in 1970, it organises data into **relations** (tables), defines precise rules about how those tables are structured, and provides a set of operations for querying and manipulating them. Understanding this model helps you write correct schemas, choose the right keys, and reason clearly about joins.

## Core Concepts

### Relations, Tuples, and Attributes

| Relational term | SQL term | Meaning |
|---|---|---|
| Relation | Table | A named set of rows, all with the same structure |
| Tuple | Row / Record | A single entry in a relation |
| Attribute | Column / Field | A named property with a specific data type |
| Domain | Data type | The set of legal values for an attribute (e.g. `INT`, `VARCHAR(100)`) |
| Degree | Number of columns | How many attributes a relation has |
| Cardinality | Number of rows | How many tuples a relation contains at a given moment |

A relation is a **set** — duplicates are not allowed, and (in theory) rows have no inherent order. In practice, MySQL stores rows in pages and you must supply `ORDER BY` to guarantee a specific order.

### Primary Keys

A **primary key** is a minimal set of attributes whose values uniquely identify every tuple. "Minimal" means you cannot remove an attribute from the set and still have uniqueness.

```sql
CREATE TABLE course (
    id          INT          NOT NULL AUTO_INCREMENT,
    title       VARCHAR(200) NOT NULL,
    slug        VARCHAR(200) NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_course_slug (slug)
);
```

`id` is the **surrogate** primary key (system-generated, no business meaning). `slug` is declared `UNIQUE` because it is a **natural key** candidate — but it is not the primary key here, keeping joins simple and stable.

### Foreign Keys and Referential Integrity

A **foreign key** is an attribute (or set of attributes) in one table whose values must match an existing primary key value in another table. This constraint is called **referential integrity**.

```sql
CREATE TABLE lesson (
    id          INT          NOT NULL AUTO_INCREMENT,
    course_id   INT          NOT NULL,
    title       VARCHAR(200) NOT NULL,
    position    SMALLINT     NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    CONSTRAINT fk_lesson_course
        FOREIGN KEY (course_id) REFERENCES course (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

With `ON DELETE CASCADE`, deleting a `course` row automatically removes all related `lesson` rows. Without the foreign key, nothing stops you from inserting a `lesson` that points to a non-existent `course_id` — silent data corruption.

### Relationships Between Tables

Three types of relationships exist between entities:

- **One-to-Many (1:N)** — the most common. One `course` has many `lesson` rows. Modelled with a foreign key on the "many" side (`lesson.course_id`).
- **Many-to-Many (M:N)** — requires a **junction table**. A student can enrol in many courses; a course has many students.
- **One-to-One (1:1)** — one row in table A corresponds to exactly one row in table B. Used to split large tables or isolate sensitive columns.

#### Many-to-Many Example

```sql
CREATE TABLE student (
    id    INT          NOT NULL AUTO_INCREMENT,
    email VARCHAR(150) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_student_email (email)
);

CREATE TABLE enrollment (
    student_id  INT      NOT NULL,
    course_id   INT      NOT NULL,
    enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id),           -- composite PK
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id) REFERENCES student (id),
    CONSTRAINT fk_enroll_course  FOREIGN KEY (course_id)  REFERENCES course  (id)
);
```

The composite primary key `(student_id, course_id)` enforces that the same student cannot enrol in the same course twice.

## NULL and the Three-Valued Logic

The relational model has a nuanced treatment of missing data. `NULL` means "unknown" — it is not zero, not an empty string, not `false`. This leads to **three-valued logic**: a comparison with `NULL` evaluates to `UNKNOWN`, not `TRUE` or `FALSE`.

```sql
-- This returns NO rows, even for rows where notes IS NULL
SELECT * FROM lesson WHERE notes = NULL;

-- Correct: use IS NULL / IS NOT NULL
SELECT * FROM lesson WHERE notes IS NULL;
```

## Querying with Relational Operations

SQL is a concrete syntax for the relational algebra. The core operations map as follows:

| Relational algebra | SQL equivalent |
|---|---|
| Selection (σ) | `WHERE` clause |
| Projection (π) | Column list in `SELECT` |
| Join (⋈) | `JOIN ... ON` |
| Union (∪) | `UNION` |
| Difference (−) | `EXCEPT` / `NOT IN` / `NOT EXISTS` |

A join between `course` and `lesson` using the foreign key:

```sql
SELECT
    c.title  AS course_title,
    l.title  AS lesson_title,
    l.position
FROM   course  c
JOIN   lesson  l ON l.course_id = c.id
WHERE  c.slug = 'backend-developer-roadmap'
ORDER  BY l.position;
```

## Common Mistakes and Best Practices

- **Storing multiple values in one column** — e.g. `tags VARCHAR(500)` containing `"java,spring,mysql"`. This violates the relational model (an attribute must be atomic). Use a separate `tag` table with a junction table instead.
- **No primary key** — every table must have one. Without it, rows cannot be uniquely addressed, updates become ambiguous, and many ORM frameworks break.
- **Skipping foreign key constraints** — relying only on application code to maintain referential integrity means one bad migration script can corrupt the whole dataset.
- **Using `NULL` as a default for everything** — prefer `NOT NULL` with a sensible default (`''`, `0`, `CURRENT_TIMESTAMP`) unless the absence of a value has genuine business meaning.
- **Overusing surrogate keys** — natural keys like `(student_id, course_id)` in a junction table are perfectly valid composite primary keys and carry their own uniqueness semantics.

## Summary

The relational model organises data into tables of typed columns and uniquely identified rows, with foreign keys enforcing relationships between tables. Every SQL statement you write — DDL or DML — is an expression of relational algebra, and understanding the model behind the syntax is what separates confident schema design from trial-and-error guesswork.
