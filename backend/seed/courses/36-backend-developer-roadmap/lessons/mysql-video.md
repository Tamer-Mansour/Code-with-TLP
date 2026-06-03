# Video: SQL and MySQL Full Course

This video provides a comprehensive, hands-on walkthrough of SQL fundamentals and MySQL 8 — from writing your first query to designing normalized relational schemas and using advanced features like transactions, indexes, and stored procedures.

## What you'll learn

- Core SQL syntax: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `JOIN`, and aggregate functions
- MySQL-specific data types (`VARCHAR`, `TEXT`, `DECIMAL`, `DATETIME`, `ENUM`) and table creation with constraints
- Database design: primary keys, foreign keys, normalization (1NF–3NF), and ER diagrams
- Filtering and sorting with `WHERE`, `ORDER BY`, `GROUP BY`, `HAVING`, and subqueries
- Indexes, transactions (`COMMIT` / `ROLLBACK`), and basic stored procedures
- Connecting MySQL to a Java application via JDBC and Spring Data JPA

## Key takeaways

- Always define a primary key and choose the narrowest appropriate data type
- Use `EXPLAIN` to inspect query execution plans and catch missing indexes early
- Wrap multi-step writes in a transaction to keep data consistent
- Parameterized queries (prepared statements) prevent SQL injection by default in JDBC

## Follow-along checklist

- [ ] MySQL 8 installed and `mysql` CLI accessible
- [ ] A test database created: `CREATE DATABASE tlp_practice;`
- [ ] MySQL Workbench or DBeaver open alongside the video
- [ ] Sample schema drafted before watching the advanced sections

The course link opens a curated YouTube search featuring free, high-quality full-course videos from channels such as freeCodeCamp on this exact topic.
