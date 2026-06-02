# The MESI Coherence Protocol

MESI is the dominant cache coherence protocol used in modern x86 and ARM processors. It tracks each cache line with one of four states, enabling efficient sharing while preventing stale reads.

## The Four States

| State | Abbreviation | Meaning |
|---|---|---|
| **Modified** | M | Line is dirty; only this cache holds it; memory is stale |
| **Exclusive** | E | Line is clean; only this cache holds it; memory is up-to-date |
| **Shared** | S | Line is clean; multiple caches may hold it; memory is up-to-date |
| **Invalid** | I | Line is not present (or has been invalidated) |

A line in state **M** must be written back to memory before any other cache can read it. A line in state **E** can be silently promoted to **M** on a local write without bus traffic. A line in state **S** must be invalidated in all caches before a write can proceed.

## State Transition Diagram

The protocol reacts to two types of events:

- **Local events**: a processor read (PrRd) or write (PrWr) from its own core.
- **Bus events**: a bus read (BusRd) or bus read-exclusive (BusRdX) seen from another core.

```
                   PrWr / BusRdX → invalidate
           ┌────────────────────────────────┐
           ▼                                │
  ┌──────────────┐  PrRd (miss)  ┌──────────────┐
  │   INVALID    │─────────────► │   SHARED     │
  └──────────────┘               └──────────────┘
         │                            │  ▲
PrRd     │           BusRdX           │  │ BusRd
(miss,   │        (other writes) ─────┘  │ (other reads)
 only    │                               │
 copy)   ▼                               │
  ┌──────────────┐  PrWr (silent) ┌──────────────┐
  │  EXCLUSIVE   │───────────────►│  MODIFIED    │
  └──────────────┘                └──────────────┘
         ▲                               │
         │         BusRd (flush)         │
         └───────────────────────────────┘
           (write back, move to S or E)
```

## Step-by-Step Worked Example

**Setup:** Core 0 and Core 1, address `A` initially in memory.

### 1. Core 0 reads A

- Cache miss → bus transaction **BusRd**
- No other cache has A → state becomes **Exclusive (E)**
- Core 0 cache: `A → E`

### 2. Core 1 reads A

- Cache miss → **BusRd**
- Core 0 sees the request on the bus; downgrades A from E to **Shared (S)**
- Core 1 receives A → state **Shared (S)**
- Both caches: `A → S`

### 3. Core 0 writes to A

- Core 0 issues **BusRdX** (read-exclusive with intent to modify)
- Core 1's copy is **invalidated** (S → I)
- Core 0 upgrades to **Modified (M)**
- Core 0 cache: `A → M (value = new_val)`; Core 1 cache: `A → I`

### 4. Core 1 reads A again

- Cache miss (A is Invalid) → **BusRd**
- Core 0 detects its M-state line is requested → **cache-to-cache transfer** (flush)
- Core 0 writes back to memory (or transfers directly), moves to **Shared (S)**
- Core 1 receives up-to-date value → **Shared (S)**

## MOESI — An Extension

Many AMD and ARM implementations add an **Owned (O)** state:

- **O**: Dirty line shared by multiple caches; the owner is responsible for future write-backs.
- Avoids writing a modified line back to main memory before sharing it — the dirty line is transferred core-to-core directly.

This reduces main memory traffic in write-heavy workloads.

## Implementation: Snooping Bus

On a small system, all caches connect to a shared bus. Each cache controller **snoops** every bus transaction:

```c
// Pseudocode for a cache controller snoop handler
void on_bus_event(BusTransaction txn) {
    CacheLine *line = lookup(txn.address);
    if (!line) return;  // we don't have this line

    if (txn.type == BUS_RD) {
        if (line->state == MODIFIED) {
            write_back_to_memory(line);
            line->state = SHARED;
        } else if (line->state == EXCLUSIVE) {
            line->state = SHARED;
        }
    } else if (txn.type == BUS_RDX) {
        // Another core wants exclusive ownership
        if (line->state == MODIFIED) {
            write_back_to_memory(line);
        }
        line->state = INVALID;
    }
}
```

## Performance Properties

| Scenario | Bus Transactions | Notes |
|---|---|---|
| Read by only one core | 1 (BusRd, E state) | Next write is silent (E→M) |
| Read by multiple cores | 1 (BusRd, S state) | Clean sharing, write requires BusRdX |
| Write with no sharers | 0 (local if E/M) | Best case — no bus traffic |
| Write with sharers | 1 (BusRdX, invalidations) | Invalidate all S copies |

## Common Pitfall

A line in **S** state cannot be silently promoted to **M** — the upgrade requires a **BusUpgr** or **BusRdX** even though no data needs to be transferred. This is called an **upgrade miss** and costs a bus round-trip even when the line data is already present and valid.

## Interview Answer

> "MESI is a four-state cache coherence protocol. Modified means the line is dirty and only in this cache. Exclusive means clean and only here. Shared means clean and potentially in multiple caches. Invalid means absent. On a write, the writing core broadcasts a BusRdX to invalidate all S-state copies and gains exclusive Modified ownership. This minimizes bus traffic compared to write-update because invalidations are cheap one-time bus messages rather than broadcasting every write value."
