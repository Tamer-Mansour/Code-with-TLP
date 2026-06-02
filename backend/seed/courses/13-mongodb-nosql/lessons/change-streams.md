# Change Streams in MongoDB

**Change streams** let your application subscribe to a real-time stream of data changes in a collection, database, or entire cluster. They are built on MongoDB's oplog and are available on replica sets and sharded clusters.

Common use cases:
- Invalidating an application-level cache when data changes.
- Pushing real-time updates to connected clients (WebSocket feeds).
- Triggering downstream workflows (e.g., send an email when an order status becomes `"shipped"`).
- Audit logging — record every write without touching application code that performs the writes.

## Opening a Change Stream

In `mongosh`:

```javascript
const stream = db.orders.watch();
while (!stream.isClosed()) {
  const change = stream.tryNext();
  if (change) printjson(change);
}
```

In Python (`pymongo`):

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
collection = client.shop.orders

with collection.watch() as stream:
    for change in stream:
        print(change)
```

## The Change Event Document

Each event document has a predictable shape:

```json
{
  "_id": { "_data": "..." },          // resume token
  "operationType": "insert",          // insert | update | replace | delete | ...
  "ns": { "db": "shop", "coll": "orders" },
  "documentKey": { "_id": "abc123" },
  "fullDocument": { "_id": "abc123", "status": "paid", "amount": 150 },
  "updateDescription": {              // only present for update events
    "updatedFields": { "status": "shipped" },
    "removedFields": []
  }
}
```

`operationType` values: `insert`, `update`, `replace`, `delete`, `drop`, `rename`, `dropDatabase`, `invalidate`.

## Filtering with Pipelines

Change streams accept an aggregation pipeline to filter or transform events before they reach your application:

```python
# Only react to order status changing to "shipped"
pipeline = [
  { "$match": {
      "operationType": "update",
      "updateDescription.updatedFields.status": "shipped"
  } }
]

with collection.watch(pipeline) as stream:
    for change in stream:
        order_id = change["documentKey"]["_id"]
        send_shipping_notification(order_id)
```

## Resume Tokens

If your application crashes, you do not need to replay all changes from the beginning. Store the `_id` (resume token) of the last event you processed:

```python
resume_token = None

with collection.watch(resume_after=resume_token) as stream:
    for change in stream:
        process(change)
        resume_token = change["_id"]   # persist to storage
```

On restart, pass the saved `resume_token` to `resume_after` and MongoDB will replay from exactly that point.

## Requirements and Limitations

| Requirement | Detail |
|---|---|
| Replica set or sharded cluster | Change streams are not available on standalone `mongod` |
| `fullDocument` | By default, update events do NOT include the full document (only changed fields). Pass `full_document="updateLookup"` to get it, but note it is a post-update lookup, not a snapshot. |
| Oplog window | If your application is offline longer than the oplog covers, the resume token becomes stale. Increase oplog size for long offline windows. |
| Permissions | The user needs `read` on the collection and `changeStream` privilege. |

Change streams are a powerful alternative to polling. A typical polling loop might query a collection every second and impose constant read load; a change stream only wakes up when something actually changes.
