# Quiz: Schema Design and Normalization

**Q1. A table violates 1NF if:**
- [ ] It has more than one primary key column
- [x] A column stores multiple values in a single cell (e.g., comma-separated)
- [ ] It has NULL values in non-key columns
- [ ] It uses VARCHAR instead of TEXT

**Q2. Which constraint prevents inserting a row in `orders` if the referenced `user_id` doesn't exist in `users`?**
- [ ] `UNIQUE KEY (user_id)`
- [ ] `NOT NULL`
- [x] `FOREIGN KEY (user_id) REFERENCES users(id)`
- [ ] `CHECK (user_id > 0)`

**Q3. You have a table `orders(order_id, customer_name, customer_email, product_id, total)`. What normal form violation exists?**
- [x] 2NF — customer_name and customer_email depend on the customer, not the order
- [ ] 1NF — the table has repeating groups
- [ ] 3NF — total is a transitive dependency
- [ ] No violation; this is well-designed

**Q4. What does `ON DELETE CASCADE` do on a foreign key?**
- [ ] It prevents deletion of the parent row if children exist
- [ ] It sets the foreign key column to NULL when the parent is deleted
- [x] It automatically deletes all child rows when the parent row is deleted
- [ ] It raises an error and rolls back the transaction

**Q5. Which of these is TRUE about NULL in MySQL?**
- [ ] `WHERE salary = NULL` returns rows where salary is null
- [x] `NULL = NULL` evaluates to NULL (not TRUE), so use `IS NULL` instead
- [ ] `COUNT(*)` skips rows where any column is NULL
- [ ] NULL and empty string `''` are equivalent in MySQL

**Q6. AUTO_INCREMENT IDs are guaranteed to be:**
- [ ] Sequential with no gaps
- [ ] Unique and sequential with no gaps, even after rollbacks
- [x] Unique, but gaps may exist due to rollbacks and failed inserts
- [ ] Reused after the maximum value is reached

**Q7. Which normal form eliminates transitive dependencies?**
- [ ] 1NF
- [ ] 2NF
- [x] 3NF
- [ ] BCNF

**Q8. You want to store a monetary amount for a payment. Which column type is most appropriate?**
- [ ] `FLOAT`
- [ ] `DOUBLE`
- [x] `DECIMAL(18, 2)`
- [ ] `INT`
