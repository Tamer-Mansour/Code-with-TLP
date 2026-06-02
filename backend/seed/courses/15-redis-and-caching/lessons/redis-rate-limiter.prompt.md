# Fixed-Window Rate Limiter

## Problem

You are implementing a fixed-window rate limiter. Time is divided into windows of `W` seconds. Each user is allowed at most `L` requests per window. A request is **ALLOWED** if the user's request count in the current window is ≤ L after incrementing; otherwise it is **DENIED**.

## Input format

```
W L
N
t1 user1
t2 user2
...
```

- Line 1: integers `W` (window size in seconds, 1 ≤ W ≤ 3600) and `L` (limit per window, 1 ≤ L ≤ 1000).
- Line 2: integer `N` — number of requests (1 ≤ N ≤ 200).
- Next N lines: integer timestamp `t` (seconds, monotonically non-decreasing) and string `user` (no spaces).

## Output format

Print `N` lines, each either `ALLOW` or `DENY` corresponding to each request in order.

## Example

Input:
```
10 2
5
0 alice
5 alice
10 alice
15 bob
15 alice
```

Output:
```
ALLOW
ALLOW
ALLOW
ALLOW
DENY
```

Explanation:
- Window size = 10 s, limit = 2 per window.
- t=0, alice: window 0, count=1 → ALLOW.
- t=5, alice: window 0, count=2 → ALLOW.
- t=10, alice: window 1 (10//10=1), count=1 → ALLOW.
- t=15, bob: window 1, bob count=1 → ALLOW.
- t=15, alice: window 1, alice count=2 → but limit is 2, so count=2 ≤ 2... wait.

Wait, re-read: limit is 2, so count must be ≤ L. At t=15, alice is in window 1. alice already made 1 request in window 1 (at t=10). Now count becomes 2 ≤ 2 → ALLOW.

(Use the example in test_cases for the definitive expected output.)
