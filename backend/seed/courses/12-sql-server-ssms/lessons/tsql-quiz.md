# Quiz: T-SQL Essentials

Test your understanding of T-SQL syntax, joins, stored procedures, and string functions.

**Q1. Which keyword limits rows returned in T-SQL instead of `LIMIT` (used in MySQL/PostgreSQL)?**
- [ ] ROWNUM
- [x] TOP
- [ ] FETCH
- [ ] LIMIT

**Q2. What does `COALESCE(NULL, NULL, 'fallback')` return?**
- [ ] NULL
- [ ] An error
- [x] 'fallback'
- [ ] 0

**Q3. Which join type keeps ALL rows from the left table, even when there is no match on the right?**
- [ ] INNER JOIN
- [x] LEFT JOIN
- [ ] CROSS JOIN
- [ ] FULL JOIN

**Q4. What does `CROSS APPLY` do in T-SQL?**
- [ ] Creates a Cartesian product of two physical tables
- [ ] Applies a filter across all databases
- [x] Invokes a table-valued expression for each row of the outer query
- [ ] Merges two result sets with no duplicates

**Q5. What is the correct way to re-raise a caught error in modern T-SQL (SQL Server 2012+)?**
- [ ] `RAISERROR(@@ERROR, 16, 1)`
- [ ] `RETURN -1`
- [x] `THROW`
- [ ] `SIGNAL SQLSTATE '45000'`

**Q6. Which function splits a delimited string into a set of rows (available from SQL Server 2016)?**
- [ ] SPLIT_STRING
- [x] STRING_SPLIT
- [ ] PARSENAME
- [ ] CHARINDEX

**Q7. `SET NOCOUNT ON` inside a stored procedure does what?**
- [ ] Prevents the procedure from returning result sets
- [x] Suppresses "N rows affected" messages sent to the client
- [ ] Disables row counting in GROUP BY
- [ ] Turns off auto-commit

**Q8. Which function concatenates multiple row values into a single delimited string (SQL Server 2017+)?**
- [ ] CONCAT_WS
- [ ] GROUP_CONCAT
- [x] STRING_AGG
- [ ] LISTAGG

**Q9. What does `@@TRANCOUNT` hold?**
- [ ] The number of rows in the most recent INSERT
- [x] The nesting depth of open transactions
- [ ] The number of open connections
- [ ] The lock count for the current session

**Q10. An inline table-valued function (iTVF) is preferred over a scalar UDF for performance because:**
- [ ] It runs in a separate process
- [ ] It disables locking
- [x] The optimizer can inline it, enabling set-based execution and parallelism
- [ ] It compiles to native code automatically
