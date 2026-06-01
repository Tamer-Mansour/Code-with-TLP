# Inner Join Two CSVs

Simulate `SELECT * FROM left INNER JOIN right ON left.user_id = right.user_id;` on tiny CSV-style tables piped through stdin.

## Input

```
<n_left>            integer row count of the left table
<left header>       comma-separated column names; must contain "user_id"
<left row 1..n_left> comma-separated values
<n_right>           integer row count of the right table
<right header>      comma-separated column names; must contain "user_id"
<right row 1..n_right>
```

## Output

- Print one header line: the left header concatenated with the right header, but **`user_id` appears only once** (skip it from the right header).
- Then, for each left row in input order, for each matching right row in input order, print the joined row.
- A joined row is the left row's values followed by the right row's values **excluding `user_id`**.
- If there are no matches, print only the header line.

## Example

Input:

```
2
user_id,name
1,Alice
2,Bob
2
user_id,amount
1,100
2,50
```

Output:

```
user_id,name,amount
1,Alice,100
2,Bob,50
```

## Constraints

- 0 ≤ rows ≤ 1000 per side.
- `user_id` is a non-empty string without commas.
