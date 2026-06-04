# Quiz: MVCC, Transactions, and Vacuum

**Q1. When PostgreSQL executes an `UPDATE`, what physically happens to the old row version?**
- [ ] It is overwritten in-place with the new data
- [ ] It is moved to a separate undo log and deleted after commit
- [x] It remains on disk with its `xmax` set to the current transaction ID, making it a dead tuple
- [ ] It is immediately removed if no other transactions are reading it

**Q2. Which statement about `VACUUM` is TRUE?**
- [ ] `VACUUM` rewrites the table to a new file and returns disk space to the OS
- [x] `VACUUM` marks dead tuple space as reusable by future inserts but does NOT shrink the physical file
- [ ] `VACUUM` is equivalent to `DELETE` followed by `INSERT` for each updated row
- [ ] `VACUUM` acquires an exclusive lock on the table while it runs

**Q3. What is the risk of skipping `VACUUM` on a heavily updated table for too long?**
- [ ] The table will be automatically dropped by Postgres after 30 days
- [ ] Queries will start returning incorrect results due to stale snapshots
- [x] Transaction ID (xid) wraparound: Postgres may refuse all writes until a manual `VACUUM FREEZE` is run
- [ ] The autovacuum process will crash the Postgres cluster

**Q4. PostgreSQL's default transaction isolation level is:**
- [x] READ COMMITTED
- [ ] REPEATABLE READ
- [ ] SERIALIZABLE
- [ ] READ UNCOMMITTED

**Q5. At `READ COMMITTED` isolation level, a phantom read is:**
- [ ] Impossible — Postgres prevents phantom reads at all isolation levels
- [ ] Impossible — Postgres uses MVCC so all reads are always consistent
- [x] Possible — each statement gets a fresh snapshot, so a re-executed range query can see rows inserted by other committed transactions
- [ ] Impossible — the default level is REPEATABLE READ, which prevents phantom reads

**Q6. Two transactions both execute `SELECT ... FOR UPDATE` on the same row, each trying to acquire a write lock. What happens?**
- [ ] Postgres raises an error immediately for the second transaction
- [ ] Both transactions proceed; the last writer wins
- [x] The second transaction blocks until the first commits or rolls back, then acquires the lock
- [ ] Postgres automatically merges the two updates into one

**Q7. `autovacuum_vacuum_scale_factor = 0.20` means:**
- [ ] Autovacuum runs every 20 seconds
- [ ] Autovacuum uses at most 20% of system resources
- [x] Autovacuum triggers a vacuum when dead tuples exceed 20% of the live tuple count
- [ ] Autovacuum vacuums 20% of the table each run
