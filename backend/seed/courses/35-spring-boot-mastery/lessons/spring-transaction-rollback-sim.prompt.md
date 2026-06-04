# Transaction Rollback Simulator

Spring's `@Transactional` rolls back on `RuntimeException` (unchecked) but **commits** on checked `Exception` by default. Simulate transaction execution.

Read **T** transactions. Each transaction starts with:
```
TRANSACTION propagation
```
where `propagation` is `REQUIRED` or `REQUIRES_NEW`.

Then read operations until `END`:
- `WRITE key value` — records a write in the current transaction's buffer.
- `THROW ExceptionType` — throws an exception; `ExceptionType` is `RUNTIME` or `CHECKED`.

**Propagation rules:**
- `REQUIRES_NEW` — always an independent transaction. Commits unless `RUNTIME` is thrown; rolls back (discards writes) on `RUNTIME`.
- `REQUIRED` — if no outer transaction is active, behaves as the outer transaction. Commits unless `RUNTIME` is thrown; rolls back on `RUNTIME`. (For this problem, each `REQUIRED` transaction is independent — there is no nesting between separate transactions in the input.)

After all transactions, print the **final committed state** as `key=value` lines sorted alphabetically by key. If nothing was committed, print `EMPTY`.

## Input format

```
T
TRANSACTION propagation
WRITE key value
...
[THROW ExceptionType]
END
...
```

## Output format

`key=value` lines sorted by key, or `EMPTY`.

## Example

**Input:**
```
2
TRANSACTION REQUIRED
WRITE balance 500
WRITE name Alice
THROW RUNTIME
END
TRANSACTION REQUIRES_NEW
WRITE balance 200
WRITE city London
THROW CHECKED
END
```

**Output:**
```
balance=200
city=London
```
