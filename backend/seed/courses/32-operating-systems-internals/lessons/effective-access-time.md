# Effective Memory Access Time With a TLB

Knowing the individual costs of a TLB hit and a TLB miss is useful, but what systems designers care about is the **average cost of a memory access** under realistic workloads. That average is called **Effective Memory Access Time (EMAT)**, and it ties together hit ratio, TLB access time, memory access time, and page-table walk cost into a single formula.

## The Formula

```
EMAT = h × (t_tlb + t_mem)
     + (1 - h) × (t_tlb + t_walk + t_mem)
```

Where:

| Symbol | Meaning |
|---|---|
| `h` | TLB hit ratio (fraction of accesses that find a valid entry) |
| `t_tlb` | Time to access the TLB (always paid, hit or miss) |
| `t_mem` | Time for one physical memory access (to fetch the actual data) |
| `t_walk` | Additional memory accesses needed to walk the page table on a miss |

Because the TLB lookup is always performed, it appears in both branches. On a miss you pay `t_walk` extra (typically 1–4 memory accesses for a 1–4-level page table) before you can proceed.

### Simplified Form

When the TLB is checked in parallel with the first level of the page table, or when `t_tlb` is negligible (a common simplifying assumption in textbooks), the formula reduces to:

```
EMAT = h × t_mem + (1 - h) × (k + 1) × t_mem
```

Where `k` = number of page-table levels (extra memory reads for the walk). This form is useful for quick back-of-envelope calculations.

## Worked Example 1: Two-Level Page Table

**Given:**
- TLB hit ratio `h = 0.95`
- Memory access time `t_mem = 100 ns`
- TLB lookup time `t_tlb = 2 ns` (negligible — sometimes ignored)
- Page-table levels `k = 2` → miss costs 2 extra memory reads

**Calculation (including t_tlb):**

```
EMAT = 0.95 × (2 + 100)
     + 0.05 × (2 + 2×100 + 100)
     = 0.95 × 102 + 0.05 × 302
     = 96.9 + 15.1
     = 112 ns
```

Without a TLB (worst case, `h = 0`):

```
No-TLB = (k+1) × t_mem = 3 × 100 = 300 ns
```

The TLB reduces average access time from 300 ns to 112 ns — a **2.7× improvement** at 95% hit ratio.

## Worked Example 2: Four-Level Page Table (x86-64)

**Given:**
- `h = 0.99`, `t_mem = 80 ns`, `t_tlb ≈ 0` (absorbed into pipeline)
- `k = 4`

```
EMAT = 0.99 × 80 + 0.01 × (4×80 + 80)
     = 79.2 + 0.01 × 400
     = 79.2 + 4.0
     = 83.2 ns
```

Even with a 4-level walk, a 99% hit ratio keeps EMAT only 4% above the raw memory access time.

## Sensitivity to Hit Ratio

The hit ratio dominates EMAT. Notice how steeply EMAT rises as `h` falls:

| Hit Ratio `h` | EMAT (t_mem=100 ns, k=2) |
|---|---|
| 1.00 | 100 ns |
| 0.99 | 103 ns |
| 0.95 | 120 ns (approx, simplified) |
| 0.90 | 130 ns |
| 0.80 | 140 ns |
| 0.50 | 200 ns |
| 0.00 | 300 ns |

This is why working-set size matters: a process whose active pages exceed TLB capacity will see a steep drop in hit ratio and a proportional increase in average memory latency.

## Huge Pages and EMAT

Using 2 MB pages instead of 4 KB pages means each TLB entry covers 512× more bytes. For the same number of active bytes, far fewer TLB entries are needed, so the hit ratio stays higher even for large working sets:

```python
# Pages needed to cover a 256 MB working set
pages_4k  = 256 * 1024 * 1024 // (4 * 1024)     # = 65,536
pages_2mb = 256 * 1024 * 1024 // (2 * 1024 * 1024)  # = 128
```

A 64-entry TLB with 4 KB pages covers only 0.1% of the 256 MB working set, but with 2 MB pages it covers the entire thing.

## Common Pitfalls

- **Forgetting that `t_walk` chains into cache misses.** The formula uses `k × t_mem`, but page-table pages may not be cached. A more conservative model replaces each page-table read with a cache-miss penalty.
- **Assuming hit ratio is a property of the hardware.** It is a property of the workload. The same TLB produces vastly different hit ratios for a tight loop vs. pointer-chasing through a large linked list.

**Interview answer:** "EMAT = h × t_mem + (1-h) × (k+1) × t_mem, where h is the TLB hit ratio and k is the number of page-table levels. At 95% hit ratio with a 2-level table and 100 ns memory, EMAT ≈ 120 ns versus 300 ns without a TLB."
