# Disk Scheduling: The SCAN (Elevator) Algorithm

**SCAN** moves the disk head in one direction, servicing all pending requests it encounters, then reverses direction at the disk boundary. Its movement resembles an elevator — hence the nickname "elevator algorithm."

## How SCAN Works

1. The head starts at a given track and moves in a specified direction (toward higher or lower track numbers).
2. Service each pending request encountered along the way.
3. When the head reaches the disk boundary (track 0 or track MAX), reverse direction and continue servicing requests in the new direction.

This ensures no request is indefinitely delayed — worst case wait is two full sweeps of the disk.

## SCAN vs SSTF vs FCFS

| Algorithm | Strategy | Starvation? | Total movement |
|---|---|---|---|
| FCFS | Service in request order | No | High, unpredictable |
| SSTF | Nearest track first | Yes (far tracks starved) | Low but unfair |
| SCAN | Elevator sweep | No | Moderate and bounded |
| C-SCAN | Circular SCAN (one direction) | No | Consistent wait time |

## Worked Example

Disk tracks: 0–199. Initial head position: **53**, direction: **up** (toward higher tracks).

Pending requests: `98 183 37 122 14 124 65 67`

**Step 1 — split requests by direction:**
- Right of head (>= 53): 65, 67, 98, 122, 124, 183
- Left of head (< 53): 14, 37

**Step 2 — service right side (ascending):**

```
53 → 65 → 67 → 98 → 122 → 124 → 183 → [hit track 199, reverse]
```

**Step 3 — service left side (descending from 183):**

But SCAN does not need to go to the boundary if there are no more requests; it reverses after the last request in the current direction. The exact behavior (go to boundary or just to last request) depends on implementation. Here we go to the boundary.

Actually: standard SCAN goes all the way to the boundary:

```
53 → 65 → 67 → 98 → 122 → 124 → 183 → 199 (boundary, reverse) → 37 → 14
```

Movement calculation:
- 53 → 65: 12; 65 → 67: 2; 67 → 98: 31; 98 → 122: 24; 122 → 124: 2; 124 → 183: 59 (subtotal: 130)
- 183 → 199: 16 tracks (boundary)
- 199 → 37: 162; 37 → 14: 23 (subtotal: 185)
- **Total: 130 + 16 + 185 = 331 tracks**

**Service order:** 65, 67, 98, 122, 124, 183, 37, 14

## LOOK vs SCAN

**LOOK** is a variant that does not travel all the way to the physical disk boundary. Instead, it reverses at the last pending request in the current direction:

```
53 → 65 → 67 → 98 → 122 → 124 → 183 (last up request, reverse) → 37 → 14
```

Movement: (183 − 53) + (183 − 14) = 130 + 169 = 299 tracks — less than SCAN.

Most modern disk schedulers implement LOOK or C-LOOK rather than true SCAN to avoid unnecessary head travel.

## C-SCAN (Circular SCAN)

C-SCAN services requests in only one direction. After reaching the end, it jumps back to the beginning without servicing requests on the return trip. This gives more uniform wait times than SCAN:

```
53 → 65 → 67 → 98 → 122 → 124 → 183 → 199 (jump to 0) → 14 → 37
```

## Implementation Outline

```python
def scan(head, direction, requests, max_track=199):
    requests = sorted(requests)
    left  = [r for r in requests if r < head]   # below head
    right = [r for r in requests if r >= head]  # at or above head

    service_order = []
    movement = 0
    current = head

    if direction == 'up':
        for r in right:
            movement += r - current
            current = r
            service_order.append(r)
        # go to boundary
        movement += max_track - current
        current = max_track
        # reverse: descend
        for r in reversed(left):
            movement += current - r
            current = r
            service_order.append(r)
    else:  # direction == 'down'
        for r in reversed(left):
            movement += current - r
            current = r
            service_order.append(r)
        movement += current - 0   # go to boundary 0
        current = 0
        for r in right:
            movement += r - current
            current = r
            service_order.append(r)

    return service_order, movement
```

## Further Reading

- **OSTEP Chapter 37: Hard Disk Drives** (https://pages.cs.wisc.edu/~remzi/OSTEP/) — physical disk structure, seek time model, and scheduling algorithms explained with full mathematical analysis.
- **MIT 6.1810 Storage Lab** (https://ocw.mit.edu/courses/6-1810-operating-system-engineering-fall-2023/) — file system layers that sit atop the disk scheduler.
