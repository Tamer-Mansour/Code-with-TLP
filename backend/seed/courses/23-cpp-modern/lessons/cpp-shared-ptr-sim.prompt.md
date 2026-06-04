# Smart Pointer Reference Count Simulator

Simulate the reference counting behavior of `std::shared_ptr`.

## Operations

- `MAKE name` — create a new `shared_ptr` named `name` owning a new object
  - Print: `Object-N created [rc=1]` (N is 1-indexed creation order)
- `COPY dst src` — create `dst` as a shared copy of `src` (increments ref count)
  - Print: `rc[Object-N]=K` (new ref count)
- `RESET name` — reset `name` (decrements ref count)
  - If count reaches 0: print `Object-N destroyed`
  - Otherwise: print `rc[Object-N]=K`
- `MOVE dst src` — move ownership from `src` to `dst` (count unchanged, `src` becomes empty)
  - Print: `rc[Object-N]=K`

## Input Format

- Line 1: integer `N`
- Lines 2..N+1: one operation per line

## Output Format

One line per event in operation order.

## Example

**Input:**
```
7
MAKE p1
MAKE p2
COPY p3 p1
RESET p1
COPY p4 p3
RESET p3
RESET p4
```

**Output:**
```
Object-1 created [rc=1]
Object-2 created [rc=1]
rc[Object-1]=2
rc[Object-1]=1
rc[Object-1]=2
rc[Object-1]=1
Object-1 destroyed
```

## Constraints

- `1 <= N <= 100`
- Pointer names are alphanumeric strings
- `COPY` and `RESET` will always reference a valid (non-empty) pointer
- `MOVE` source will always be a non-empty pointer
- Object IDs are assigned in the order `MAKE` operations appear (1-indexed)
