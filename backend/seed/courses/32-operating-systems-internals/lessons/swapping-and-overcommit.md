# Swapping, Overcommit, and the Swap File

Virtual memory lets a system **promise more memory than it physically has**. This is only sustainable because most of that promised memory is either never accessed or can be temporarily stored on disk. Understanding swapping and overcommit is essential for diagnosing production memory pressure.

## What Is Swapping?

**Swapping** (also called **paging out**) is the OS evicting a physical memory page to disk when RAM is under pressure, freeing that physical frame for another use. Later, when the process accesses the evicted virtual address, a **major page fault** brings it back.

```
RAM is full → OS selects a victim page (LRU heuristic)
           → writes victim to swap space on disk
           → marks its page table entry as "not present"
           → frees the physical frame for another process

Later: process accesses the virtual address
     → MMU: entry not present → page fault
     → OS: finds page in swap → reads it back
     → restores page table entry → resumes process
```

The key performance cost: a single swap-in requires a **disk read** (~0.1 ms SSD, ~5 ms HDD), three to four orders of magnitude slower than a RAM access (~100 ns).

## Swap Space

On Linux, swap space is either a dedicated **swap partition** or a **swap file**:

```bash
# Check current swap usage
free -h
swapon --show

# Create a 4 GB swap file
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

Windows uses a swap file called `pagefile.sys`. macOS uses compressed memory (zswap-like) before writing to disk.

## Overcommit

**Overcommitting** means the OS allows the total committed virtual memory across all processes to exceed physical RAM + swap. Linux overcommits by default.

### Why It Works in Practice

- `malloc(1 GB)` does not immediately consume 1 GB of physical memory — it reserves virtual space.
- Only pages that are **written** get physical frames (demand paging + copy-on-write).
- Most processes have large virtual allocations with a small active working set.

### Overcommit Modes (Linux)

| `/proc/sys/vm/overcommit_memory` | Behavior |
|---|---|
| `0` (default) | Heuristic — allow reasonable overcommit, reject obvious abuse |
| `1` | Always allow — never refuse `malloc` (dangerous) |
| `2` | Never overcommit — total virtual commit ≤ swap + RAM × `overcommit_ratio` |

```bash
# Check current mode
cat /proc/sys/vm/overcommit_memory

# Check how much has been committed
cat /proc/meminfo | grep Commit
# CommitLimit: total allowed; Committed_AS: total committed
```

## The OOM Killer

When overcommit mode 0 or 1 is used and the system genuinely runs out of both RAM and swap, the Linux **OOM (Out-Of-Memory) killer** selects a process to terminate:

- Each process has an **oom_score** (0–1000) computed from RSS, swap usage, process age, and the process's `oom_score_adj` value.
- The process with the highest score is killed with `SIGKILL`.

```bash
# Protect a critical process from the OOM killer
echo -1000 > /proc/<pid>/oom_score_adj   # -1000 = never kill

# Check a process's current OOM score
cat /proc/<pid>/oom_score
```

## Swap Thrashing

**Thrashing** occurs when the combined working sets of all processes exceed RAM and every memory access triggers a page fault that evicts another needed page:

```
Process A needs page X → evict page Y
Process B needs page Y → evict page X
Process A needs page X → evict page Y ...  (loop)
```

Symptoms: CPU nearly idle, disk I/O pegged at 100%, system appears frozen.

Diagnosis:

```bash
# Watch swap usage and page fault rates
vmstat 1         # si (swap in), so (swap out) columns
sar -B 1         # pgpgin/s, pgpgout/s
```

Solutions: add RAM, reduce memory footprint, limit overcommit, or use `cgroups` memory limits to isolate workloads.

## Common Pitfall

Assuming that `malloc` succeeding means memory is available. With overcommit mode 1, `malloc` always succeeds — but the first write to each page might fail with an OOM kill. Programs that depend on `malloc` returning `NULL` to detect OOM will never see it under aggressive overcommit.

**Interview answer:** Swapping evicts inactive physical pages to disk, freeing frames for other processes at the cost of major-fault latency; overcommit lets total virtual commitments exceed RAM+swap because demand paging means most committed memory is never touched simultaneously, and the OOM killer handles the rare case when physical resources are genuinely exhausted.
