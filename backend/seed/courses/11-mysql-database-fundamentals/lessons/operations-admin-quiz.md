# Quiz: Operations, Users, and Backups

**Q1. Which statement creates a new MySQL user that can connect only from localhost?**
- [ ] `ADD USER 'alice'@'localhost' WITH PASSWORD 'secret';`
- [x] `CREATE USER 'alice'@'localhost' IDENTIFIED BY 'secret';`
- [ ] `INSERT INTO mysql.users VALUES ('alice', 'localhost', PASSWORD('secret'));`
- [ ] `GRANT USER 'alice'@'localhost' PASSWORD 'secret';`

**Q2. You want to give user `alice` read-only access to the `shop` database. Which command is correct?**
- [ ] `GRANT ALL ON shop.* TO 'alice'@'localhost';`
- [x] `GRANT SELECT ON shop.* TO 'alice'@'localhost';`
- [ ] `ALLOW SELECT ON shop TO 'alice';`
- [ ] `SET PERMISSION SELECT ON shop FOR 'alice';`

**Q3. After granting or revoking privileges, which command ensures changes take effect immediately?**
- [ ] `COMMIT;`
- [ ] `RELOAD PRIVILEGES;`
- [x] `FLUSH PRIVILEGES;`
- [ ] `REFRESH GRANTS;`

**Q4. `mysqldump` creates:**
- [ ] A binary snapshot of the InnoDB tablespace files
- [x] A text file of SQL statements (CREATE TABLE + INSERT) that recreates the database
- [ ] A compressed archive of the MySQL data directory
- [ ] A replication binlog file

**Q5. Which `mysqldump` flag also exports the database structure (CREATE TABLE) in addition to data?**
- [x] By default, mysqldump exports both structure and data; use `--no-data` to exclude data
- [ ] `--schema-only`
- [ ] `--with-ddl`
- [ ] `--include-create`

**Q6. In MySQL replication, the replica reads events from the primary's:**
- [ ] InnoDB redo log
- [x] Binary log (binlog)
- [ ] Slow query log
- [ ] General query log

**Q7. REVOKE is used to:**
- [ ] Delete a user account from MySQL
- [x] Remove specific privileges previously granted to a user
- [ ] Reset a user's password
- [ ] Disable a user's account temporarily

**Q8. Which tool performs a faster, non-blocking physical backup of InnoDB files (compared to mysqldump)?**
- [ ] `mysqlexport`
- [x] `mysqlbackup` (MySQL Enterprise Backup) or `xtrabackup` (Percona, open source)
- [ ] `mysqldump --fast`
- [ ] `cp -r /var/lib/mysql`
