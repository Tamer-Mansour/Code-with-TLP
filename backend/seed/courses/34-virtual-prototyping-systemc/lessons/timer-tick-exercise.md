# Simulate Timer Ticks and Interrupt Firing

In this exercise you will implement a simplified virtual timer simulator in Python. The simulator reads a timer configuration from stdin, advances simulation time tick by tick, and prints each event (tick, interrupt fired, counter reload) to stdout.

## What You Will Implement

Your program will:
1. Read timer configuration (tick period, period register, mode, total simulation time).
2. Simulate the timer counter advancing each tick.
3. Print a log line whenever the counter overflows and an interrupt fires.
4. Stop when the total simulation time is exhausted.

## Input Format

```
PERIOD <n>        # counter reloads at this value (1-based, fires when counter == PERIOD)
MODE <periodic|oneshot>
TICKS <t>         # total number of ticks to simulate
```

## Output Format

For each interrupt event print:
```
IRQ at tick <tick_number> counter=<value>
```

After simulation ends, print:
```
Total IRQs: <count>
```

## Example

Input:
```
PERIOD 3
MODE periodic
TICKS 10
```

Output:
```
IRQ at tick 3 counter=3
IRQ at tick 6 counter=3
IRQ at tick 9 counter=3
Total IRQs: 3
```

## Constraints

- `PERIOD` is between 1 and 1000.
- `TICKS` is between 1 and 10000.
- Counter starts at 0 and increments by 1 each tick.
- In periodic mode the counter resets to 0 after firing; in one-shot mode it stops.
- An interrupt fires exactly when `counter == PERIOD`.
- No external libraries required.
