# How Caches and the TLB Interact (VIPT/PIPT)

The TLB and the data cache solve different problems — translation vs. storage — but they must cooperate on every memory access. The way they are combined determines cache lookup speed, aliasing risk, and hardware complexity. Three fundamental designs exist: VIVT, VIPT, and PIPT.

## Addresses: Virtual vs Physical

- **Virtual address (VA):** What the CPU generates. Unique within a process, but two processes can have the same VA pointing to different physical locations.
- **Physical address (PA):** What DRAM actually sees. Globally unique.

The tag stored in each cache line determines how the cache is indexed and compared:

| Design | Index source | Tag source | Common use |
|---|---|---|---|
| VIVT | Virtual | Virtual | Rare (aliasing problems) |
| VIPT | Virtual | Physical | L1 D-cache on ARM, x86 |
| PIPT | Physical | Physical | L2/L3 caches |

## PIPT: Physically Indexed, Physically Tagged

The cache is looked up using the physical address. The TLB must complete first, providing the PA, before the cache can be accessed.

```
Virtual Address
      ↓
    TLB lookup (serial)
      ↓
  Physical Address
      ↓
  Cache lookup (index + tag from PA)
      ↓
    Data (or cache miss → DRAM)
```

**Pro:** No aliasing — one PA always maps to one cache line.  
**Con:** TLB and cache are strictly serial. The TLB latency (even on a hit) adds to the critical path.

PIPT is used for L2 and L3 caches where the extra cycle is tolerable because the cache access itself is already slower.

## VIPT: Virtually Indexed, Physically Tagged

The cache index comes from the virtual address (fast, no TLB needed), but the tag used for comparison comes from the physical address (arrives from the TLB in parallel).

```
Virtual Address
  ├─ lower bits → Cache Index → fetch candidate sets (parallel)
  └─ upper bits → TLB lookup  → Physical Tag (parallel)
                                      ↓
                           Compare tag against candidate sets
                                      ↓
                                  Hit or Miss
```

This allows the TLB lookup and cache set access to proceed **in parallel**, hiding much of the TLB latency. The x86 L1 D-cache and ARM Cortex-A L1 cache are typically VIPT.

### The Aliasing Constraint

VIPT introduces an aliasing risk: two virtual addresses in different processes could have the same index bits but map to different physical addresses. If the cache is larger than a page, different VAs with the same index bits could collide into the same cache set while referencing different PAs.

The safe condition is:

```
Cache set index bits ⊆ page offset bits

i.e., Cache size / Associativity ≤ Page size
```

For a 4 KB page (12-bit offset), a 4-way associative VIPT cache can be at most 4 × 4 KB = 16 KB without aliasing. This is exactly why ARM Cortex-A L1 D-caches are typically 16 KB or 32 KB (the latter requiring 2-way minimum associativity to stay alias-free).

```
Example: 32 KB, 2-way VIPT cache, 4 KB pages

Index bits = log2(32 KB / 2 / 64 B) = log2(256) = 8 bits
Offset bits = log2(64 B) = 6 bits
Index + offset = 14 bits

Page offset = 12 bits → 14 > 12 → ALIAS RISK if single-way
With 2-way: effective index width per way = 13 bits ≤ 12? No…

Correct: 2-way means 32KB/2 = 16KB per way → index selects among
16KB/64B = 256 sets → 8 index bits; index+offset = 8+6 = 14 bits
vs page offset = 12 bits → STILL risky for aliasing.

OS fix: color pages so that aliased VAs map to the same PA
(page coloring) or hardware fix: use the physical address bit
to disambiguate (ARM's "VIPT but alias-free" guarantee).
```

In practice, ARM Cortex-A series guarantees alias-freedom by design (index bits never exceed the page offset width), so no OS intervention is needed.

## VIVT: Virtually Indexed, Virtually Tagged

Both index and tag are virtual. Fastest possible lookup — no TLB needed at all — but:

- **Aliasing:** Two VAs in the same process mapping the same PA produce two independent cache lines that can diverge (homonyms).
- **Homonyms:** The same VA in two processes refers to different PAs; the cache cannot distinguish them without flushing on context switches.

VIVT requires flushing the entire cache on every context switch, making it impractical for general-purpose OSes. It appears only in single-address-space systems or certain embedded contexts.

## Practical Implications

- **x86 L1 D-cache:** 32 KB, 8-way, VIPT, alias-free (index bits fit within 12-bit page offset).
- **ARM Cortex-A72 L1 D-cache:** 32 KB, 2-way, PIPT (ARM moved to PIPT on some cores to simplify correctness).
- **L2/L3 everywhere:** PIPT — correctness over speed, since these are already higher-latency.

**Interview answer:** "VIPT caches use the virtual address to index cache sets (fast, parallel with TLB lookup) but compare tags using the physical address (from the TLB). This avoids aliasing as long as the cache size per way does not exceed the page size. PIPT is fully correct but serial with the TLB; VIVT is fastest but requires cache flushes on context switches."
