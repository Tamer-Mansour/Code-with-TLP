# Quiz: DDL, Schema Design, and DML

Test your understanding of table design, constraints, normalization, and safe data manipulation.

**Q1. Which constraint ensures that a column's value matches a value from another table's primary key?**
- [ ] UNIQUE
- [ ] CHECK
- [x] FOREIGN KEY
- [ ] NOT NULL

**Q2. A table in SQL Server can have at most how many clustered indexes?**
- [ ] Unlimited
- [ ] 2
- [x] 1
- [ ] 249 (same as nonclustered limit)

**Q3. You run `UPDATE dbo.employees SET salary = 100000` without a WHERE clause. What happens?**
- [ ] SQL Server raises an error because WHERE is required
- [ ] Only the first row is updated
- [x] Every row in the table is updated to salary = 100000
- [ ] Nothing — SQL Server ignores updates without WHERE

**Q4. Which normal form eliminates partial dependencies (where a non-key column depends on only part of a composite primary key)?**
- [ ] First Normal Form (1NF)
- [x] Second Normal Form (2NF)
- [ ] Third Normal Form (3NF)
- [ ] Boyce-Codd Normal Form (BCNF)

**Q5. What is the key difference between `DELETE FROM t` and `TRUNCATE TABLE t`?**
- [ ] DELETE removes columns; TRUNCATE removes rows
- [ ] TRUNCATE can use a WHERE clause; DELETE cannot
- [x] TRUNCATE is minimally logged, resets IDENTITY, and cannot fire triggers; DELETE is fully logged and fires triggers
- [ ] They are functionally identical

**Q6. Which data type should you use for a price column that requires exact decimal arithmetic (e.g., $9.99)?**
- [ ] FLOAT
- [ ] REAL
- [x] DECIMAL(10,2)
- [ ] MONEY (never use it — rounding issues)

**Q7. When you declare `IDENTITY(1,1)` on a column, what does SQL Server do?**
- [ ] Requires the application to supply a unique integer on each insert
- [x] Automatically generates a sequential integer starting at 1, incrementing by 1
- [ ] Creates a UUID (GUID) for each row
- [ ] Applies a UNIQUE constraint only — no auto-generation

**Q8. Which statement correctly adds a new nullable column to an existing table?**
- [ ] `CREATE COLUMN dbo.products.weight DECIMAL(8,3) NULL`
- [ ] `MODIFY TABLE dbo.products ADD weight DECIMAL(8,3) NULL`
- [x] `ALTER TABLE dbo.products ADD weight DECIMAL(8,3) NULL`
- [ ] `UPDATE TABLE dbo.products ADD COLUMN weight DECIMAL(8,3) NULL`

**Q9. In a many-to-many relationship (e.g., orders and products), how is the relationship typically represented in SQL Server?**
- [ ] By adding a comma-separated column to one of the tables
- [ ] By combining both tables into one denormalized table
- [x] By creating a junction (bridge) table with foreign keys to both parent tables
- [ ] By using CROSS JOIN at query time

**Q10. The ACID property that guarantees committed data survives a server restart is:**
- [ ] Atomicity
- [ ] Consistency
- [ ] Isolation
- [x] Durability
