# Quiz: PostgreSQL Operations

**Q1. What does the Write-Ahead Log (WAL) protect against?**
- [ ] Concurrent writes causing data races between transactions
- [ ] Disk-full errors when tables grow unexpectedly
- [x] Data loss on a crash: every committed change is written to WAL before the data pages are flushed, so the database can replay WAL to recover
- [ ] Bloat from dead tuples accumulating faster than autovacuum can remove them

**Q2. `pg_dump` creates a logical backup. Which of the following is TRUE about it?**
- [ ] It takes a consistent snapshot using an exclusive lock on all tables
- [x] It uses `REPEATABLE READ` isolation to capture a consistent view of the database without blocking other transactions
- [ ] It can only back up a single table at a time
- [ ] It is the only tool that supports Point-in-Time Recovery (PITR)

**Q3. Point-in-Time Recovery (PITR) requires:**
- [ ] A `pg_dump` file and the PostgreSQL binary
- [x] A base backup (`pg_basebackup`) plus a continuous WAL archive
- [ ] Streaming replication with at least one standby server
- [ ] The `pg_stat_statements` extension to be loaded

**Q4. In streaming replication, the standby server is:**
- [ ] An independent database that receives periodic `pg_dump` snapshots
- [ ] A hot standby that replicates at the logical (row change) level using triggers
- [x] A physical copy of the primary that replays WAL records streamed in real time
- [ ] A pgBouncer instance that caches query results from the primary

**Q5. pgBouncer's `transaction` pooling mode means:**
- [ ] Each client gets a dedicated backend connection for the duration of the session
- [x] A backend connection is allocated per transaction and returned to the pool after each `COMMIT` or `ROLLBACK`
- [ ] All clients share a single backend connection and queries are serialized
- [ ] pgBouncer automatically retries failed transactions on behalf of the client

**Q6. Which view shows currently running queries and their states in PostgreSQL?**
- [ ] `pg_stat_replication`
- [ ] `pg_stat_user_tables`
- [x] `pg_stat_activity`
- [ ] `information_schema.routines`
