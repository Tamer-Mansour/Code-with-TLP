# NoSQL vs SQL — When to Use What

"NoSQL" describes a loose family of databases that broke from the relational tradition during the mid-2000s scaling crunch. The label covers four distinct categories:

- **Document** (MongoDB, Couchbase) — store JSON-shaped objects.
- **Key-value** (Redis, DynamoDB) — opaque blob per key.
- **Wide-column** (Cassandra, Bigtable) — table-shaped but flexible columns per row.
- **Graph** (Neo4j, JanusGraph) — first-class edges and traversals.

This course is about **documents**, using MongoDB as the working example.

## What's different about documents

A document is a JSON-ish object — nested fields, arrays, no fixed schema across rows:

```json
{
  "_id": "ord_001",
  "customer": { "id": "u_42", "name": "Alice" },
  "items": [
    { "sku": "A", "qty": 2, "price": 9.99 },
    { "sku": "B", "qty": 1, "price": 4.50 }
  ],
  "total": 24.48,
  "createdAt": "2025-06-01T10:00:00Z"
}
```

The next document in the same collection might omit some fields or add new ones. Mongo doesn't care.

## Pros of document databases

- **No schema migration for new fields.** Just write them.
- **One read per "object."** The whole order is here — no joining 4 tables.
- **Native fit for hierarchical data** (forms, configs, event payloads).
- **Horizontal scaling baked in** (sharding).

## Cons

- **No foreign keys, no enforced constraints.** Bad writes become bad reads.
- **Joins are awkward and slower** (`$lookup`).
- **Transactions are weaker by default** — multi-document transactions exist but are expensive.
- **Ad-hoc reporting is harder** — pipelines aren't as well-understood as SQL.

## When to choose document

- Object payloads that vary across rows (CMS content, product catalogs).
- Event/log data where each record is self-contained.
- Rapid prototyping where the schema isn't pinned down.
- Heavy read patterns that match the document shape (no joins needed).

## When to stick with SQL

- Relational integrity matters (banking, inventory, anything with money).
- You need rich ad-hoc analytical queries (BI tools, ad-hoc SQL).
- The schema is stable and known.
- The team already speaks SQL.

## A common pragmatic stance

Many production systems use **both**: Postgres or MySQL for the system of record, MongoDB (or Elasticsearch, or DynamoDB) for a specific service whose access pattern fits documents. Pick the right tool for the *access pattern*, not the trend.
