# Closure Counter Factory

Simulate JavaScript's closure-based counter pattern by processing a sequence of counter operations.

## What is a Closure Counter?

A closure counter is a classic JavaScript pattern that demonstrates lexical scoping. The counter's state lives in a closure — invisible from outside, but persistent across calls:

```javascript
function makeCounter(start = 0) {
  let count = start;
  const initialValue = start;
  return {
    inc:   () => ++count,
    dec:   () => --count,
    get:   () => count,
    reset: () => { count = initialValue; },
  };
}

const a = makeCounter(0);
a.inc(); // 1
a.inc(); // 2
a.get(); // 2
a.dec(); // 1
a.get(); // 1

const b = makeCounter(10);
b.get(); // 10  -- independent from 'a'
```

Each call to `makeCounter` creates an **independent** closure. Counters do not share state.

## Task

Process a sequence of commands that create counters and operate on them. For each `GET` command, print the current counter value.

**Commands:**
- `CREATE name start` — create counter `name` initialized to integer `start`
- `INC name` — increment counter by 1
- `DEC name` — decrement counter by 1
- `GET name` — print the current value
- `RESET name` — restore counter to its original `start` value

## Example

**Input:**
```
8
CREATE a 0
INC a
INC a
GET a
DEC a
GET a
CREATE b 10
GET b
```

**Output:**
```
2
1
10
```

## Constraints

- 1 ≤ N ≤ 200 commands
- Counter names are single lowercase letters or short strings
- Counter values are integers (may go negative)
- All `INC`, `DEC`, `GET`, `RESET` operations reference previously created counters

## Further Reading

- [You Don't Know JS Yet — Scope & Closures](https://github.com/getify/You-Dont-Know-JS) — The definitive deep-dive into how closures work under the hood in V8.
- [Eloquent JavaScript Chapter 3](https://eloquentjavascript.net/03_functions.html) — Functions, covering closure semantics with clear examples.
