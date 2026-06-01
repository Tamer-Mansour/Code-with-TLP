# What is MySQL?

MySQL is one of the most widely deployed open-source **relational database management systems** (RDBMS) in the world. It stores data in **tables** of rows and columns, lets you query and modify that data with **SQL**, and guarantees those changes survive crashes through its transactional storage engine.

It was created in 1995 by MySQL AB, acquired by Sun (2008), and is now stewarded by Oracle. A community fork, **MariaDB**, is also widely used and largely compatible.

## Where MySQL fits

A typical web stack looks like this:

```
Browser  →  HTTP server  →  Application code  →  MySQL  →  Disk
```

Your application code holds the business logic. MySQL is the **system of record** — the durable, queryable source of truth.

## What MySQL is good at

- **Structured data** with clear relationships: users, orders, products, comments.
- **Transactions**: "transfer $10 from A to B" either fully happens or fully doesn't.
- **Concurrent access** from many connections without corrupting data.
- **Querying** with SQL — declarative, set-based, and surprisingly powerful.

## What it is not

- Not a search engine (use Elasticsearch / OpenSearch for full-text at scale).
- Not a queue (use Redis, Kafka, RabbitMQ).
- Not a document store, though `JSON` columns exist (MongoDB is purpose-built for that).
- Not a cache (Redis).

## Storage engines

A MySQL feature that surprises newcomers: the **storage engine** is pluggable.

| Engine   | Transactions | Foreign keys | Crash safe | Use for           |
|----------|:------------:|:------------:|:----------:|-------------------|
| InnoDB   | Yes          | Yes          | Yes        | Almost everything |
| MyISAM   | No           | No           | No         | Legacy only       |
| Memory   | No           | No           | No         | Temp scratch      |

Since MySQL 5.5, **InnoDB is the default** and is what you should use unless you have a very specific reason not to.

## A first query

```sql
SELECT id, name, email
FROM users
WHERE created_at > '2025-01-01'
ORDER BY created_at DESC
LIMIT 10;
```

Read it left-to-right and it almost sounds like English: *select these columns, from this table, where this filter holds, sorted by this column, limited to ten rows*.

Behind the scenes MySQL parses that into a tree, picks an index, walks the storage engine, and streams rows back to you. The rest of this course is the story of what happens in that middle step — and how to make it fast.
