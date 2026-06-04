# Dependency Injection Container Simulator

Spring's IoC container resolves beans by type and wires them together. Simulate a minimal DI container.

Read **N** bean definitions, each as:
```
BeanName ClassName dep1 dep2 ...
```
where `dep1 dep2 ...` are optional dependency bean names (other bean names in the list). Each bean name and class name are single words with no spaces.

Then read a single bean name to resolve.

Print the **instantiation order** (topological sort) needed to fully wire that bean, one class name per line — deepest dependencies first, requested bean last.

If a **circular dependency** exists in the resolution chain, print:
```
CIRCULAR DEPENDENCY
```

## Input format

```
N
BeanName1 ClassName1 [dep1 dep2 ...]
BeanName2 ClassName2 [dep1 dep2 ...]
...
targetBeanName
```

## Output format

One class name per line in instantiation order, or `CIRCULAR DEPENDENCY`.

## Example

**Input:**
```
4
orderService OrderService orderRepository emailService
orderRepository JdbcOrderRepository
emailService SmtpEmailService
auditService AuditService orderService
orderService
```

**Output:**
```
JdbcOrderRepository
SmtpEmailService
OrderService
```
