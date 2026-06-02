# Spectre and Branch-Prediction Side Channels

In January 2018, researchers disclosed **Spectre** and **Meltdown** — two classes of vulnerabilities that showed speculative execution, the cornerstone of modern CPU performance, could be weaponized to leak secret data across security boundaries. Spectre, in particular, is rooted in branch prediction.

## The Core Insight

Speculative execution is designed to leave no *architectural* trace when the speculation is wrong — the ROB is flushed, registers are restored, and memory writes are discarded. But speculation *does* leave **microarchitectural** traces: the cache, the TLB, and execution-unit timing are all changed by speculative instructions, even after the ROB is rolled back.

An attacker can observe these microarchitectural side effects through a **cache timing side channel** — a carefully measured time difference that reveals whether a particular cache line was loaded.

## Spectre Variant 1: Bounds-Check Bypass

The classic attack exploits a conditional branch used for array bounds checking:

```c
// Victim code (e.g., kernel or sandbox runtime)
if (index < array1_size) {              // Branch B
    uint8_t x = array1[index];          // Load 1 (speculative if B predicted taken)
    sink = array2[x * 512];             // Load 2 (speculative — trains cache)
}
```

**Attack steps:**

1. **Train the predictor:** Call the victim function many times with valid indices so the branch predictor learns that Branch B is *almost always taken*.
2. **Trigger speculation:** Call the victim with an out-of-bounds `index` pointing to a secret byte (e.g., a kernel password) outside `array1`. The predictor predicts Branch B taken and speculatively executes both loads.
3. **Wait for rollback:** The CPU detects the bounds check failed, squashes the loads, and restores architectural state. The secret is never architecturally visible.
4. **Measure the cache:** `array2[secret * 512]` was loaded speculatively into the cache. Time accesses to each `array2[k * 512]` (k = 0…255). The one that is fast was cached — revealing `secret`.

```
Attack timeline:
  Train: index=1,2,3,...  → predictor says "taken" always
  Attack: index = &secret → predictor: TAKEN (wrong!)
  Speculation: x = *(secret address); array2[x*512] fetched into cache
  Rollback: architectural state clean
  Measure: cache hit at array2[42*512]  →  secret == 42
```

## Why the Cache Is the Oracle

The **FLUSH+RELOAD** technique times memory accesses at nanosecond precision:

```python
# Conceptual pseudo-code
flush(array2)                 # evict all of array2 from cache
trigger_speculation(index)    # cause the victim to speculate
for k in range(256):
    t0 = rdtsc()
    _ = array2[k * 512]
    t1 = rdtsc()
    if (t1 - t0) < CACHE_HIT_THRESHOLD:
        print(f"Secret byte = {k}")
```

A cache hit takes ~4 ns; a cache miss ~100 ns. The difference is easily distinguishable.

## Spectre Variant 2: Branch Target Injection

A second variant trains the **indirect branch predictor** (BTB) to point a victim's indirect jump to attacker-chosen code, causing the victim to speculatively execute a "gadget" that leaks data through the cache.

This is particularly dangerous because:
- The training can happen from a *different process* (cross-process attack).
- The BTB is shared across processes on the same physical core.

## Mitigations and Their Costs

| Mitigation | What it does | Performance cost |
|------------|-------------|-----------------|
| **Retpoline** | Replace indirect branches with a return-based trampoline that misdirects speculation into an infinite loop | 2–15% on indirect-branch-heavy code |
| **IBRS / STIBP** | Microcode: Isolate branch predictors across privilege levels | 10–30% (early microcode), <5% with enhanced IBRS |
| **Array index masking** | Always mask index before use, even if bound check passes | Compiler/developer burden |
| **Site isolation** | Run each website origin in a separate process (Chrome) | Memory overhead; reduced SharedArrayBuffer resolution |
| **Serializing instructions** | `LFENCE` prevents later instructions from executing until all prior loads complete | 5–30% where inserted |

## Lessons for Architects

- **Microarchitectural state is architectural state** from a security perspective. Anything the CPU touches speculatively is a potential channel.
- **Sharing is dangerous.** BTBs, caches, and TLBs shared across security domains enable cross-domain attacks. Future designs may need per-domain prediction structures.
- **Performance vs. security is a first-class design tension.** Every cycle of speculation is an opportunity for a side channel.

## Key Terms

| Term | Meaning |
|------|---------|
| **Spectre** | Family of attacks exploiting speculative execution and branch prediction |
| **Meltdown** | Exploits out-of-order execution past a privilege fault (not branch-based) |
| **FLUSH+RELOAD** | Cache timing technique to observe what a victim loaded |
| **Retpoline** | Return trampoline software mitigation for indirect branch injection |
| **IBRS** | Indirect Branch Restricted Speculation — CPU microcode mitigation |

> **Interview answer:** Spectre exploits the fact that mis-speculated instructions change cache state even after rollback. An attacker trains the branch predictor to cause the victim to speculate over a secret-data access, then uses cache timing (FLUSH+RELOAD) to read the resulting microarchitectural side effect — leaking the secret without ever touching it architecturally.
