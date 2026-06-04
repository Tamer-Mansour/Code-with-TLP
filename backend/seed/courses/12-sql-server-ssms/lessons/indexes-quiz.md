# Quiz: Indexes and Execution Plans

Test your understanding of SQL Server index types, design trade-offs, and execution plan analysis.

**Q1. How many clustered indexes can a single SQL Server table have?**
- [ ] Unlimited
- [ ] Up to 249
- [x] Exactly 1 (or 0 if the table is a heap)
- [ ] Up to 32

**Q2. What does a clustered index actually define about a table?**
- [ ] A sorted copy of selected columns stored separately
- [x] The physical storage order of the actual data rows in the table
- [ ] A hash map from the key to the row location
- [ ] A compressed snapshot of the table for read-only queries

**Q3. A nonclustered index row locator (for a table with a clustered index) contains:**
- [ ] The physical page address and slot number of the data row
- [x] The clustered index key value, which is used to do a key lookup into the clustered index
- [ ] A full copy of the row
- [ ] The ROWID from an internal heap pointer

**Q4. What is a "covering index" in SQL Server?**
- [ ] An index that automatically covers all columns
- [ ] An index used during a full table scan
- [x] A nonclustered index that includes all columns needed by a query, eliminating the need for a key lookup
- [ ] A clustered index with a filtered WHERE clause

**Q5. Which SSMS shortcut displays the ACTUAL (post-execution) execution plan?**
- [ ] Ctrl+L (Estimated Plan)
- [x] Ctrl+M (Include Actual Execution Plan, then run the query)
- [ ] Ctrl+K
- [ ] F7

**Q6. The execution plan operator with the highest cost percentage should be investigated first because:**
- [x] It indicates where the query spends the most work, making it the best target for optimization
- [ ] SQL Server always estimates it incorrectly
- [ ] It always indicates a missing index
- [ ] It represents the most recently executed step

**Q7. Adding too many indexes on a table primarily hurts:**
- [ ] SELECT query performance
- [ ] Backup size
- [x] Write (INSERT, UPDATE, DELETE) performance, since each index must be maintained
- [ ] Connection pool availability

**Q8. Which DMV helps identify indexes that SQL Server itself predicts would improve query performance?**
- [ ] `sys.dm_exec_query_stats`
- [ ] `sys.dm_os_wait_stats`
- [x] `sys.dm_db_missing_index_details`
- [ ] `sys.dm_exec_cached_plans`

**Q9. A "Key Lookup" operator in an execution plan indicates:**
- [ ] A query that uses only the primary key
- [x] An additional B-tree traversal into the clustered index to retrieve columns not included in the nonclustered index
- [ ] A join between two tables on a foreign key
- [ ] A full table scan of the clustered index

**Q10. Which statement about IDENTITY columns is correct?**
- [ ] You can freely insert custom values into IDENTITY columns without any extra steps
- [ ] IDENTITY columns guarantee values are contiguous with no gaps
- [x] Gaps can occur in IDENTITY sequences (e.g., after a rollback or failed insert)
- [ ] Each table can have multiple IDENTITY columns
