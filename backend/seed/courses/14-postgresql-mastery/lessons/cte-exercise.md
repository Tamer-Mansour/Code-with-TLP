# Exercise: Simulate a CTE Chain

Practice writing CTE-style data transformations in Python. You will be given a list of orders and must apply a two-step filter (paid status, then current month) and return the customer IDs with their order counts — just as a chained CTE would in Postgres.

This exercise reinforces how Postgres processes `WITH` expressions step by step before the final `SELECT`.
