# Relational Schema Validator

In a relational database, **referential integrity** means every foreign key value in a child table must match an existing primary key in the parent table. MySQL enforces this automatically when you declare `FOREIGN KEY` constraints, but understanding what the engine is checking — and what breaks when it isn't there — is fundamental.

## The problem this exercise models

```sql
CREATE TABLE students (
  id   INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);

CREATE TABLE enrollments (
  student_id INT NOT NULL,
  course     VARCHAR(100) NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(id)
);
```

If you try to insert `(4, 'History')` into `enrollments` when no student with `id = 4` exists, MySQL will reject it with **Error 1452: Cannot add or update a child row: a foreign key constraint fails**.

An "orphaned" row is one whose foreign key points to a parent that doesn't exist — exactly what this constraint prevents.

## What you will implement

Write a program that simulates this check without a real database. Given a list of student records and enrollment records, determine whether referential integrity holds.

- Read all student IDs into a set (the "parent" table).
- For each enrollment, check whether its `student_id` is in that set.
- Any `student_id` not found is an **orphan**.

## Key insight

This is exactly the check MySQL's InnoDB performs on every `INSERT` or `UPDATE` that touches a foreign key column. The engine holds a shared lock on the parent row during the child insert to guarantee the parent can't be deleted mid-write.

## Further reading

- *Database Design — 2nd Edition*, Adrienne Watt (BCcampus): Chapter on Referential Integrity — https://opentextbc.ca/dbdesign01/
- *CS50's Introduction to Databases with SQL*, Harvard University — https://pll.harvard.edu/course/cs50s-introduction-databases-sql
