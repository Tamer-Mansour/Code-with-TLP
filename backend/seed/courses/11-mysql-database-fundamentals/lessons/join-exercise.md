# Inner Join Two Tables

Time to simulate a SQL inner join in Python. The judge will pipe stdin to your program.

## Input format

```
<n_left>
<left header>
<left row 1>
...
<left row n_left>
<n_right>
<right header>
<right row 1>
...
<right row n_right>
```

Both tables include a column called `user_id`. Inner-join them on `user_id`.

## Output format

Print the joined header (left header + right header, with `user_id` appearing only once), then every matching joined row. Preserve the **left table's iteration order**, and for each matched left row print right matches in input order.

See the prompt file for the exact contract and worked example.
