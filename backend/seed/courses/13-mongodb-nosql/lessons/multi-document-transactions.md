# Multi-Document Transactions in MongoDB

For years, MongoDB was criticized for lacking multi-document ACID guarantees. Since version 4.0 (2018), full multi-document transactions are supported on replica sets, and since 4.2 they work across sharded clusters too.

## When You Need Transactions

Single-document operations in MongoDB are always atomic. A single `updateOne` either fully applies or does not — no partial writes. For many use cases, smart schema design (embedding related data in one document) eliminates the need for transactions entirely.

You need multi-document transactions when you must atomically modify **two or more separate documents** and cannot denormalize them. Classic examples:

- Transferring funds between two account documents.
- Creating an order document and decrementing inventory in a product document simultaneously.
- Writing an audit-log entry and updating a status record together.

## Starting a Session and Transaction

Transactions require a **client session**. In `mongosh`:

```javascript
const session = db.getMongo().startSession();
session.startTransaction({
  readConcern:  { level: "snapshot" },
  writeConcern: { w: "majority" }
});

try {
  const accounts = session.getDatabase("bank").accounts;

  accounts.updateOne(
    { _id: "alice" },
    { $inc: { balance: -200 } },
    { session }
  );

  accounts.updateOne(
    { _id: "bob" },
    { $inc: { balance: 200 } },
    { session }
  );

  session.commitTransaction();
  console.log("Transfer complete");
} catch (err) {
  session.abortTransaction();
  console.error("Rolled back:", err.message);
} finally {
  session.endSession();
}
```

Key points:
- Pass `{ session }` to **every** operation inside the transaction.
- Call `commitTransaction()` on success, `abortTransaction()` on error.
- Always call `endSession()` in a `finally` block.

## Read and Write Concerns

| Concern | Recommended Value | Why |
|---|---|---|
| `readConcern` | `snapshot` | Reads a consistent snapshot of committed data at transaction start |
| `writeConcern` | `majority` | Write is acknowledged by a majority of replica-set members before commit |

Using `snapshot` + `majority` gives you the strongest guarantees and avoids dirty reads.

## Limitations to Know

- **Max 16 MB** of data written per transaction.
- **Max 60 seconds** for a transaction to complete (configurable with `transactionLifetimeLimitSeconds`).
- Transactions carry overhead. If a single-document operation or a redesigned schema solves the problem, prefer that.
- DDL (creating collections, adding indexes) cannot be done inside a transaction in most cases.
- On sharded clusters, all shards involved must be reachable — a partial failure aborts the entire transaction.

## Application-Level Pattern: Retry Logic

MongoDB drivers recommend wrapping transactions in a **retry loop**, because a transaction may abort due to a transient write conflict or network blip.

```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

client = MongoClient("mongodb://localhost:27017/")

def run_transfer(session):
    with session.start_transaction():
        accounts = client.bank.accounts
        accounts.update_one({"_id": "alice"}, {"$inc": {"balance": -200}}, session=session)
        accounts.update_one({"_id": "bob"},   {"$inc": {"balance":  200}}, session=session)

with client.start_session() as session:
    while True:
        try:
            run_transfer(session)
            break
        except (ConnectionFailure, OperationFailure) as exc:
            if exc.has_error_label("TransientTransactionError"):
                continue   # retry
            raise
```

The `TransientTransactionError` label signals safe-to-retry situations. The driver does most of this automatically if you use the `with_transaction()` helper, which is the preferred approach in production drivers.
