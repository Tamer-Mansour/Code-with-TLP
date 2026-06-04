# Exercise: Enforce a CHECK Constraint

SQL Server CHECK constraints enforce data validity rules at the database level — the engine rejects any INSERT or UPDATE that violates the constraint, regardless of which application made the request.

## The SQL Equivalent

```sql
ALTER TABLE dbo.employees
ADD CONSTRAINT ck_emp_age    CHECK (age BETWEEN 18 AND 65),
    CONSTRAINT ck_emp_status CHECK (status IN ('active', 'inactive'));
```

With these constraints in place, any INSERT like:

```sql
INSERT INTO dbo.employees (name, age, status)
VALUES ('Bob', 17, 'active');   -- REJECTED: age 17 < 18
```

...will fail with:

```
Msg 547, Level 16, State 0
The INSERT statement conflicted with the CHECK constraint "ck_emp_age".
```

## Why Check Constraints Matter

Applications come and go. The database outlives them all. By enforcing rules in the schema, you guarantee that:

- A direct SQL insert from SSMS cannot violate the rule
- A bug in one application cannot corrupt data that other applications depend on
- Data integrity is a property of the **data**, not an assumption in the **code**

## Multiple Constraints on One Column

A column can have more than one constraint:

```sql
CONSTRAINT ck_salary_range  CHECK (salary BETWEEN 15000 AND 500000),
CONSTRAINT ck_salary_int    CHECK (salary = FLOOR(salary))   -- must be whole number
```

Both must be satisfied for the row to be accepted.

## CHECK Constraint Limitations

- CHECK constraints are not evaluated during `TRUNCATE TABLE` (no rows are individually tested).
- A CHECK constraint can reference any column **in the same row** but cannot reference other tables or call user-defined functions in most cases.
- NULLs pass CHECK constraints — `age BETWEEN 18 AND 65` does **not** block NULL ages. Add `NOT NULL` separately.

## In This Exercise

You will receive rows with a name, age, and status. Apply the two-condition check (age 18–65 inclusive, status must be 'active' or 'inactive') and print `OK` or `REJECTED` for each row.

> **Further reading:** *Database Design — 2nd Edition* by Adrienne Watt covers constraints and integrity rules in Chapter 8 — free at https://opentextbc.ca/dbdesign01/
