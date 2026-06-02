# String Pool Move/Copy Simulator

You are simulating a string pool that tracks move vs copy operations.

**Input format:**
- Line 1: integer N (number of strings)
- Lines 2..N+1: each line is either `MOVE:<word>` or `COPY:<word>` where `<word>` contains no spaces

**Output format (single line):**
```
moves=<M> copies=<C> pool=<w1> <w2> ... <wN>
```

Where M is the count of MOVE operations, C is the count of COPY operations, and the pool words appear in input order.

**Example:**
```
Input:
3
MOVE:alpha
COPY:beta
MOVE:gamma

Output:
moves=2 copies=1 pool=alpha beta gamma
```
