# LRU Page Replacement — Detailed Trace

Simulate the Least Recently Used (LRU) page replacement algorithm and output a full per-access trace.

For each page access, print whether it resulted in a `HIT` or `FAULT`, and the current frame contents (sorted ascending) after the access.

On a FAULT when frames are full, evict the least recently used page and load the new one.
On a HIT, update the recency order (promote the page to most-recently-used) but do not change the frame set.

After all accesses, print the total number of page faults.

## Input Format

```
F
p1 p2 p3 ... pN
```

- Line 1: integer F — number of frames
- Line 2: space-separated page reference string

## Output Format

```
Access <page>: <status>  frames=<sorted_list>
...
Total page faults: <count>
```

- `<status>` is either `HIT   ` or `FAULT ` — left-justified, padded to 6 characters with spaces
- `<sorted_list>` is a Python-style list: `[1, 2, 3]`

## Sample Input

```
3
1 2 3 4 1 2 5 1 2 3 4 5
```

## Sample Output

```
Access 1: FAULT  frames=[1]
Access 2: FAULT  frames=[1, 2]
Access 3: FAULT  frames=[1, 2, 3]
Access 4: FAULT  frames=[2, 3, 4]
Access 1: FAULT  frames=[1, 3, 4]
Access 2: FAULT  frames=[1, 2, 4]
Access 5: FAULT  frames=[1, 2, 5]
Access 1: HIT    frames=[1, 2, 5]
Access 2: HIT    frames=[1, 2, 5]
Access 3: FAULT  frames=[1, 2, 3]
Access 4: FAULT  frames=[2, 3, 4]
Access 5: FAULT  frames=[3, 4, 5]
Total page faults: 10
```

## Constraints

- 1 <= F <= 10
- 1 <= number of references <= 30
- Page numbers are positive integers
