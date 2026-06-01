# Quiz: Postgres Basics

**Q1. The default TCP port for PostgreSQL is:**
- [ ] 3306
- [x] 5432
- [ ] 1433
- [ ] 27017

**Q2. Which file maps client hosts and auth methods?**
- [ ] `postgresql.conf`
- [x] `pg_hba.conf`
- [ ] `pg_ident.conf`
- [ ] `auth.conf`

**Q3. In psql, what does `\d users` do?**
- [ ] Drops the table
- [x] Describes the table (columns, indexes, constraints)
- [ ] Deletes all rows
- [ ] Dumps the table as SQL

**Q4. PostgreSQL's concurrency model is called:**
- [ ] Row locking
- [ ] Snapshot isolation only
- [x] MVCC (Multi-Version Concurrency Control)
- [ ] Optimistic locking

**Q5. Which is NOT a built-in Postgres type?**
- [ ] JSONB
- [ ] tsvector
- [x] DOCUMENT
- [ ] inet

**Q6. The right way to install PostGIS in a database is:**
- [ ] `apt install postgis`
- [x] `CREATE EXTENSION postgis;`
- [ ] `INSTALL EXTENSION postgis;`
- [ ] `LOAD postgis;`
