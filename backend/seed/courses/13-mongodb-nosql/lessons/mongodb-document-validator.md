# Document Validator

MongoDB stores data as flexible documents, but production systems almost always enforce a required set of fields at the application level (or via `$jsonSchema` validation). Understanding how to detect missing required fields is foundational to working with document databases.

## The Exercise

You are given a sequence of JSON-like records separated by `---` delimiters. Each record is a set of `key:value` pairs, one per line. Your job is to verify that every record contains the three required fields: `name`, `age`, and `email`.

For each record, print `VALID` if all three fields are present, or `MISSING: <fields>` listing the absent fields in alphabetical order, comma-separated.

## Example

Input:

```
name:Alice
age:30
email:alice@example.com
---
name:Bob
email:bob@example.com
---
age:25
```

Output:

```
VALID
MISSING: age
MISSING: email,name
```

## Key Concepts

**Schema validation in MongoDB** — By default, MongoDB does not enforce a schema. However, since v3.6 you can attach a `$jsonSchema` validator:

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      required: ["name", "age", "email"],
      properties: {
        name:  { bsonType: "string" },
        age:   { bsonType: "int", minimum: 0 },
        email: { bsonType: "string" }
      }
    }
  }
});
```

Inserts that violate the schema throw a `WriteError`. This exercise simulates the same logic in pure Python — parsing a record's field names and checking completeness.

## Approach

1. Split input on `---` boundaries to get individual records.
2. For each record, collect all field names (left side of `:`).
3. Compare the set of found fields against `{'name', 'age', 'email'}`.
4. If the difference is empty, output `VALID`; otherwise output `MISSING: ` followed by the missing fields sorted alphabetically and joined with `,`.

## Why This Matters

In real applications:

- An e-commerce platform that stores orders without a `customer` field will crash when billing runs.
- A user service missing `email` cannot send activation links.
- Field-level validation at insertion time is cheaper than discovering corrupt data months later during a data-science query.

The document model's flexibility is a feature — but it demands discipline. Either validate at the schema level (MongoDB's `$jsonSchema`) or at the application level before calling `insertOne`.

## Further Reading

- Christof Strauch, *NoSQL Databases* (HDM Stuttgart), §5 — Document Stores and Schema Evolution: [https://www.christof-strauch.de/nosqldbs.pdf](https://www.christof-strauch.de/nosqldbs.pdf)
- MongoDB documentation on Schema Validation: `db.createCollection` with `validator` option.
