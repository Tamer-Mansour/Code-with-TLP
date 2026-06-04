# Variable Scope Simulator

## Problem

You are given a series of JavaScript variable declaration scenarios. For each scenario, determine the output that JavaScript would produce.

Each test case specifies:
- A declaration keyword (`var` or `let`)
- A variable name (for context only)
- An integer value N
- A context (`loop` or `function`)

**Output rules:**

- `loop` + `var`: Because `var` is function-scoped, all N simulated loop callbacks close over the same variable and see its final value N. Output: `loop: ` followed by N copies of N, space-separated.
- `loop` + `let`: Because `let` creates a new binding per iteration, each callback sees 0, 1, 2, ..., N-1. Output: `loop: ` followed by `0 1 2 ... N-1`.
- `function` (either keyword): A simple function-scoped access. Output: `function: N`.

## Input Format

```
T
keyword varname value context
```

- Line 1: T (number of test cases, 1 ≤ T ≤ 100)
- Next T lines: four space-separated tokens

## Output Format

One line per test case, exactly as described above.

## Examples

**Input:**
```
3
var counter 3 loop
let counter 3 loop
var x 42 function
```

**Output:**
```
loop: 3 3 3
loop: 0 1 2
function: 42
```

**Input:**
```
2
let i 5 loop
var n 1 loop
```

**Output:**
```
loop: 0 1 2 3 4
loop: 1
```

## Constraints

- 1 ≤ T ≤ 100
- 1 ≤ value ≤ 20
- keyword is exactly `var` or `let`
- context is exactly `loop` or `function`
