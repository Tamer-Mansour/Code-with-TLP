# Quiz: Joins and Subqueries

**Q1. An INNER JOIN between `users` and `orders` on `user_id` returns:**
- [ ] All users, with NULL in order columns if they have no orders
- [x] Only users who have at least one matching order
- [ ] All orders, with NULL in user columns if no matching user exists
- [ ] The Cartesian product of both tables

**Q2. What is the difference between a LEFT JOIN and a RIGHT JOIN?**
- [ ] LEFT JOIN is faster because MySQL scans the left table first
- [x] LEFT JOIN keeps all rows from the left table; RIGHT JOIN keeps all rows from the right table
- [ ] They are identical; the direction is just a naming convention
- [ ] RIGHT JOIN requires an index; LEFT JOIN does not

**Q3. A correlated subquery:**
- [ ] Returns a single value and cannot reference the outer query
- [ ] Is executed once before the outer query
- [x] References a column from the outer query and is re-evaluated for every outer row
- [ ] Is the same as a CTE (Common Table Expression)

**Q4. Which SQL construct lets you name a subquery and reference it multiple times in the same statement?**
- [ ] Derived table
- [ ] Correlated subquery
- [x] CTE (WITH clause)
- [ ] UNION

**Q5. What does `EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id)` evaluate to?**
- [ ] The count of orders for the user
- [x] TRUE if the user has at least one order, FALSE otherwise
- [ ] The first order_id for the user
- [ ] NULL if the user has no orders

**Q6. A CROSS JOIN produces:**
- [ ] Only rows where both tables have matching keys
- [ ] All rows from the left table plus NULLs for unmatched right rows
- [x] The Cartesian product — every left row paired with every right row
- [ ] An error if no ON condition is given
