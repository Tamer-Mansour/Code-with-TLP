# Problem: Pack and Unpack Status Flags Into a Byte

## Description

You are given a sequence of operations to apply to an 8-bit status register that starts at 0. The register uses its lower 4 bits as named flags:

- Bit 0: `READY`
- Bit 1: `BLOCKED`
- Bit 2: `ERROR`
- Bit 3: `DONE`
- Bits 4–7 are always 0.

After applying all operations, output:
1. The final register value as a decimal integer.
2. The state of each flag (`1` or `0`), one per line, in the order: READY, BLOCKED, ERROR, DONE.

## Operations

Each operation is one line in the form `<OP> <FLAG>`:

| OP | Action |
|---|---|
| `SET` | Set the named flag to 1 |
| `CLEAR` | Clear the named flag to 0 |
| `TOGGLE` | Flip the named flag |

## Input Format

Line 1: integer N — number of operations.
Lines 2 to N+1: each is `<OP> <FLAG>` where OP is `SET`, `CLEAR`, or `TOGGLE` and FLAG is `READY`, `BLOCKED`, `ERROR`, or `DONE`.

## Output Format

```
<register decimal value>
READY=<0 or 1>
BLOCKED=<0 or 1>
ERROR=<0 or 1>
DONE=<0 or 1>
```

## Constraints

- 1 <= N <= 100
- Operations are always valid (known OP and FLAG names)
- No blank lines in input

## Sample Input 1

```
4
SET READY
SET ERROR
SET DONE
CLEAR ERROR
```

## Sample Output 1

```
9
READY=1
BLOCKED=0
ERROR=0
DONE=1
```

**Explanation:**
- Start: `00000000` = 0
- SET READY: `00000001` = 1
- SET ERROR: `00000101` = 5
- SET DONE: `00001101` = 13
- CLEAR ERROR: `00001001` = 9
- READY=bit0=1, BLOCKED=bit1=0, ERROR=bit2=0, DONE=bit3=1

## Sample Input 2

```
3
SET BLOCKED
TOGGLE BLOCKED
SET DONE
```

## Sample Output 2

```
8
READY=0
BLOCKED=0
ERROR=0
DONE=1
```

**Explanation:**
- SET BLOCKED: `00000010` = 2
- TOGGLE BLOCKED: `00000000` = 0 (was 1, now 0)
- SET DONE: `00001000` = 8
