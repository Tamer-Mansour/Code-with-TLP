# Closure Counter Factory

## Problem

Simulate a JavaScript closure-based counter factory. Process N commands that create and manipulate named counters. For each `GET` command, print the counter's current value.

**Commands:**

| Command | Effect |
|---------|--------|
| `CREATE name start` | Create counter `name` with initial value `start` |
| `INC name` | Increment counter `name` by 1 |
| `DEC name` | Decrement counter `name` by 1 |
| `GET name` | Print the current value of counter `name` |
| `RESET name` | Restore counter `name` to its original `start` value |

Counters are independent — operations on one do not affect others.

## Input Format

```
N
COMMAND args...
...
```

- Line 1: N (number of commands, 1 ≤ N ≤ 200)
- Next N lines: one command per line

## Output Format

Print a line for each `GET` command only.

## Examples

**Input:**
```
8
CREATE a 0
INC a
INC a
GET a
DEC a
GET a
CREATE b 10
GET b
```

**Output:**
```
2
1
10
```

**Input:**
```
6
CREATE x 5
DEC x
DEC x
GET x
RESET x
GET x
```

**Output:**
```
3
5
```

**Input:**
```
5
CREATE c 100
INC c
INC c
INC c
GET c
```

**Output:**
```
103
```

## Constraints

- 1 ≤ N ≤ 200
- Counter names are alphanumeric strings
- Initial start values are integers in range [-1000, 1000]
- All INC/DEC/GET/RESET commands reference a counter that has already been created
