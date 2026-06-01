# Sum and Average

## Input

```
N
<int 1> <int 2> ... <int N>
```

- N ≥ 0
- Integers fit in a 32-bit signed range.

## Output

A single line: `<sum> <average>` separated by one space.

- If the average is exact (whole number), print as integer (`5`, not `5.00`).
- Otherwise print with two decimals (`2.33`).
- If N is 0 (empty input), print `0 0`.

## Examples

Input:

```
4
2 4 6 8
```

Output:

```
20 5
```

Input:

```
3
1 2 4
```

Output:

```
7 2.33
```

Input:

```
0
```

Output:

```
0 0
```
