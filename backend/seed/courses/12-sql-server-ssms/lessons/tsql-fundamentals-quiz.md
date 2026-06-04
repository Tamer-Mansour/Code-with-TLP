# Quiz: T-SQL Fundamentals and Data Retrieval

Test your understanding of SELECT basics, NULL handling, filtering, and aggregation in T-SQL.

**Q1. What does `WHERE price = NULL` return when some rows have a NULL price?**
- [ ] All rows where price is NULL
- [ ] All rows where price is not NULL
- [x] Zero rows — because NULL = NULL evaluates to UNKNOWN, not TRUE
- [ ] A syntax error

**Q2. Which operator correctly tests for a missing value in T-SQL?**
- [ ] `= NULL`
- [ ] `!= NULL`
- [x] `IS NULL`
- [ ] `== NULL`

**Q3. In T-SQL, string literals must be enclosed in:**
- [ ] Double quotes: `"Alice"`
- [x] Single quotes: `'Alice'`
- [ ] Backticks: `` `Alice` ``
- [ ] Either single or double quotes

**Q4. What is the result of `COALESCE(NULL, NULL, 42, NULL)`?**
- [ ] NULL
- [ ] 0
- [x] 42
- [ ] An error

**Q5. Which clause filters rows AFTER grouping (i.e., filters on aggregated values)?**
- [ ] WHERE
- [x] HAVING
- [ ] FILTER
- [ ] ON

**Q6. You want to find the top 5 highest-paid employees. Which T-SQL syntax is correct?**
- [ ] `SELECT LIMIT 5 * FROM dbo.employees ORDER BY salary DESC`
- [x] `SELECT TOP 5 * FROM dbo.employees ORDER BY salary DESC`
- [ ] `SELECT * FROM dbo.employees ORDER BY salary DESC LIMIT 5`
- [ ] `SELECT FIRST 5 * FROM dbo.employees ORDER BY salary DESC`

**Q7. Which aggregate function counts only non-NULL values in a column?**
- [ ] `COUNT(*)`
- [x] `COUNT(column_name)`
- [ ] `SUM(column_name)`
- [ ] Both COUNT(*) and COUNT(column_name) behave identically

**Q8. What does `BETWEEN 10 AND 20` mean in a WHERE clause?**
- [ ] Values strictly greater than 10 and strictly less than 20
- [x] Values from 10 to 20 inclusive (>= 10 AND <= 20)
- [ ] Values from 11 to 19 (exclusive on both ends)
- [ ] Values greater than 10 and less than or equal to 20

**Q9. What is the correct T-SQL syntax to get rows 11 through 20 (page 2 of 10 per page)?**
- [ ] `SELECT * FROM t LIMIT 10 OFFSET 10`
- [x] `SELECT * FROM t ORDER BY id OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY`
- [ ] `SELECT TOP 10 * FROM t WHERE id > 10`
- [ ] `SELECT * FROM t SKIP 10 TAKE 10`

**Q10. Which T-SQL function returns the current UTC date and time with high precision?**
- [ ] `GETDATE()`
- [ ] `NOW()`
- [x] `SYSUTCDATETIME()`
- [ ] `CURRENT_TIMESTAMP`
