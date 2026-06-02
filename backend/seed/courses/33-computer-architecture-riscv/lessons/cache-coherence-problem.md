# The Cache Coherence Problem

Private caches are essential for performance — without them, every memory access would cross the shared bus and create a bottleneck. But private caches create a dangerous inconsistency: two processors can hold different values for the same memory address. This is the **cache coherence problem**.

## A Concrete Example

Suppose two cores, Core 0 and Core 1, both cache memory address `0x1000`, which initially holds `0`.

```
Initial state: Mem[0x1000] = 0
Core 0 cache: [0x1000] = 0   (clean)
Core 1 cache: [0x1000] = 0   (clean)
```

**Step 1:** Core 0 writes `42` to `0x1000`. Its cache line is updated, but Core 1's cache still holds `0`.

```
After Core 0 writes:
Core 0 cache: [0x1000] = 42  (dirty)
Core 1 cache: [0x1000] = 0   (STALE — incoherent!)
Main memory:  [0x1000] = 0   (not yet written back)
```

**Step 2:** Core 1 reads `0x1000` and gets `0` — the wrong answer.

This violates the programmer's expectation that shared variables have a single logical value.

## Formal Definition of Coherence

A memory system is **coherent** if:

1. **Write propagation**: A write by any processor is eventually visible to all other processors.
2. **Write serialization**: All writes to the same location are seen in the same order by all processors.
3. **Read-my-writes**: A processor always reads the most recent value it wrote.

Note that coherence is per-address (single variable at a time). **Consistency** (covered in a later lesson) deals with the ordering of accesses to *different* addresses.

## Why Private Caches Make This Hard

The whole point of a cache is to avoid going to main memory on every access. But that means:

- **Write-back caches** delay propagating writes; a core may hold a dirty line invisible to others.
- **Write-through caches** always update main memory, but cores still hold stale read copies.
- Cache lines are typically 64 bytes — reading one address pulls in adjacent bytes, which can be independently cached by another core.

## The Two Classic Solutions

### 1. Write-Invalidate

When a processor writes, it sends an **invalidation** message to all other caches holding that line. They mark their copy invalid. The next access from another core causes a miss and fetches the up-to-date value.

```
Core 0 writes 0x1000:
  → Broadcast: "Invalidate 0x1000"
  → Core 1's cache entry for 0x1000 → INVALID
  → Core 1's next read → cache miss → fetches 42 from Core 0 or memory
```

Used by: MESI protocol (most modern CPUs).

### 2. Write-Update (Write-Broadcast)

When a processor writes, it broadcasts the **new value** to all caches. Every copy is updated in place.

- Advantage: No miss on the next read — data is immediately available.
- Disadvantage: Every single write floods the bus, even if other cores don't need the value. Wastes bandwidth.

Used by: Dragon protocol (largely historical).

## Coherence Granularity

Coherence operates at **cache-line granularity** (typically 64 bytes), not byte granularity. This is both efficient (fewer tracking entries needed) and a source of the **false sharing** problem — two processors writing different variables that happen to share a cache line cause unnecessary invalidations.

## The Coherence Directory

In large systems, broadcasting invalidations to every core doesn't scale. A **directory** tracks which caches hold each line, and invalidations are sent only to those caches. This is the foundation of directory-based coherence protocols (covered in a later lesson).

## Code Example — Observing Incoherence Without Synchronization

```c
// Shared variable (no synchronization)
int x = 0;

// Thread 0 (Core 0)
void thread0() {
    x = 42;        // Writes to Core 0's cache
    // No fence — no guarantee Core 1 sees this
}

// Thread 1 (Core 1)
void thread1() {
    int val = x;   // May read stale 0 from Core 1's cache
    printf("%d\n", val);  // Could print 0 or 42 — undefined behavior
}
```

With proper cache coherence hardware and a memory fence, `val` is guaranteed to be `42` after `thread0` completes. Without the fence, the ordering is unspecified even with coherence hardware.

## Interview Answer

> "Cache coherence is the property that all processors observe a consistent value for any given memory address. It breaks down because each core has a private cache that can hold an outdated copy after another core writes. Hardware solves this with either write-invalidate (the writer broadcasts an invalidation, forcing other caches to reload on next access) or write-update (the writer broadcasts the new value). Modern CPUs use write-invalidate protocols like MESI because write-update wastes bus bandwidth."
