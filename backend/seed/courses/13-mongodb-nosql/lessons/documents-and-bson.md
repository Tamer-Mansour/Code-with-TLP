# Documents, BSON, and the _id Field

A **document** is the fundamental unit in MongoDB — like a row in SQL, but more expressive.

## Document = JSON-ish

```json
{
  "_id": ObjectId("651a..."),
  "name": "Alice",
  "tags": ["admin", "early-adopter"],
  "address": {
    "city": "Berlin",
    "country": "DE"
  },
  "loginCount": 42,
  "lastLogin": ISODate("2025-06-01T09:00:00Z")
}
```

Nested objects, arrays, dates, ObjectIds — all native types.

## BSON, not JSON

On the wire and on disk MongoDB stores **BSON** — Binary JSON. BSON adds types JSON doesn't have:

- **ObjectId** — 12-byte unique ID (timestamp + machine + counter).
- **Date** — ISO 8601 timestamp.
- **Int32 / Int64 / Double / Decimal128** — numeric distinctions.
- **Binary** — raw bytes.
- **UUID** — universally unique identifier.

When you `JSON.stringify` a document, those types collapse to strings. Be careful round-tripping.

## The `_id` field

Every document has one. If you don't supply it, MongoDB generates an `ObjectId`. `_id` is automatically indexed and is the *only* field that's guaranteed unique unless you add other unique indexes.

```javascript
db.users.insertOne({ _id: "u_001", name: "Alice" });  // your own ID
db.users.insertOne({ name: "Bob" });                  // auto ObjectId
```

`ObjectId`s are sortable by creation time:

```javascript
db.users.find().sort({ _id: -1 }).limit(10);   // 10 newest
```

## Collections

A **collection** is a bag of documents. There's no enforced schema across them. You can:

```javascript
db.users.insertOne({ name: "Alice" });
db.users.insertOne({ name: "Bob", isAdmin: true });
db.users.insertOne({ nickname: "carol42", lastSeen: new Date() });
```

All three sit in `users`, with different fields.

## Schema validation (when you want it)

You can opt into validation per collection:

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email"],
      properties: {
        email: { bsonType: "string", pattern: "^.+@.+$" },
        loginCount: { bsonType: "int", minimum: 0 }
      }
    }
  }
});
```

Rejected writes throw on `insertOne`. Useful for hardening a core collection without losing flexibility everywhere else.

## Field naming rules

- Cannot start with `$`.
- Cannot contain `.` (that's the path separator).
- `_id` is reserved (you can write it, you can't reuse the value).

## Limits worth knowing

- Document size: **16 MB**. Files larger than that go in GridFS.
- Nested depth: **100 levels**.
- Database/collection name length: 64 bytes.

If your documents are pushing 16 MB, your schema probably wants reworking — not a bigger limit.
