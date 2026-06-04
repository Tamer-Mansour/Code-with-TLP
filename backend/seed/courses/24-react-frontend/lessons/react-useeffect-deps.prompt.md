# useEffect Dependency Tracker

The `useEffect` hook re-runs whenever a value in its dependency array changes between renders. Simulate a sequence of component renders and determine when the effect fires.

## Input

- **Line 1:** A comma-separated list of tracked variable names (the dependency array).
- **Subsequent lines:** One render per line, given as comma-separated values in the same order as the variable names.

## Output

For each render line (in order):

- First render: always print `EFFECT RUNS` (the component just mounted).
- Subsequent renders: print `EFFECT RUNS` if any tracked value changed from the previous render, or `NO EFFECT` if all values are identical.

## Examples

**Example 1**

Input:
```
count,name
0,Alice
0,Alice
1,Alice
1,Bob
1,Bob
```

Output:
```
EFFECT RUNS
NO EFFECT
EFFECT RUNS
EFFECT RUNS
NO EFFECT
```

**Example 2**

Input:
```
x
5
5
10
10
10
```

Output:
```
EFFECT RUNS
NO EFFECT
EFFECT RUNS
NO EFFECT
NO EFFECT
```

**Example 3**

Input:
```
a,b
1,2
1,3
1,3
```

Output:
```
EFFECT RUNS
EFFECT RUNS
NO EFFECT
```

## Notes

- Values are compared as strings (exact character-by-character match, like `Object.is` on primitives).
- The first line of input is the header row (variable names) — it is not a render.
- There is always at least one render line.
