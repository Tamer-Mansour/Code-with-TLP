# RAII Resource Tracker Simulation

Simulate RAII (Resource Acquisition Is Initialization) behavior for a sequence of resource operations.

## Operations

- `ACQUIRE name` — acquire a resource named `name` in the current scope
- `RELEASE name` — explicitly release resource `name`
  - If already released: print `ERROR: name already released`
  - Otherwise: print `MANUAL-RELEASE: name`
- `SCOPE_END` — end the current scope; automatically release all resources acquired in this scope, in **reverse** order of acquisition. Print `AUTO-RELEASE: name` for each.

## Input Format

- Line 1: integer `N`
- Lines 2..N+1: one operation per line (`SCOPE_END` has no second word)

## Output Format

One line per release event (in the order they occur).

## Example

**Input:**
```
8
ACQUIRE fileA
ACQUIRE dbConn
ACQUIRE mutex
SCOPE_END
ACQUIRE socket
RELEASE socket
RELEASE socket
SCOPE_END
```

**Output:**
```
AUTO-RELEASE: mutex
AUTO-RELEASE: dbConn
AUTO-RELEASE: fileA
MANUAL-RELEASE: socket
ERROR: socket already released
```

## Notes

- A `SCOPE_END` only releases resources acquired **since the last `SCOPE_END`** (or since the start if there was none yet). Resources from outer scopes are not affected.
- After `SCOPE_END`, the scope resets (no resources pending until the next `ACQUIRE`).
- A resource that was manually `RELEASE`d before `SCOPE_END` is not auto-released again (it is already gone).

## Constraints

- `1 <= N <= 200`
- Resource names are alphanumeric strings with no spaces
- There will be at least one `SCOPE_END`
