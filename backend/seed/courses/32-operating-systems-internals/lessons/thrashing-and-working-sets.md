# Thrashing and the Working Set Model

Thrashing is a pathological state where a system spends more time handling page faults than doing useful work. Understanding it — and the working set model that prevents it — is a cornerstone of OS memory management theory and a frequent interview topic.

## What is thrashing?

Thrashing occurs when the total memory demand of all running processes exceeds available physical RAM by so much that pages are constantly being evicted and immediately faulted back in. The CPU utilization curve paradoxically *drops* as more processes are added, because every process is blocking on I/O waiting for its pages.

```
CPU Utilization
  100% ─────────────────╮
                         ╲
                          ╲
                           ╲ ← thrashing begins here
   0% ────────────────────────────────► Number of processes
                           ↑
                    Optimal multiprogramming degree
```

### The thrashing feedback loop

1. A process needs more pages than are free.
2. The page-replacement algorithm evicts pages belonging to *other* processes.
3. Those processes immediately fault them back in.
4. Everyone is waiting on disk I/O.
5. CPU utilization collapses to near zero.
6. The OS scheduler may load *more* processes (thinking the CPU is idle), making things worse.

## The Working Set Model

Peter Denning's **working set** is the set of pages a process has actively used within the last Δ (delta) time units. It captures the principle of **temporal locality**: programs repeatedly access the same subset of pages in any short window.

```
Working Set W(t, Δ) = {pages accessed in time interval (t−Δ, t]}
```

- If all of a process's working set fits in RAM → it runs without faulting.
- If it does not fit → the process will thrash on its own subset.

### Working set size example

Suppose a process accesses pages in this sequence over 10 time steps:
```
Time:   1  2  3  4  5  6  7  8  9  10
Page:   A  B  C  A  B  D  A  B  C  D
```

With Δ = 4, the working set at t=10 is: `{A, B, C, D}` — 4 pages must be resident.

## Policy implications

### Admission control (preventing thrashing)

The OS should only admit a new process if:
```
sum of all working set sizes ≤ available physical frames
```

If this condition would be violated, suspend (swap out) a process entirely — it is better to fully swap one process than to thrash many.

### Working Set Page Replacement

In practice, exact working sets are expensive to track. Two approximations are common:

| Algorithm | Mechanism |
|---|---|
| WSClock | Clock hand skips pages accessed within Δ ticks; evicts only "old" pages |
| PFF (Page-Fault Frequency) | Increase Δ (give more frames) if fault rate is too high; decrease Δ if fault rate is low |

**Page-Fault Frequency (PFF) control:**
```
if fault_rate > upper_threshold:
    allocate more frames to this process
elif fault_rate < lower_threshold:
    reclaim frames from this process
```

## Detecting thrashing in practice

```bash
# High swap I/O is the clearest signal
vmstat 1       # check si (swap-in) and so (swap-out) columns
iostat -x 1    # check %util on swap device

# Kernel metric: pgscan vs pgsteal
cat /proc/vmstat | grep -E "pgscan|pgsteal|pageoutrun"
# If pgscan >> pgsteal, the system is reclaiming aggressively → near thrashing
```

## Mitigations

- **Reduce multiprogramming degree** — swap out whole processes.
- **Increase physical RAM** — the most effective fix.
- **Use `mlock`** — pin critical pages for latency-sensitive processes.
- **`cgroups` memory limits** — isolate processes; prevent one from stealing from others.
- **ZRAM / zswap** — compress pages in RAM before evicting to disk, buying headroom.

```bash
# Linux: swap tendency (0=avoid swap, 100=swap aggressively)
cat /proc/sys/vm/swappiness
# Lowering this value reduces thrashing risk on desktop/server systems
```

## Worked analogy

Think of physical frames as desk space and working sets as the documents each person needs open. If ten people need 5 documents each but the desk fits only 30 documents, they will constantly swap documents in and out — thrashing. The fix is either a bigger desk or fewer people working simultaneously.

**Interview answer:** Thrashing is when the total working set size of all processes exceeds available RAM, causing constant page eviction and re-loading; the working set model prevents it by admitting new processes only when their working set fits in memory, and suspending processes when the sum of working sets exceeds capacity.
