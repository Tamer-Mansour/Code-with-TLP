# Min-Heap Operations (Manual Implementation)

Simulate a min-heap using a flat Python list — **do not import or use the `heapq` module**. Implement insert and extract-min from scratch.

## Input Format

Read lines from standard input until EOF. Each line is one of:

- `INSERT x` — insert integer `x` (may be negative)
- `EXTRACT_MIN` — remove and print the minimum element

## Output Format

For each `EXTRACT_MIN` operation, print the minimum value on its own line.  
If `EXTRACT_MIN` is called on an empty heap, print `EMPTY`.

`INSERT` operations produce no output.

## Constraints

- At most 10000 operations total
- Values: −10⁹ ≤ x ≤ 10⁹
- You must implement the heap manually; do not use `heapq`

## Example

**Input:**
```
INSERT 5
INSERT 3
INSERT 8
EXTRACT_MIN
INSERT 1
EXTRACT_MIN
EXTRACT_MIN
```

**Output:**
```
3
1
5
```

## Hint

After each INSERT, sift the new element up until it is not smaller than its parent. After each EXTRACT_MIN, move the last element to the root and sift it down until it is not larger than both its children.
