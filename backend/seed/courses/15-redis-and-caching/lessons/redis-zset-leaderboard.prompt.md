# Sorted-Set Leaderboard

Implement a minimal Redis sorted-set, supporting three commands:

- `ZADD <member> <score>` — set the score of `member` to the integer `score`.
- `ZINCRBY <member> <delta>` — add integer `delta` to the score of `member`. If member doesn't exist, it starts at 0 then increments.
- `ZTOP <K>` — print the top-K members by score descending. Ties broken by member name ascending.

## Input

```
N
<command 1>
<command 2>
... N commands total
```

`N` is the number of commands (1 ≤ N ≤ 10000). Each command is on its own line.

## Output

After **each** `ZTOP K`, print K lines (or fewer if fewer members exist), each formatted as `<member> <score>`, in score-descending / name-ascending order.

`ZADD` and `ZINCRBY` produce no output.

## Example

Input:

```
4
ZADD alice 10
ZADD bob 20
ZADD carol 15
ZTOP 3
```

Output:

```
bob 20
carol 15
alice 10
```

## Ties

Input:

```
4
ZADD x 1
ZADD y 1
ZADD z 1
ZTOP 2
```

Output:

```
x 1
y 1
```
