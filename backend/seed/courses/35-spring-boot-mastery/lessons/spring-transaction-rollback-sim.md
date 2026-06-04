# Exercise: Transaction Rollback Simulator

Spring's `@Transactional` annotation provides ACID guarantees around database operations. One of its most important — and most misunderstood — behaviours is its **rollback policy**: by default, Spring rolls back on unchecked exceptions (`RuntimeException`) but **commits** on checked exceptions. This exercise makes that rule concrete.

## What you need to implement

Simulate transaction execution with two propagation levels:

- `REQUIRED` — join an existing outer transaction if one is active, or start a new one.
- `REQUIRES_NEW` — always start an independent transaction, regardless of any outer transaction.

When a `RUNTIME` exception is thrown, the current transaction rolls back (all writes in that transaction are discarded). When a `CHECKED` exception is thrown, the current transaction commits its writes normally.

## Real-world connection

```java
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

@Service
public class OrderService {

    @Transactional                                         // REQUIRED (default)
    public void placeOrder(Order order) {
        orderRepo.save(order);
        auditService.writeEntry("order placed");          // REQUIRES_NEW
        // if placeOrder throws RuntimeException → both roll back?
        // No — REQUIRES_NEW already committed audit entry
    }
}

@Service
public class AuditService {

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void writeEntry(String msg) {
        auditRepo.save(new AuditEntry(msg));
        // commits independently even if outer transaction rolls back
    }
}
```

Understanding `REQUIRES_NEW` is critical when writing audit logs, outbox records, or any operation that must persist regardless of the outer transaction's outcome.

> **Important:** Use `org.springframework.transaction.annotation.Transactional` — NOT `jakarta.transaction.Transactional`. The Spring annotation supports propagation, isolation, `readOnly`, `rollbackFor`, and `noRollbackFor` attributes that the Jakarta one does not.

## Input format

```
T
TRANSACTION propagation
WRITE key value
...
THROW ExceptionType
END
...
```

- First line: `T` — number of transactions.
- Each transaction starts with `TRANSACTION REQUIRED` or `TRANSACTION REQUIRES_NEW`.
- `WRITE key value` — records a key-value pair in the current transaction's buffer.
- `THROW RUNTIME` or `THROW CHECKED` — triggers an exception; the transaction handles it per the rollback rules.
- `END` — ends the transaction block.

## Output format

After all transactions execute, print the **final committed state** as `key=value` lines sorted alphabetically by key. If nothing was committed, print `EMPTY`.

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

The first transaction (REQUIRED, no outer context) rolls back because of `RUNTIME`. The second transaction (REQUIRES_NEW) commits because `CHECKED` exceptions do not trigger rollback.

## Further reading

- [Spring Boot Reference — Transaction Management](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Spring Boot Community eBook](https://riptutorial.com/ebook/spring-boot) — covers `@Transactional` propagation and isolation levels
