# Prompt: Simulate Timer Ticks and Interrupt Firing

## Problem Description

Implement a simplified virtual timer simulator. The timer has a counter that starts at 0 and increments by 1 every tick. When the counter reaches the PERIOD value, an interrupt fires. In periodic mode the counter resets to 0 and continues; in one-shot mode the timer stops after the first interrupt.

## Input Format

Exactly 3 lines, in this order:

```
PERIOD <n>
MODE <periodic|oneshot>
TICKS <t>
```

- `PERIOD n` — the counter value at which an interrupt fires (integer, 1 ≤ n ≤ 1000)
- `MODE periodic` or `MODE oneshot`
- `TICKS t` — total number of ticks to simulate (integer, 1 ≤ t ≤ 10000)

## Output Format

For each interrupt event, print one line:
```
IRQ at tick <tick_number> counter=<value>
```

where `<tick_number>` is the current tick (1-based) and `<value>` is the counter value at the time of firing (always equal to PERIOD).

After simulation completes, print:
```
Total IRQs: <count>
```

## Constraints

- Counter starts at 0 before tick 1.
- Each tick: increment counter by 1, then check if `counter == PERIOD`.
- In periodic mode: after firing, reset counter to 0 and continue ticking.
- In one-shot mode: after the first firing, stop ticking (no more IRQs for remaining ticks).
- No libraries beyond the Python standard library.
- Time limit: 3000 ms. Memory limit: 256 MB.

## Sample Test Cases

### Sample 1

Input:
```
PERIOD 3
MODE periodic
TICKS 10
```

Expected output:
```
IRQ at tick 3 counter=3
IRQ at tick 6 counter=3
IRQ at tick 9 counter=3
Total IRQs: 3
```

### Sample 2

Input:
```
PERIOD 5
MODE oneshot
TICKS 12
```

Expected output:
```
IRQ at tick 5 counter=5
Total IRQs: 1
```

### Sample 3

Input:
```
PERIOD 1
MODE periodic
TICKS 4
```

Expected output:
```
IRQ at tick 1 counter=1
IRQ at tick 2 counter=1
IRQ at tick 3 counter=1
IRQ at tick 4 counter=1
Total IRQs: 4
```
