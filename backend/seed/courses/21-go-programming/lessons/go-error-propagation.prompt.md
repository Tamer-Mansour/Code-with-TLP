# Error Propagation Chain

## Problem

Go 1.13+ introduced error wrapping with `fmt.Errorf("%w", err)` and `errors.Is`/`errors.As` for unwrapping error chains.

`errors.Is` traverses an entire error chain looking for a target error. It is equivalent to asking: "does this error, or any error it wraps, match the target?"

This exercise simulates that chain traversal using string identities.

You are given an error chain as a string, with components separated by ` -> ` (a space, arrow, space). The first component is the outermost error; the last is the innermost (root cause).

For each query string, determine whether it appears **anywhere** in the chain (simulating `errors.Is` string-identity semantics). Print `YES` if found, `NO` otherwise.

## Input Format

```
<error chain string>
Q
query1
query2
...
```

- Line 1: the error chain (e.g. `network error -> connection refused -> timeout`)
- Line 2: `Q`, number of queries (1 <= Q <= 50)
- Next Q lines: one query string each

## Output Format

Q lines, each `YES` or `NO`.

## Example

**Input:**
```
network error -> connection refused -> timeout
4
timeout
network error
disk full
connection refused
```

**Output:**
```
YES
YES
NO
YES
```

## Constraints

- Chain has 1 to 10 components
- Each component is a non-empty string (no leading/trailing spaces after splitting on ` -> `)
- Matching is exact (case-sensitive)
- 1 <= Q <= 50
