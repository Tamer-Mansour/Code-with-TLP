# Exercise Prompt: Simulate Round-Robin Bus Arbitration

## Problem Statement

Simulate a shared bus with round-robin arbitration among N masters.

The bus serves one transaction at a time. An arbiter maintains a `next` pointer (initially 0). Whenever the bus is free, it:

1. Collects all requests whose `arrive_time <= bus_free_time`.
2. Scans masters starting from `next`, cycling through 0..N-1, and grants the **first** master with a pending request.
3. If no master has an arrived request, advances `bus_free_time` to the earliest pending arrive_time and repeats.
4. After granting master `m`: grant_time = current bus_free_time, complete_time = grant_time + latency[m] * CLK_NS, bus_free_time = complete_time, next = (m + 1) % N.

Output one line per grant, in grant order.

## Input Format

```
N CLK_NS
lat_0 lat_1 ... lat_{N-1}
R
master_id_0 arrive_time_0
master_id_1 arrive_time_1
...
```

- `N` — number of masters (1 ≤ N ≤ 8)
- `CLK_NS` — clock period in nanoseconds (integer ≥ 1)
- `lat_i` — latency of master i in clock cycles (integer ≥ 1)
- `R` — number of requests (1 ≤ R ≤ 30)
- Each request line: `master_id arrive_time` (both integers ≥ 0)
- Requests are given in arrive_time order (ascending); ties broken by master_id ascending.

## Output Format

One line per granted request, in the order granted:

```
M grant_ns complete_ns
```

All times are integers (nanoseconds).

## Sample Input

```
3 10
2 3 1
4
0 0
1 0
2 0
1 50
```

## Sample Output

```
0 0 20
1 20 50
2 50 60
1 60 90
```

## Explanation

- bus_free=0, next=0. Arrived at t≤0: masters 0, 1, 2. Scan from 0: grant master 0. complete=0+2×10=20. next=1.
- bus_free=20, next=1. Arrived at t≤20: masters 1, 2. Scan from 1: grant master 1. complete=20+3×10=50. next=2.
- bus_free=50, next=2. Arrived at t≤50: master 2. Scan from 2: grant master 2. complete=50+1×10=60. next=0.
- bus_free=60, next=0. Arrived at t≤60: master 1 (arrive 50). Scan from 0: master 0 no request, master 1 yes → grant master 1. complete=60+3×10=90. next=2. Done.

## Constraints

- All arrive_times are non-negative integers (nanoseconds).
- latency[m] × CLK_NS gives integer nanoseconds.
- A master can appear multiple times in the request list; requests are processed in input order.
- 1 ≤ N ≤ 8, 1 ≤ R ≤ 30, 1 ≤ lat_i ≤ 20, 1 ≤ CLK_NS ≤ 100.

## Notes

- Use a queue (deque or list) per master to hold pending requests.
- Process requests one at a time by simulating the bus timeline.
- When scanning round-robin from `next`, try indices: next, (next+1)%N, ..., (next+N-1)%N.
