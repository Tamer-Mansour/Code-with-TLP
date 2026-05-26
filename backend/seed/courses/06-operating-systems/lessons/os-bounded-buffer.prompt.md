# Bounded Buffer Simulation

Simulate a **bounded buffer** with sequential produce and consume operations. Print all items successfully consumed, in the order they were consumed.

## Input

```
CAP K
op_1
op_2
...
op_K
```

- First line: CAP (buffer capacity, 1 ≤ CAP ≤ 20) and K (number of operations, 1 ≤ K ≤ 100).
- Next K lines: each line is either:
  - `P n` — produce item n (integer, 1 ≤ n ≤ 1000)
  - `C` — consume one item

## Output

Print all items consumed, space-separated, in the order they were consumed. If no items were consumed, print `EMPTY`.

## Rules

- The buffer is initially empty.
- `P n`: if the buffer has fewer than CAP items, append n to the back. Otherwise, **skip** (item is dropped, nothing is printed, no error).
- `C`: if the buffer is non-empty, remove and record the front item. Otherwise, **skip**.

## Examples

**Example 1**
```
Input:
3 6
P 1
P 2
P 3
C
C
C

Output:
1 2 3
```

**Example 2**
```
Input:
2 7
P 1
P 2
P 3
C
C
P 4
C

Output:
1 2 4
```
*Explanation:* P3 is skipped (buffer full with 1,2). After consuming 1 and 2, buffer is empty. P4 adds 4. C consumes 4.

**Example 3**
```
Input:
1 3
C
P 5
C

Output:
5
```
*Explanation:* First C skipped (empty). P5 succeeds. Second C consumes 5.

**Example 4**
```
Input:
2 3
C
C
C

Output:
EMPTY
```

## Constraints

- Output items separated by single spaces.
- Output `EMPTY` if nothing was consumed.
- Do not print anything for skipped operations.
