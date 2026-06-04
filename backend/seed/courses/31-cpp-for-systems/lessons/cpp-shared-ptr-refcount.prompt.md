# Reference Counting Simulation

## Problem Description

Simulate the behavior of `std::shared_ptr` reference counting. You manage a set of named handles that point to named objects. Each object has a reference count tracking how many handles currently point to it.

## Commands

Each line of stdin contains one command:

| Command | Effect |
|---|---|
| `CREATE id` | Create a new shared object with reference count 1. Handle name `id` points to object `id`. |
| `COPY src dst` | Create handle `dst` pointing to the same object as `src`. Increment that object's reference count by 1. |
| `DROP id` | Release handle `id`. Decrement the object's reference count by 1. If the count reaches 0, print `DESTROYED obj_id` and remove the object. |
| `QUERY id` | Print the current reference count of the object that handle `id` points to. |

## Output Format

- `DROP id` when ref count reaches 0: print `DESTROYED obj_id` (where `obj_id` is the original object name, i.e., the id used in `CREATE`).
- `QUERY id`: print the integer reference count on its own line.
- All other commands produce no output.

## Constraints

- Handle and object ids are uppercase letters and digits, length 1–10.
- At most 200 commands per test case.
- `COPY`, `DROP`, and `QUERY` are only called on handles that currently exist.
- `CREATE` is only called with ids that are not already in use as a handle.

## Sample Input 1

```
CREATE A
COPY A B
COPY A C
QUERY B
DROP A
QUERY C
DROP B
DROP C
```

## Sample Output 1

```
3
2
DESTROYED A
```

**Explanation:** After `CREATE A`, object A has count 1. After `COPY A B` and `COPY A C`, count is 3. `QUERY B` returns 3. `DROP A` reduces count to 2 — not zero, no message. `QUERY C` returns 2. `DROP B` reduces count to 1. `DROP C` reduces count to 0, so `DESTROYED A` is printed.

## Sample Input 2

```
CREATE X
QUERY X
DROP X
```

## Sample Output 2

```
1
DESTROYED X
```

## Sample Input 3

```
CREATE obj1
CREATE obj2
COPY obj1 ref1
COPY obj2 ref2
COPY obj1 ref3
QUERY ref1
QUERY ref3
DROP obj1
QUERY ref1
DROP ref1
DROP ref3
DROP obj2
DROP ref2
```

## Sample Output 3

```
3
3
2
1
DESTROYED obj1
DESTROYED obj2
```
