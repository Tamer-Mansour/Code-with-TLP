# Practice: Producer-Consumer with Semaphore Trace

This exercise simulates the classic bounded-buffer producer-consumer synchronization problem and asks you to print a detailed event-by-event trace showing buffer state transitions and blocking conditions.

## Background

The **producer-consumer problem** is one of the three classic synchronization problems (along with Readers-Writers and Dining Philosophers). A bounded buffer of capacity C holds items:

- **Producers** add items. If the buffer is full, the producer *blocks* (cannot proceed).
- **Consumers** remove items. If the buffer is empty, the consumer *blocks*.

A semaphore-based solution uses three synchronization objects:

```
empty = Semaphore(C)   # counts free slots (starts at C)
full  = Semaphore(0)   # counts filled slots (starts at 0)
mutex = Mutex()        # mutual exclusion for buffer access
```

In this simulation, blocked events are **skipped** (not re-queued): a blocked producer drops its item, a blocked consumer produces no output item.

## Input Format

```
C
event_1
event_2
...
```

- `C`: buffer capacity
- Each event is either `P <item>` (produce item) or `C` (consume)

## Output Format

For each event, print one line. Then print the final buffer state.

```
PRODUCE <item>   -> buffer=<list>
PRODUCE <item>   -> buffer=<list>
PRODUCER BLOCKS (buffer full, dropped: <item>)
CONSUME <item>   -> buffer=<list>
CONSUMER BLOCKS (buffer empty)
Final buffer: <list>
```

The item name in `PRODUCE` and `CONSUME` lines is padded to 10 characters (left-justified with spaces).

## Example

**Input:**
```
3
P apple
P banana
P cherry
P date
C
C
P elderberry
C
C
C
```

**Output:**
```
PRODUCE apple      -> buffer=['apple']
PRODUCE banana     -> buffer=['apple', 'banana']
PRODUCE cherry     -> buffer=['apple', 'banana', 'cherry']
PRODUCER BLOCKS (buffer full, dropped: date)
CONSUME apple      -> buffer=['banana', 'cherry']
CONSUME banana     -> buffer=['cherry']
PRODUCE elderberry -> buffer=['cherry', 'elderberry']
CONSUME cherry     -> buffer=['elderberry']
CONSUME elderberry -> buffer=[]
CONSUMER BLOCKS (buffer empty)
Final buffer: []
```

## Further Reading

- OSTEP Chapter 30 — Condition Variables: https://pages.cs.wisc.edu/~remzi/OSTEP/
- OSTEP Chapter 31 — Semaphores: https://pages.cs.wisc.edu/~remzi/OSTEP/
- xv6 Book (MIT) — Locking chapter: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/3def8fcd397933ebb846fb479bdcf556_MIT6_828F12_xv6-book-rev7.pdf
