# Normalize to First Normal Form (1NF)

**First Normal Form (1NF)** is the foundation of relational database design. A table is in 1NF when every cell holds exactly one atomic value — no lists, no repeating groups, no comma-separated multi-values.

## The violation this exercise fixes

Imagine someone designed a student-course table like this:

```sql
CREATE TABLE student_courses (
  student_id INT,
  courses    VARCHAR(500)   -- "Math;Science;Art"
);
```

This violates 1NF. The `courses` column holds multiple values jammed into one cell. This causes real problems:

- You cannot index individual courses.
- Queries like `WHERE courses = 'Math'` require a slow `LIKE '%Math%'` scan.
- Counting how many students take Math requires string parsing in the application.
- Updating a single course enrollment touches the whole row.

## The correct 1NF design

Split the multi-valued column into separate rows:

```sql
CREATE TABLE student_courses (
  student_id INT,
  course     VARCHAR(100),
  PRIMARY KEY (student_id, course)
);
```

Now each row holds exactly one `(student, course)` pair. You can index, count, and update individual courses cleanly.

## What you will implement

Given N rows where each row has a `student_id` and a semicolon-separated list of courses, output the normalized 1NF rows: one `(student_id, course)` pair per line, sorted by `student_id` ascending then by course name ascending.

## SQL equivalent

This exercise models the output of:

```sql
-- After normalization, this query is trivial:
SELECT student_id, course
FROM student_courses
ORDER BY student_id, course;
```

## Further reading

- *Database Design — 2nd Edition*, Adrienne Watt (BCcampus) — Chapter 8: Normalization — https://opentextbc.ca/dbdesign01/
- *MIT OCW 1.264J*, Lecture 10: Normalization — https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/
