# Template Type Dispatcher

## Problem Description

Simulate a compile-time type-dispatch system inspired by C++ template specialization and `if constexpr`. Given a sequence of typed values, apply the correct operation for each type.

You are given a series of lines each containing a type tag and a value. Apply the rule for that type and print the result:

| Type tag | Rule | Output format |
|---|---|---|
| `INT` | Print the value multiplied by 2 | `INT: N` |
| `FLOAT` | Print the value rounded to 2 decimal places | `FLOAT: N.NN` |
| `STR` | Print the string reversed | `STR: reversed_string` |
| `BOOL` | Print `true` if value is `1`, `false` otherwise | `BOOL: true` or `BOOL: false` |

## Input Format

- First line: integer N (number of values).
- Next N lines: `TYPE value` where TYPE is one of `INT`, `FLOAT`, `STR`, `BOOL`.

## Output Format

One line per input value in the format shown above.

## Constraints

- 1 ≤ N ≤ 100.
- INT values fit in a 32-bit signed integer.
- FLOAT values have at most 6 decimal places of input precision.
- STR values are non-empty, no spaces, length 1–50.
- BOOL values are `0` or `1`.

## Sample Input 1

```
5
INT 21
FLOAT 3.14159
STR hello
BOOL 1
BOOL 0
```

## Sample Output 1

```
INT: 42
FLOAT: 3.14
STR: olleh
BOOL: true
BOOL: false
```

## Sample Input 2

```
4
INT -5
FLOAT 2.5
STR racecar
INT 0
```

## Sample Output 2

```
INT: -10
FLOAT: 2.50
STR: racecar
INT: 0
```

## Sample Input 3

```
6
STR abcde
INT 1000000
FLOAT 0.1
BOOL 0
STR Z
FLOAT 99.999
```

## Sample Output 3

```
STR: edcba
INT: 2000000
FLOAT: 0.10
BOOL: false
STR: Z
FLOAT: 100.00
```
