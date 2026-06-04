# Exercise: Loosely-Timed vs Approximately-Timed Latency Calculator

## Problem Statement

In TLM-2.0 virtual prototyping, two timing models are defined:

**Loosely-Timed (LT)**: the initiator uses temporal decoupling. It accumulates a local time offset and only synchronizes with the global simulation clock when the offset exceeds the quantum. This minimizes context switches and maximizes simulation speed.

**Approximately-Timed (AT)**: each transaction phase (`BEGIN_REQ`, `END_REQ`, `BEGIN_RESP`, `END_RESP`) is timed individually to model pipelined bus behavior.

You are given T transactions, a bus latency per transaction (in ns), and a quantum size (in ns).

**For LT**: compute the total simulated time as `ceil(T * bus_latency / quantum) * quantum` (the time at which the last quantum sync occurs, rounding up to the nearest quantum boundary).

**For AT**: total simulated time = `T * bus_latency` (every transaction is individually timed, no batching).

Print:
- `LT_TOTAL_NS=<value>`
- `AT_TOTAL_NS=<value>`
- `SPEEDUP=<ratio>` where ratio = `AT_TOTAL_NS / LT_TOTAL_NS` rounded to 2 decimal places

## Input Format

- Line 1: `T` (number of transactions, 1 <= T <= 10000)
- Line 2: `bus_latency` (integer ns per transaction, 1 <= bus_latency <= 1000)
- Line 3: `quantum` (integer ns, 1 <= quantum <= 1000000)
- Line 4: `phases` (integer, number of AT phases — provided for context, not used in final time calculation)

## Output Format

Three lines exactly as shown above.

## Constraints

- 1 <= T <= 10000
- 1 <= bus_latency <= 1000
- 1 <= quantum <= 1000000

## Sample Input

```
100
10
50
4
```

## Sample Output

```
LT_TOTAL_NS=1000
AT_TOTAL_NS=1000
SPEEDUP=1.00
```

## Additional Example

Input:
```
200
5
100
4
```

Output:
```
LT_TOTAL_NS=1000
AT_TOTAL_NS=1000
SPEEDUP=1.00
```

## Another Example

Input:
```
150
10
1000
4
```

Output:
```
LT_TOTAL_NS=2000
AT_TOTAL_NS=1500
SPEEDUP=0.75
```
