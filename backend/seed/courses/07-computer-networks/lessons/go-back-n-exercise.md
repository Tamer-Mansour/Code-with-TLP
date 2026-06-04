# Exercise: Go-Back-N Sliding Window Simulator

The **Go-Back-N ARQ** protocol allows the sender to keep up to W frames outstanding (unacknowledged). When a frame is lost, the sender must retransmit that frame **and all subsequent frames** in the window — even if they arrived correctly at the receiver.

This exercise asks you to simulate GBN and count the total number of frame transmissions required to deliver all frames in order.

## Rules of this Simulation

- Frames are numbered 0, 1, 2, … (N frames total, where N = number of outcome entries).
- The sender may have at most W unacknowledged frames outstanding.
- Each round, the sender fills the window by transmitting as many frames as allowed.
- If every frame in the current window is delivered (outcome = 1), they are all ACKed and the window advances.
- If any frame in the window is lost (outcome = 0), the frames before it (in the same round) are ACKed, but from the lost frame onward the entire window must be retransmitted.
- Retransmission of a previously-failed frame succeeds on the retry (the failure is one-time per original frame slot).
- Count every individual frame transmission (original + retransmissions).

## Input Format

```
<W>
<o0> <o1> <o2> ... <oN-1>
```

Line 1: window size W (integer).
Line 2: space-separated outcomes for each frame (0 = lost, 1 = delivered).

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
Total transmissions: 9
```

*Explanation:* Window 1 sends frames 0, 1, 2. Frame 0 and 1 delivered, frame 2 lost → 3 transmissions, 2 ACKed. Window 2 retransmits frame 2 and sends 3, 4 (window = 3 starting at frame 2). Frame 2 now succeeds. Frames 2, 3 delivered (4 delivered so far), frame 4 is also in window… trace continues until all 6 frames delivered. Total = 9.

**Input:**
```
4
1 1 1 1 1
```
**Output:**
```
Total transmissions: 5
```

*Explanation:* All frames delivered on first try; 5 transmissions total.
