# Transaction Rollback Simulator

Transactions are the unit of atomic work in MySQL. When something goes wrong mid-transaction, `ROLLBACK` undoes every change back to a known-good state. `SAVEPOINT` lets you create checkpoints within a transaction so you can roll back to an intermediate state without abandoning everything.

## The transaction commands

```sql
START TRANSACTION;          -- begin a new transaction

INSERT INTO accounts VALUES ('Alice', 1000);
SAVEPOINT after_alice;      -- checkpoint here

INSERT INTO accounts VALUES ('Bob', 2000);
DELETE FROM accounts WHERE name = 'Bob';

ROLLBACK TO SAVEPOINT after_alice;   -- undo back to checkpoint
-- Bob is gone again; Alice still exists

INSERT INTO accounts VALUES ('Dave', 4000);
COMMIT;                     -- finalize: Alice + Dave survive
```

## ACID reminder

| Property    | What it guarantees                                              |
|-------------|----------------------------------------------------------------|
| Atomic      | All or nothing — partial commits cannot exist                  |
| Consistent  | Constraints hold before and after each transaction             |
| Isolated    | Concurrent transactions don't see each other's partial work    |
| Durable     | Committed data survives server crashes (via InnoDB redo log)   |

## InnoDB vs MyISAM — a critical difference

**MyISAM does NOT support transactions.** This is not a minor quirk — it means:

- `ROLLBACK` has no effect on MyISAM tables.
- There is no crash recovery for MyISAM writes.
- Foreign key constraints are silently ignored on MyISAM.

InnoDB has been the MySQL default since version 5.5. Always use InnoDB for tables that need transactional integrity.

## SAVEPOINT behavior in detail

- `SAVEPOINT sp_name` — saves a snapshot of current transaction state.
- `ROLLBACK TO SAVEPOINT sp_name` — reverts to that snapshot; the transaction continues (not committed yet).
- `RELEASE SAVEPOINT sp_name` — discards a savepoint (freeing memory; optional).
- `COMMIT` finalizes all remaining work and releases all savepoints.

## This exercise

Implement the transaction log interpreter: process `BEGIN`, `INSERT`, `DELETE`, `SAVEPOINT`, `ROLLBACK_TO_SAVEPOINT`, `COMMIT`, and `ROLLBACK` commands and output the final table state.

## Further reading

- *MIT OCW 1.264J*, Lecture 15: SQL Transactions — https://ocw.mit.edu/courses/1-264j-database-internet-and-systems-integration-technologies-fall-2013/
- *MIT OCW 6.830: Database Systems* — Transaction processing chapter — https://ocw.mit.edu/courses/6-830-database-systems-fall-2010/
