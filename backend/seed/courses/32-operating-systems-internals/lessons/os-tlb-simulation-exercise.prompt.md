# Prompt: Simulate a TLB With LRU Replacement

## Problem Statement

Simulate a fully-associative TLB with **LRU (Least Recently Used)** replacement. Given a TLB capacity and a sequence of virtual page number (VPN) accesses, determine how many accesses are hits and how many are misses.

**Rules:**
- The TLB starts empty.
- On a **hit**: the VPN is already in the TLB. Mark it as most recently used. Count a hit.
- On a **miss**: the VPN is not in the TLB. Count a miss.
  - If the TLB has an empty slot, install the VPN there.
  - If the TLB is full, evict the **least recently used** VPN, then install the new one.

Output the total hits, total misses, and hit percentage rounded to exactly two decimal places.

## Input Format

```
capacity
N
vpn_1 vpn_2 ... vpn_N
```

- Line 1: integer `capacity` (1 ≤ capacity ≤ 64), the number of TLB entries.
- Line 2: integer `N` (1 ≤ N ≤ 1000), the number of memory accesses.
- Line 3: `N` space-separated integers, each a virtual page number (0 ≤ VPN ≤ 10000).

## Output Format

```
Hits: <hits>
Misses: <misses>
Hit ratio: <percentage>%
```

Where `<percentage>` is formatted to exactly two decimal places.

## Constraints

- 1 ≤ capacity ≤ 64
- 1 ≤ N ≤ 1000
- 0 ≤ VPN ≤ 10000

## Sample Input

```
3
9
1 2 3 1 2 4 1 2 3
```

## Sample Output

```
Hits: 4
Misses: 5
Hit ratio: 44.44%
```

## Explanation

Step-by-step for capacity=3, accesses=[1,2,3,1,2,4,1,2,3]:

| Step | VPN | TLB state (MRU→LRU) | Result |
|------|-----|----------------------|--------|
| 1    | 1   | [1]                  | MISS   |
| 2    | 2   | [2,1]                | MISS   |
| 3    | 3   | [3,2,1]              | MISS   |
| 4    | 1   | [1,3,2]              | HIT    |
| 5    | 2   | [2,1,3]              | HIT    |
| 6    | 4   | [4,2,1] (evict 3)    | MISS   |
| 7    | 1   | [1,4,2]              | HIT    |
| 8    | 2   | [2,1,4]              | HIT    |
| 9    | 3   | [3,2,1] (evict 4)    | MISS   |

Hits=4, Misses=5, Hit ratio=4/9=44.44%
