# updateOne, updateMany, deleteMany

Mongo writes come in `One` and `Many` flavors. The difference is whether the write stops after the first match or affects all matches.

## updateOne / updateMany

```javascript
db.users.updateOne(
  { _id: ObjectId("...") },
  { $set: { lastLogin: new Date(), loginCount: 5 } }
);

db.users.updateMany(
  { isActive: false },
  { $set: { isArchived: true } }
);
```

The second argument is an **update document** with **update operators** — never a raw replacement (unless you use `replaceOne`).

## Update operators

| Operator      | What it does                                  |
|---------------|-----------------------------------------------|
| `$set`        | Set/overwrite a field                         |
| `$unset`      | Remove a field                                |
| `$inc`        | Increment numeric field                       |
| `$mul`        | Multiply                                      |
| `$min`/`$max` | Update only if new value is smaller/larger    |
| `$push`       | Append to an array                            |
| `$addToSet`   | Append if not already present                 |
| `$pull`       | Remove matching values from an array          |
| `$rename`     | Rename a field                                |

```javascript
db.users.updateOne(
  { _id: u },
  {
    $inc: { loginCount: 1 },
    $set: { lastLogin: new Date() },
    $push: { recentIps: "10.0.0.1" }
  }
);
```

## Atomic updates

A single `updateOne` is atomic on a single document — `$inc` and `$push` won't lose updates under concurrency, where a read-modify-write from the application would.

## Upsert

`upsert: true` says "insert if no document matches":

```javascript
db.counters.updateOne(
  { _id: "users" },
  { $inc: { value: 1 } },
  { upsert: true }
);
```

## findAndModify variants

When you need the document back:

```javascript
const doc = db.tasks.findOneAndUpdate(
  { status: "queued" },
  { $set: { status: "running", startedAt: new Date() } },
  { returnDocument: "after", sort: { priority: -1 } }
);
```

Useful for queue-style patterns.

## deleteOne / deleteMany

```javascript
db.users.deleteOne({ _id: ObjectId("...") });
db.users.deleteMany({ isArchived: true });
```

There's no soft-delete by default. If you want one, set a `deletedAt` field and filter on it everywhere.

## Bulk writes

For mixed batches, `bulkWrite`:

```javascript
db.orders.bulkWrite([
  { insertOne: { document: { _id: 1, total: 10 } } },
  { updateOne: { filter: { _id: 2 }, update: { $inc: { total: 5 } } } },
  { deleteOne: { filter: { _id: 3 } } }
], { ordered: false });
```

`ordered: false` lets MongoDB parallelize, but a failure mid-batch doesn't stop the rest.

## Watch out

- A `find()` followed by an `updateOne()` from application code is **not atomic**. Either use a single update operator, or wrap in a transaction.
- `updateMany` with no filter (`{}`) updates everything. The shell yells at you if `safeMode` is on; in code, double-check your filter object.
