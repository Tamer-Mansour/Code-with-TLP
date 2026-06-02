# Compute Sync Points from a Time Quantum

## Problem Description

You are simulating the synchronization logic of a TLM quantum keeper. An initiator thread accumulates transaction delays in a local time variable. When the local time reaches or exceeds the **quantum** `Q`, a synchronization occurs: the global time advances by the full local time, and the local time resets to zero.

Given a quantum `Q` and a sequence of transaction delays, determine every global time at which a synchronization occurs, including a final synchronization if there is any remaining local time after all transactions are processed.

## Input Format

```
Q N
d1 d2 d3 ... dN
```

- Line 1: two integers `Q` (the time quantum in nanoseconds) and `N` (number of transactions).
- Line 2: `N` space-separated integers, each representing the annotated delay (in nanoseconds) of one transaction. Transactions are processed in the given order.

## Output Format

Print one integer per line for each synchronization point (the global time at which the sync occurs), in chronological order. After all sync points, print:

```
Total syncs: K
```

where `K` is the total number of synchronizations (including the final one if applicable).

## Constraints

- `1 <= Q <= 1_000_000`
- `1 <= N <= 1_000`
- `1 <= di <= 1_000_000` for each delay `di`
- Each sync triggers when `local_time >= Q` after adding a delay, or at the end if any local time remains.

## Sample Input

```
1000 7
300 300 300 300 200 600 400
```

## Sample Output

```
1200
2400
Total syncs: 2
```

## Explanation

- After tx1: local=300 (no sync)
- After tx2: local=600 (no sync)
- After tx3: local=900 (no sync)
- After tx4: local=1200 >= 1000 → sync; global=1200, local=0
- After tx5: local=200 (no sync)
- After tx6: local=800 (no sync)
- After tx7: local=1200 >= 1000 → sync; global=2400, local=0
- End: local=0, no final sync needed

## Additional Example

Input:
```
1000 4
100 200 150 300
```

Output:
```
750
Total syncs: 1
```

Explanation: local accumulates to 750 after all 4 transactions (no mid-run sync); at the end, local=750 > 0 so a final sync occurs: global=750.
