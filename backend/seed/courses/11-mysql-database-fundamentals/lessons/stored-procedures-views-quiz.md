# Quiz: Stored Procedures and Views

**Q1. What is the correct syntax to create a stored procedure in MySQL?**
- [ ] `DEFINE PROCEDURE get_user(IN uid INT) SELECT * FROM users WHERE id = uid;`
- [x] `CREATE PROCEDURE get_user(IN uid INT) BEGIN SELECT * FROM users WHERE id = uid; END`
- [ ] `PROCEDURE get_user AS SELECT * FROM users WHERE id = @uid;`
- [ ] `CREATE FUNCTION get_user(uid INT) RETURNS TABLE AS SELECT * FROM users;`

**Q2. You call a stored procedure with `CALL get_user(42)`. What parameter mode would `uid` need to be declared as?**
- [x] `IN`
- [ ] `OUT`
- [ ] `INOUT`
- [ ] `RETURN`

**Q3. A view is best described as:**
- [ ] A cached copy of a query result stored on disk
- [x] A named, stored SELECT query that behaves like a virtual table
- [ ] A trigger that runs before each SELECT
- [ ] An indexed copy of one or more tables

**Q4. Which of these views is NOT updatable?**
- [ ] `CREATE VIEW active_users AS SELECT * FROM users WHERE is_active = 1`
- [x] `CREATE VIEW user_order_count AS SELECT user_id, COUNT(*) FROM orders GROUP BY user_id`
- [ ] `CREATE VIEW recent_orders AS SELECT id, amount FROM orders WHERE created_at > NOW()`
- [ ] `CREATE VIEW vip_users AS SELECT id, email FROM users WHERE tier = 'vip'`

**Q5. What does a BEFORE INSERT trigger allow you to do?**
- [ ] Prevent all INSERT operations on the table
- [ ] Run a stored procedure after each INSERT
- [x] Modify or validate the NEW row values before they are written to the table
- [ ] Automatically create a backup of the row being inserted

**Q6. You want a trigger that fires after a row is deleted from `orders`. Which is correct?**
- [ ] `CREATE TRIGGER t BEFORE DELETE ON orders FOR EACH ROW BEGIN ... END`
- [x] `CREATE TRIGGER t AFTER DELETE ON orders FOR EACH ROW BEGIN ... END`
- [ ] `CREATE TRIGGER t ON DELETE orders FOR EACH ROW BEGIN ... END`
- [ ] `CREATE TRIGGER t AFTER REMOVE ON orders FOR EACH ROW BEGIN ... END`

**Q7. Stored procedures differ from functions in MySQL in that:**
- [ ] Procedures can accept parameters; functions cannot
- [x] Procedures are called with CALL and can have OUT parameters; functions return a value and are used in expressions
- [ ] Functions support transactions; procedures do not
- [ ] Procedures are faster than functions

**Q8. Which statement drops the view named `active_users`?**
- [ ] `REMOVE VIEW active_users;`
- [ ] `DELETE VIEW active_users;`
- [x] `DROP VIEW active_users;`
- [ ] `ALTER VIEW active_users DROP;`
