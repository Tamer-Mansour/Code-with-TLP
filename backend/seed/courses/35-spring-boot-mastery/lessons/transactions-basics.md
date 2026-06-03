# Transactions with @Transactional

A *transaction* groups multiple database operations into a single atomic unit: either every change commits, or none do. In Spring Data JPA you rarely manage transactions by hand. Instead, you declare them with the `@Transactional` annotation and let Spring's transaction manager handle `begin`, `commit`, and `rollback` around your method.

## Why transactions matter

Consider transferring money between two accounts. Two updates must happen together — debit one, credit the other. If the second fails, the first must be undone, or money simply disappears.

```java
@Service
public class TransferService {

    private final AccountRepository accounts;

    public TransferService(AccountRepository accounts) {
        this.accounts = accounts;
    }

    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accounts.findById(fromId).orElseThrow();
        Account to = accounts.findById(toId).orElseThrow();

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));
        // No explicit save() needed: managed entities are flushed at commit.
    }
}
```

If any line throws, Spring rolls back both balance changes. The method runs inside one persistence context, so dirty-checked changes flush automatically on commit.

## Enabling transactions

Spring Boot auto-configures a `PlatformTransactionManager` when JPA is on the classpath — no extra setup is needed. Just place the annotation from the correct package:

```java
import org.springframework.transaction.annotation.Transactional; // use THIS one
// NOT jakarta.transaction.Transactional
```

## Rollback rules

A common surprise: by default Spring only rolls back on **unchecked** exceptions (`RuntimeException`, `Error`). Checked exceptions commit unless you say otherwise.

| Exception thrown                 | Default behaviour |
|----------------------------------|-------------------|
| `RuntimeException` / subclass     | Rollback          |
| `Error`                          | Rollback          |
| Checked `Exception` (e.g. `IOException`) | **Commit**  |

Override with `rollbackFor` / `noRollbackFor`:

```java
@Transactional(rollbackFor = IOException.class)
public void process() throws IOException { ... }
```

## Read-only transactions

For pure queries, mark the method read-only. This lets the JPA provider skip dirty checking and hints the driver/connection pool for optimizations.

```java
@Transactional(readOnly = true)
public List<Account> listAccounts() {
    return accounts.findAll();
}
```

## Propagation in brief

`propagation` controls what happens when a transactional method calls another. The defaults are sensible; the most useful values:

- `REQUIRED` (default) — join the existing transaction, or start one.
- `REQUIRES_NEW` — suspend the current transaction and run in a fresh, independent one (e.g. writing an audit log that must persist even if the outer call rolls back).

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void writeAuditEntry(String message) { ... }
```

## Common mistakes and best practices

- **Self-invocation does nothing.** Spring proxies the bean, so calling a `@Transactional` method from another method *in the same class* bypasses the proxy. Move the method to a separate bean.
- **`private` methods are ignored.** The proxy can only intercept `public` methods.
- **Annotate the service layer, not repositories.** Keep business operations as the transactional boundary.
- **Catching exceptions silently** prevents rollback — if you swallow a `RuntimeException`, Spring never sees it and commits the partial work.
- **Keep transactions short.** Avoid remote calls or slow I/O inside them; they hold a DB connection and locks.

## Summary

`@Transactional` makes a method atomic, committing on success and rolling back on unchecked exceptions. Annotate `public` service methods, remember the checked-exception rollback rule, and use `readOnly` and `REQUIRES_NEW` where they fit.
