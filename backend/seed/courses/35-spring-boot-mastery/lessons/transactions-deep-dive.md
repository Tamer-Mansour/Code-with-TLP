# Transactions Deep Dive: Propagation and Isolation

Spring's `@Transactional` looks simple, but two settings control almost everything about how it behaves under load: **propagation** (how a method joins or starts transactions) and **isolation** (how concurrent transactions see each other's data). Getting these right is the difference between correct, performant code and silent data corruption.

## How `@Transactional` Works

Spring wraps your bean in a proxy. When you call a `@Transactional` method from outside, the proxy opens a transaction, runs the method, then commits or rolls back. By default it rolls back on unchecked exceptions (`RuntimeException`, `Error`) and commits on checked exceptions.

```java
@Service
public class OrderService {

    @Transactional
    public Order placeOrder(Long customerId, List<Item> items) {
        Order order = orderRepository.save(new Order(customerId));
        inventoryService.reserve(items); // joins the same transaction by default
        return order;
    }
}
```

## Propagation

Propagation decides what happens when a transactional method is called while another transaction may already be running.

| Propagation     | If a transaction exists      | If none exists        |
|-----------------|------------------------------|-----------------------|
| `REQUIRED` (default) | Join it                  | Start a new one       |
| `REQUIRES_NEW`  | Suspend it, start a new one  | Start a new one       |
| `NESTED`        | Create a savepoint           | Start a new one       |
| `SUPPORTS`      | Join it                      | Run non-transactionally |
| `MANDATORY`     | Join it                      | Throw exception       |
| `NEVER`         | Throw exception              | Run non-transactionally |
| `NOT_SUPPORTED` | Suspend it                   | Run non-transactionally |

A classic use of `REQUIRES_NEW` is audit logging that must persist even if the main transaction rolls back:

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void logFailure(String reason) {
    auditRepository.save(new AuditEntry(reason)); // commits independently
}
```

## Isolation

Isolation governs which concurrency anomalies are possible: **dirty reads**, **non-repeatable reads**, and **phantom reads**.

| Isolation         | Dirty read | Non-repeatable read | Phantom read |
|-------------------|:---------:|:-------------------:|:------------:|
| `READ_UNCOMMITTED`| Yes       | Yes                 | Yes          |
| `READ_COMMITTED`  | No        | Yes                 | Yes          |
| `REPEATABLE_READ` | No        | No                  | Yes          |
| `SERIALIZABLE`    | No        | No                  | No           |

`Isolation.DEFAULT` uses the database's setting (PostgreSQL defaults to `READ_COMMITTED`; MySQL/InnoDB to `REPEATABLE_READ`). Override only when a specific invariant demands it, since stricter isolation means more locking and contention.

```java
@Transactional(isolation = Isolation.REPEATABLE_READ)
public BigDecimal computeStatement(Long accountId) {
    // Re-reads of the same rows return identical values for the whole method.
    return ledgerRepository.balanceFor(accountId);
}
```

## Common Mistakes and Best Practices

- **Self-invocation bypasses the proxy.** Calling `this.otherMethod()` inside the same bean does not start a new transaction. Move the method to another bean.
- **`@Transactional` on a `private` method is ignored** — the proxy can only intercept `public` methods.
- **Checked exceptions don't roll back by default.** Use `@Transactional(rollbackFor = Exception.class)` when needed.
- **`REQUIRES_NEW` suspends the outer transaction**, holding two connections at once — beware connection-pool exhaustion in loops.
- **`NESTED` requires JDBC savepoint support** and a `DataSourceTransactionManager`; it is not supported by JPA in all setups.
- **Keep transactions short.** Never make remote/HTTP calls inside an open transaction.

## Summary

Use `REQUIRED` and the database's default isolation for most code; reach for `REQUIRES_NEW` to commit work independently and raise isolation only to protect a specific invariant. Always remember the proxy boundary—self-calls and non-public methods silently skip transaction management.
