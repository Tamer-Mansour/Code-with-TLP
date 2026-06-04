# TCP Congestion Window Simulator (Slow Start + Congestion Avoidance)

Simulate **TCP Reno** congestion control round by round.

## Input Format

```
<ssthresh> <max_rounds>
<event_1>
<event_2>
...
```

- Line 1: initial `ssthresh` and `max_rounds` (number of rounds to simulate).
- Next `max_rounds` lines: each is either `OK` (no loss) or `LOSS` (timeout occurred).

## Rules

- `cwnd` starts at **1 MSS**.
- **Slow Start** phase: `cwnd < ssthresh` — on `OK`, `cwnd *= 2`.
- **Congestion Avoidance** phase: `cwnd >= ssthresh` — on `OK`, `cwnd += 1`.
- On `LOSS`: `ssthresh = max(cwnd // 2, 1)`, then `cwnd = 1` (returns to Slow Start).
- The phase and values printed for each round reflect the state **before** applying that round's event.

## Output Format

For each round, print:

```
Round R: cwnd=C ssthresh=T phase=PHASE
```

Where `PHASE` is `SlowStart` when `cwnd < ssthresh`, or `CongAvoid` when `cwnd >= ssthresh`.

## Examples

**Input:**
```
16 8
OK
OK
OK
OK
LOSS
OK
OK
OK
```
**Output:**
```
Round 1: cwnd=1 ssthresh=16 phase=SlowStart
Round 2: cwnd=2 ssthresh=16 phase=SlowStart
Round 3: cwnd=4 ssthresh=16 phase=SlowStart
Round 4: cwnd=8 ssthresh=16 phase=SlowStart
Round 5: cwnd=16 ssthresh=16 phase=CongAvoid
Round 6: cwnd=1 ssthresh=8 phase=SlowStart
Round 7: cwnd=2 ssthresh=8 phase=SlowStart
Round 8: cwnd=4 ssthresh=8 phase=SlowStart
```

**Input:**
```
8 6
OK
OK
OK
OK
OK
OK
```
**Output:**
```
Round 1: cwnd=1 ssthresh=8 phase=SlowStart
Round 2: cwnd=2 ssthresh=8 phase=SlowStart
Round 3: cwnd=4 ssthresh=8 phase=SlowStart
Round 4: cwnd=8 ssthresh=8 phase=CongAvoid
Round 5: cwnd=9 ssthresh=8 phase=CongAvoid
Round 6: cwnd=10 ssthresh=8 phase=CongAvoid
```
