# Quiz: Transactions and Concurrency

**Q1. Which ACID property guarantees that a committed transaction survives a server crash?**
- [ ] Atomicity
- [ ] Consistency
- [ ] Isolation
- [x] Durability

**Q2. What is MySQL InnoDB's default transaction isolation level?**
- [ ] READ UNCOMMITTED
- [ ] READ COMMITTED
- [x] REPEATABLE READ
- [ ] SERIALIZABLE

**Q3. A "dirty read" means:**
- [ ] Reading a row that has been deleted by another committed transaction
- [x] Reading a row that another transaction has modified but not yet committed
- [ ] Reading the same row twice and getting different values within one transaction
- [ ] Reading a row that requires a full table scan

**Q4. You issue `SELECT balance FROM accounts WHERE id = 1` inside a transaction. Another concurrent transaction then updates and commits that row. If you run the same SELECT again in the same transaction under REPEATABLE READ, what do you see?**
- [x] The original value from when your transaction started (snapshot read)
- [ ] The updated value committed by the other transaction
- [ ] An error — MySQL detects the conflict
- [ ] NULL, because the row is locked

**Q5. Which statement correctly acquires an exclusive row lock in InnoDB?**
- [ ] `SELECT * FROM orders WHERE id = 1;`
- [ ] `SELECT * FROM orders WHERE id = 1 FOR SHARE;`
- [x] `SELECT * FROM orders WHERE id = 1 FOR UPDATE;`
- [ ] `LOCK TABLE orders WRITE;`

**Q6. InnoDB detects a deadlock and kills one of the transactions. What error code does it return?**
- [ ] 1040
- [ ] 1205
- [x] 1213
- [ ] 1064

**Q7. What does MVCC (Multi-Version Concurrency Control) allow in InnoDB?**
- [ ] Two transactions to write to the same row simultaneously
- [x] Readers to see a consistent snapshot without blocking writers
- [ ] Automatic retries on deadlock
- [ ] Automatic selection of the best isolation level per query
