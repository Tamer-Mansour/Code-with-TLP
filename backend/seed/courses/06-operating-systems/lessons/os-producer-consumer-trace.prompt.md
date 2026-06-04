# Producer-Consumer with Semaphore Trace

Simulate a bounded-buffer producer-consumer system and print a detailed event trace.

Given a buffer capacity C and a sequence of producer/consumer events, simulate the semaphore-based protocol. Print each event's outcome and the resulting buffer state. Blocked events are skipped (not re-queued).

## Input Format

```
C
P <item>
C
P <item>
...
```

- First line: buffer capacity C
- Each subsequent line is either `P <item>` (produce) or `C` (consume)

## Output Format

For each produce event:
- If buffer is not full: `PRODUCE <item>   -> buffer=<list>` (item padded to 10 chars)
- If buffer is full: `PRODUCER BLOCKS (buffer full, dropped: <item>)`

For each consume event:
- If buffer is not empty: `CONSUME <item>   -> buffer=<list>` (consumed item padded to 10 chars)
- If buffer is empty: `CONSUMER BLOCKS (buffer empty)`

Final line: `Final buffer: <list>`

## Sample Input

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

## Sample Output

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

## Constraints

- 1 <= C <= 10
- 1 <= number of events <= 50
- Item names consist of lowercase letters only, max 15 characters
