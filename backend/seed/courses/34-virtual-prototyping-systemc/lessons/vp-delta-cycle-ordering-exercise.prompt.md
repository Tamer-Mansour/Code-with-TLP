# Exercise: Resolve Delta-Cycle Update Ordering

## Problem Statement

Simulate the SystemC evaluate-update (delta-cycle) loop for a network of combinational logic gates. Given initial signal values and gate definitions, find the final stable values of all signals and how many delta cycles were needed to reach quiescence.

## Input Format

```
S G
sig1 val1
sig2 val2
...
sigS valS
type out in1 [in2]
...
(G gate lines total)
```

- First line: integers S (1 ≤ S ≤ 20) and G (1 ≤ G ≤ 20).
- Next S lines: signal name (alphanumeric, no spaces) and initial value (0 or 1).
- Next G lines: gate definition using one of:
  - `NOT out in1` — out = 1 - in1
  - `AND out in1 in2` — out = in1 AND in2
  - `OR  out in1 in2` — out = in1 OR in2
- All signal names referenced by gates appear in the signal list.
- No combinational loops (convergence guaranteed within 50 deltas).
- If multiple gates write the same output, the last gate (in input order) wins.

## Output Format

```
Deltas: D
sig1=val1
sig2=val2
...
```

- First line: total delta cycles executed (rounds that produced at least one signal change).
- Then one line per signal in **alphabetical order** by name, format `name=value`.

## Algorithm

Each round (delta cycle):

1. **Evaluate**: compute new value for every gate output using current signal values.
2. **Update**: apply all computed values. If any signal's value changed, increment delta count.
3. Repeat until no signal changes.

## Constraints

- 1 ≤ S ≤ 20, 1 ≤ G ≤ 20
- Signal values are 0 or 1.
- No combinational loops; guaranteed convergence.

## Sample Input 1

```
4 2
a 1
b 0
c 0
y 0
NOT c a
AND y c b
```

Delta 1 evaluate: NOT c a → c=NOT(1)=0 (was 0, no change); AND y c b → y=AND(0,0)=0 (was 0, no change). No changes → 0 deltas.

## Sample Output 1

```
Deltas: 0
a=1
b=0
c=0
y=0
```

## Sample Input 2

```
4 2
a 0
b 1
c 1
y 0
NOT c a
AND y c b
```

Delta 1: c=NOT(0)=1 (no change); y=AND(1,1)=1 (was 0, CHANGE). Update: y=1. Delta 2: no changes. Total: 1.

## Sample Output 2

```
Deltas: 1
a=0
b=1
c=1
y=1
```

## Sample Input 3

```
4 2
a 0
b 0
c 0
d 1
NOT b a
AND c b d
```

Delta 1: b=NOT(0)=1 (CHANGE); c=AND(0,1)=0 (no change, uses old b=0). Update: b=1. Delta 2: b=NOT(0)=1 (no change); c=AND(1,1)=1 (CHANGE). Update: c=1. Delta 3: no changes. Total: 2.

## Sample Output 3

```
Deltas: 2
a=0
b=1
c=1
d=1
```
