# First-Fit, Best-Fit, and Worst-Fit Allocation

When a process requests memory and the allocator manages a list of free holes of varying sizes, it must decide **which hole to use**. The choice determines allocation speed, memory utilization, and the degree of external fragmentation over time. Three classical strategies — First-Fit, Best-Fit, and Worst-Fit — make different tradeoffs.

## The Free List Model

Imagine physical memory represented as an ordered list of free blocks:

```
[16 KB at 0x0000] → [8 KB at 0x5000] → [24 KB at 0x9000] → [4 KB at 0xF000]
```

A new allocation request for 10 KB arrives. Which block does the allocator use?

## First-Fit

**Algorithm:** Scan the free list from the beginning and return the **first hole** that is large enough.

```python
def first_fit(free_list, size):
    for block in free_list:
        if block.size >= size:
            return block
    return None  # allocation failure
```

**Trace for 10 KB request:**
- 16 KB at 0x0000 ≥ 10 KB → **allocate here**, split into [10 KB used] + [6 KB free]

### Characteristics

| Property | Value |
|---|---|
| Speed | O(n) worst case, often O(1) in practice |
| Fragmentation | Moderate; leaves small holes at the start of memory |
| Overhead | Low — stop scanning at first match |

First-Fit is the **fastest** general-purpose strategy and performs well in practice. It tends to cluster small leftover holes near the beginning of the address space.

## Best-Fit

**Algorithm:** Scan the entire free list and return the **smallest hole that is still large enough**.

```python
def best_fit(free_list, size):
    best = None
    for block in free_list:
        if block.size >= size:
            if best is None or block.size < best.size:
                best = block
    return best
```

**Trace for 10 KB request:**
- 16 KB ≥ 10 KB — candidate, waste = 6 KB
- 8 KB < 10 KB — skip
- 24 KB ≥ 10 KB — candidate, waste = 14 KB
- 4 KB < 10 KB — skip
- **Winner:** 16 KB block (smallest hole ≥ request), leftover = 6 KB

### Characteristics

| Property | Value |
|---|---|
| Speed | O(n) always (must scan all) |
| Fragmentation | Tends to create many tiny unusable holes |
| Overhead | Higher; can use a sorted tree for O(log n) |

**Paradox:** Best-Fit sounds optimal but often produces the *worst* external fragmentation over time, because the tiny leftover slivers are too small to satisfy future requests and accumulate as waste.

## Worst-Fit

**Algorithm:** Return the **largest available hole**.

```python
def worst_fit(free_list, size):
    worst = None
    for block in free_list:
        if block.size >= size:
            if worst is None or block.size > worst.size:
                worst = block
    return worst
```

**Trace for 10 KB request:**
- **Winner:** 24 KB block, leftover = 14 KB

### Characteristics

| Property | Value |
|---|---|
| Speed | O(n) or O(log n) with max-heap |
| Fragmentation | Moderate; leftover pieces are large enough to be useful |
| Overhead | Moderate |

The rationale: leaving large remainders means future requests can still be satisfied. In practice, Worst-Fit performs the *worst* of the three on most workloads — the "large pieces" it preserves shrink quickly and fragmentation still accumulates.

## Strategy Comparison Table

| Strategy | Scan Entire List? | Leftover Piece | Real-World Performance |
|---|---|---|---|
| First-Fit | No (stop early) | Variable | Best overall |
| Best-Fit | Yes | Smallest possible | Good utilization, many tiny holes |
| Worst-Fit | Yes | Largest possible | Worst in practice |

## Next-Fit Variant

A practical improvement on First-Fit: instead of always restarting from the beginning, **Next-Fit** resumes the scan from where it last stopped. This distributes allocations across the entire address space, reducing the concentration of small holes at the front.

```
After allocating from position X, next search starts at X+1 (wrapped).
```

## Worked Comparison

Free list: `[100 KB][500 KB][200 KB][300 KB][600 KB]`. Request: 212 KB.

| Strategy | Chosen Block | Leftover |
|---|---|---|
| First-Fit | 500 KB | 288 KB |
| Best-Fit | 300 KB | 88 KB |
| Worst-Fit | 600 KB | 388 KB |

Best-Fit left the smallest leftover, but that 88 KB hole may become stranded. Worst-Fit left a 388 KB block — still useful. First-Fit was the quickest to find.

## Common Pitfalls

- Assuming Best-Fit minimizes fragmentation — it minimizes waste *per allocation* but maximizes the number of unusable holes over time.
- Forgetting that all three strategies require splitting the chosen block and reinserting the remainder into the free list.
- Ignoring the cost of sorted structures needed to make Best-Fit and Worst-Fit fast.

**Interview answer:** First-Fit allocates the first hole that fits (fast, good overall). Best-Fit allocates the smallest sufficient hole (minimizes immediate waste but creates many tiny unusable fragments). Worst-Fit allocates the largest hole (large remainders, but performs worst in practice). First-Fit is preferred in most real allocators.
