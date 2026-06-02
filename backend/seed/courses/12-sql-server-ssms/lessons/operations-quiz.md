# Quiz: SQL Server Operations

Test your knowledge of security, backups, and SQL Server Agent.

**Q1. In SQL Server, what is the difference between a Login and a User?**
- [ ] They are interchangeable terms
- [x] A Login is a server-level principal; a User is a database-level principal mapped to a Login
- [ ] A User has more privileges than a Login by default
- [ ] A Login belongs to a single database; a User belongs to the whole instance

**Q2. Which recovery model allows point-in-time restore by chaining transaction log backups?**
- [ ] Simple
- [ ] Bulk-Logged
- [x] Full
- [ ] Archive

**Q3. What does `BACKUP LOG SalesDB TO DISK = 'C:\backups\sales.trn'` do?**
- [ ] Performs a full database backup including only transaction logs
- [x] Backs up the transaction log and truncates the inactive portion of the log file
- [ ] Copies the .ldf file to disk
- [ ] Creates a snapshot backup of the log

**Q4. Which SQL Server Agent job step subsystem runs a T-SQL script?**
- [ ] CmdExec
- [ ] PowerShell
- [x] TSQL
- [ ] ActiveScripting

**Q5. Where does SQL Server Agent store its job configuration?**
- [ ] `master` database
- [ ] `model` database
- [x] `msdb` database
- [ ] `tempdb` database

**Q6. What does the `WITH (ONLINE = ON)` option in `ALTER INDEX ... REBUILD` enable?**
- [ ] Automatically updates statistics after the rebuild
- [x] Allows reads and writes to the table during the index rebuild (Enterprise Edition)
- [ ] Publishes the index definition to other servers
- [ ] Sends an email alert when the rebuild completes

**Q7. Which fragmentation percentage threshold is commonly used to decide between REORGANIZE and REBUILD?**
- [ ] 5 % for REBUILD, 15 % for REORGANIZE
- [x] 5–30 % for REORGANIZE, above 30 % for REBUILD
- [ ] Always use REBUILD regardless of fragmentation
- [ ] 50 % for REORGANIZE, 80 % for REBUILD

**Q8. A SQL Server Login is granted `db_datareader` role in a database. What can that Login do?**
- [ ] Insert, update, and delete rows
- [ ] Create tables and indexes
- [x] Read all user tables in the database
- [ ] Run BACKUP DATABASE commands
