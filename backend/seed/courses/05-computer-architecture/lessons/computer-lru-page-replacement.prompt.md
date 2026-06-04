# LRU Page Replacement Simulator

Simulate the **Least Recently Used (LRU)** page replacement algorithm for a virtual memory system. Given a number of physical page frames and a reference string, compute the total number of page faults.

## Algorithm

Maintain a set of at most `F` page frames. On each page access:
- If the page is already in a frame: **HIT** — move it to "most recently used" position.
- If the page is not in a frame: **FAULT**
  - If frames are not full: load the page.
  - If frames are full: **evict the least recently used page**, then load the new page.

## Input Format

```
Line 1: F — number of physical frames (1 <= F <= 10)
Line 2: space-separated list of page numbers (the reference string, 1–50 accesses, page numbers 0–99)
```

## Output Format

For each page reference (in order), print `FAULT` or `HIT` on its own line.  
On the final line, print: `Total page faults: X`

## Examples

**Example 1 — Working set fits in frames**
```
Input:
3
1 2 3 1 2 3

Output:
FAULT
FAULT
FAULT
HIT
HIT
HIT
Total page faults: 3
```

**Example 2 — Working set exceeds frames (thrashing)**
```
Input:
2
1 2 3 1 2 3

Output:
FAULT
FAULT
FAULT
FAULT
FAULT
FAULT
Total page faults: 6
```
Explanation: With 2 frames and 3 distinct pages cycling, every access is a fault.

**Example 3 — Single frame**
```
Input:
1
1 2 3 1

Output:
FAULT
FAULT
FAULT
FAULT
Total page faults: 4
```

## Hints

- Python's `collections.OrderedDict` works perfectly as an ordered LRU cache.
- Insert new entries at the end (most recently used).
- On a hit, use `move_to_end(key)` to refresh the entry.
- On a fault with a full cache, use `popitem(last=False)` to evict the LRU entry (the first/leftmost).
