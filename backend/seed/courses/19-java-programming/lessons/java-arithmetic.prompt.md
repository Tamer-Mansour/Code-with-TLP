# Variable Types and Arithmetic

Read two integers from standard input, one per line.

Print their **sum**, **difference**, **product**, and **integer quotient** (truncated toward zero, matching Java's `int` division behaviour), each on its own line in the format `Label: value`.

## Input format

```
A
B
```

Both `A` and `B` are integers in the range `-10^6` to `10^6`. `B` is never `0`.

## Output format

```
Sum: <A+B>
Difference: <A-B>
Product: <A*B>
Quotient: <A/B>
```

The quotient is the result of integer division (truncate toward zero).

## Example

**Input**
```
17
5
```

**Output**
```
Sum: 22
Difference: 12
Product: 85
Quotient: 3
```

## Constraints

- `-1 000 000 <= A, B <= 1 000 000`
- `B != 0`
