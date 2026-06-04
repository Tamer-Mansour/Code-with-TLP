# Go-Back-N Sliding Window Simulator

Simulate the **Go-Back-N ARQ** protocol and count the total number of frame transmissions.

## Input Format

```
<W>
<o0> <o1> <o2> ... <oN-1>
```

- Line 1: window size `W` (integer, 1 ≤ W ≤ 10).
- Line 2: space-separated per-frame outcomes (1 = delivered, 0 = lost).

## Protocol Rules

1. The sender fills the window by transmitting up to `W` frames starting from the oldest undelivered frame.
2. Frames are processed left to right within each window batch.
3. Frames before any error in the batch are acknowledged and the delivered pointer advances.
4. On a lost frame: retransmit that frame (it succeeds on the retry), then continue — all frames from the error position onward fill the next window batch.
5. Count every individual frame transmission, including retransmissions.

## Output Format

```
Total transmissions: <T>
```

## Examples

**Input:**
```
3
1 1 0 1 1 1
```
**Output:**
```
Total transmissions: 7
```

**Input:**
```
4
1 1 1 1 1
```
**Output:**
```
Total transmissions: 5
```

**Input:**
```
1
1 0 1 1
```
**Output:**
```
Total transmissions: 5
```
