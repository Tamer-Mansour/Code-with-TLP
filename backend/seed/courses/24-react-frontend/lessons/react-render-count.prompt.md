# Render Count Simulation

Simulate React's "skip render if state is the same" rule.

## Input

A series of `SET <key> <value>` commands, one per line. Each is one attempt to set `key` to `value` in a key/value store.

## Output

A single integer: the number of commands that **actually changed** the store. A command counts as a real change if:

- The key didn't exist before, OR
- The key existed but the previous value was different.

## Examples

Input:

```
SET a 1
SET b 2
SET c 3
```

Output: `3` (all three were new)

Input:

```
SET a 1
SET a 1
SET a 1
```

Output: `1` (only the first one changed state)

Input:

```
SET a 1
SET a 2
SET b 1
SET b 1
```

Output: `3`

Input: (empty) → Output: `0`

## Notes

- `key` and `value` are simple tokens without spaces.
- Case-sensitive comparison.
- Ignore blank lines.
