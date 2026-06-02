# Prompt: Simulate Reference Counting and Cycle Leaks

## Problem Description

Implement a simplified reference-counting memory manager that simulates how `shared_ptr` and `weak_ptr` track object lifetimes.

## Commands

Each line of stdin contains one command:

| Command | Effect |
|---|---|
| `ALLOC <id>` | Create object `id`. Strong count = 1, weak count = 0. |
| `SHARE <id>` | Increment strong count of `id`. |
| `WEAK <id>` | Increment weak count of `id`. |
| `RELEASE <id>` | Decrement strong count. If strong count reaches 0: print destruction message, then decrement weak by 1 (implicit hold). If weak also reaches 0: print freed message. |
| `DROP_WEAK <id>` | Decrement weak count. If both strong=0 and weak=0 after: print freed message. |
| `STATUS <id>` | Print current counts or freed status. |

## Output Format (exact strings, one per command)

- `ALLOC x` → `allocated x`
- `SHARE x` → `shared x (strong=N)` where N is the new strong count
- `WEAK x` → `weak ref x (weak=N)` where N is the new weak count
- `RELEASE x` when new strong count > 0 → `released x (strong=N)`
- `RELEASE x` when new strong count == 0 → print `destroyed x`, then:
  - if new weak count (after decrementing implicit hold) == 0 → also print `freed x`
- `DROP_WEAK x` when weak count drops to 0 AND strong count is already 0 → `freed x`
- `DROP_WEAK x` otherwise → `dropped weak x (weak=N)` where N is the new weak count
- `STATUS x` when control block exists → `x: strong=N weak=N`
- `STATUS x` when control block freed → `x: freed`

## Constraints

- Object ids are alphanumeric strings with underscores, length 1–20.
- At most 100 commands per test case.
- `RELEASE` is only called when strong count >= 1.
- `DROP_WEAK` is only called when weak count >= 1.
- `SHARE`, `WEAK`, `STATUS`, `RELEASE`, `DROP_WEAK` are only called on ids that have been `ALLOC`ed.
- Strong and weak counts fit in a 32-bit integer.

## Sample Input 1

```
ALLOC node_a
ALLOC node_b
SHARE node_a
SHARE node_b
RELEASE node_a
RELEASE node_b
STATUS node_a
STATUS node_b
```

## Sample Output 1

```
allocated node_a
allocated node_b
shared node_a (strong=2)
shared node_b (strong=2)
released node_a (strong=1)
released node_b (strong=1)
node_a: strong=1 weak=0
node_b: strong=1 weak=0
```

## Sample Input 2

```
ALLOC obj
WEAK obj
RELEASE obj
STATUS obj
DROP_WEAK obj
STATUS obj
```

## Sample Output 2

```
allocated obj
weak ref obj (weak=1)
destroyed obj
obj: strong=0 weak=1
dropped weak obj (weak=0)
freed obj
```

Note: After `RELEASE` reduces strong to 0, the implicit hold decrements weak by 1 as well. Wait — in this case, weak=1 from the explicit `WEAK` command. The implicit hold means weak count starts conceptually at 1 (the implicit hold) when strong > 0. For simplicity in this simulation, the implicit hold is modeled as follows: when strong count drops to 0, decrement weak by 1. If the result is 0 and no explicit weak refs remain, print `freed`. Otherwise just print `destroyed`. Since `WEAK obj` added 1, after the implicit release weak becomes 1 (from 2: 1 explicit + 1 implicit). So `STATUS obj` shows `strong=0 weak=1`. Then `DROP_WEAK obj` drops it to 0, printing `freed obj`.

**Revised model for implementation clarity:**

Maintain two counters per object: `strong` and `weak`. The implicit hold is represented by initializing `weak = 1` at `ALLOC` time (not 0). This way:
- `ALLOC x` → strong=1, weak=1 (the 1 in weak is the implicit hold)
- `WEAK x` → weak++
- `RELEASE x` → strong--; if strong==0: print destroyed, then weak--; if weak==0: print freed
- `DROP_WEAK x` → weak--; if strong==0 and weak==0: print freed; else print dropped
- `STATUS x` → if control block exists print strong and (weak-1 if strong>0 else weak) ... 

Actually to keep it simple and match expected output, use this exact model:

- `ALLOC x` → strong=1, explicit_weak=0; print allocated x
- `SHARE x` → strong++; print shared x (strong=N)
- `WEAK x` → explicit_weak++; print weak ref x (weak=N) where N=explicit_weak
- `RELEASE x` → strong--; if strong==0: print destroyed x; if explicit_weak==0: print freed x and remove; else object is "zombie" (destroyed but control block alive)
- `DROP_WEAK x` → explicit_weak--; if zombie and explicit_weak==0: print freed x and remove; else print dropped weak x (weak=N)
- `STATUS x` → if removed: print x: freed; else print x: strong=N weak=M where N=strong, M=explicit_weak

## Sample Input 3 (correct cleanup, no cycle)

```
ALLOC x
SHARE x
RELEASE x
STATUS x
RELEASE x
STATUS x
```

## Sample Output 3

```
allocated x
shared x (strong=2)
released x (strong=1)
x: strong=1 weak=0
destroyed x
freed x
x: freed
```
