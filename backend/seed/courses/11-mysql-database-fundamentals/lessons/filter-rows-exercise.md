# Filter Rows from a CSV

In this exercise you'll write the Python equivalent of:

```sql
SELECT * FROM people WHERE age > :threshold;
```

Why Python? The course grader runs stdin→stdout programs in pure Python, so we'll *simulate* SQL semantics in code. Going through this loop helps cement what `WHERE` actually does row-by-row.

The input is a CSV. The first line is the header, the second line is the threshold, then the data rows. Print the header and every row where `age` is **strictly greater** than the threshold.

See the prompt file for the exact I/O contract.
