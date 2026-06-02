# Minor vs Major Page Faults

Not all page faults are equally expensive. The OS classifies them into two categories based on whether disk I/O is required. Knowing this distinction is critical for performance profiling and for answering latency questions correctly in interviews.

## Minor page faults (soft faults)

A **minor fault** occurs when the page the process needs is already present in physical memory — it just lacks a mapping in this process's page table. No disk I/O is required. The kernel simply installs a PTE pointing to the existing frame and returns.

Common causes:

- **First access after `fork()`** — the child shares the parent's pages (copy-on-write). Until a write happens, reading those pages causes minor faults to establish mappings.
- **Shared libraries already loaded** — `libc.so` loaded by another process sits in the page cache. A new process mapping it faults in pages that are already in RAM.
- **Anonymous memory after `mmap(MAP_ANONYMOUS)`** — the page is allocated from a pool of pre-zeroed pages.
- **Stack growth** — each new stack page below the current top causes a minor fault.

```bash
# Observe minor and major faults for a command
/usr/bin/time -v ls 2>&1 | grep "page faults"
#   Minor (reclaiming a frame): 236
#   Major (requiring I/O): 0
```

**Cost:** roughly 1–5 microseconds — just kernel overhead, no I/O.

## Major page faults (hard faults)

A **major fault** occurs when the kernel must perform I/O to satisfy the fault — either reading from a swap device or reading from a file on disk.

Common causes:

- **Swapped-out pages** — the page was evicted from RAM and written to swap; it must be read back.
- **First access to a file-backed `mmap`** — e.g., opening a large binary or database file with `mmap()` and reading a page that has not been loaded yet.
- **Page cache eviction** — a page that was in the cache was reclaimed under memory pressure before the process accessed it again.

```python
# Python: mmap a large file — first access to each page causes a major fault
import mmap, os

with open("big_file.bin", "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    _ = mm[0]      # major fault: reads page 0 from disk into page cache
    _ = mm[0]      # no fault: page is now in cache
```

**Cost:** 100–500 microseconds per fault on an SSD; 5–20 milliseconds on a spinning disk.

## Comparison table

| Property | Minor fault | Major fault |
|---|---|---|
| Disk I/O required | No | Yes |
| Typical cost | 1–5 µs | 100 µs – 20 ms |
| Process blocked? | No (runs inline) | Yes (sleeps on I/O) |
| Example cause | Fork child reading parent's pages | First access to swapped page |
| Kernel counter | `ps -o minflt` | `ps -o majflt` |

## How to measure in practice

```bash
# Per-process counters from /proc
cat /proc/<PID>/status | grep -i fault

# Or use perf
perf stat -e minor-faults,major-faults ./your_program

# Cumulative counts since process start
ps -o pid,minflt,majflt -p <PID>
```

## Pitfall: "no major faults" does not mean no I/O

Reads through the kernel's page cache (via `read()`) are not page faults at all — they copy data into user buffers. Major faults are specific to `mmap` and swap.

## Worked example: cold vs warm run

```bash
# Drop page cache to simulate cold start
echo 3 > /proc/sys/vm/drop_caches

time ./my_server   # first run: many major faults (binaries loaded from disk)
time ./my_server   # second run: pages in cache → only minor faults, starts faster
```

The dramatic difference between a "cold" and "warm" start is almost entirely explained by major vs minor fault counts.

**Interview answer:** A minor fault has no disk I/O — the kernel just maps an already-resident page; a major fault requires loading data from disk or swap, blocking the process for hundreds of microseconds to milliseconds.
