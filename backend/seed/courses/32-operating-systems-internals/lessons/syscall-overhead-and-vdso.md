# System Call Overhead and the vDSO

System calls are essential but not free. Understanding their cost — and how Linux minimizes it for common cases — is relevant to performance-sensitive code and to interview discussions about OS optimization.

## What Makes System Calls Expensive?

A naive mental model says "a syscall just switches a flag." The real cost is several independent penalties:

1. **Privilege-level switch** — `syscall`/`sysret` flush parts of the CPU pipeline.
2. **Register save/restore** — the kernel saves all user registers to the kernel stack (`pt_regs`) and restores them on return.
3. **Stack switch** — from user stack to per-thread kernel stack (accessed via `GSBASE`).
4. **Kernel entry/exit overhead** — Spectre/Meltdown mitigations (KPTI, IBRS, STIBP) add substantial cost on post-2018 kernels.
5. **TLB and cache effects** — switching page tables (KPTI) flushes TLB entries; the cold kernel code path may cause instruction cache misses.

### Measured Cost (x86-64, Linux 6.x)

| Condition | Typical round-trip latency |
|---|---|
| Pre-Meltdown patch | ~100 ns |
| Post-KPTI (Meltdown mitigated) | ~200–400 ns |
| vDSO (no kernel entry) | ~3–10 ns |

Even at 200 ns, a program making 1 million syscalls per second spends 200 ms/s — 20% of one CPU core — just on syscall overhead.

## The vDSO (Virtual Dynamic Shared Object)

The vDSO is a small shared library that the kernel **maps into every process's address space automatically** at a random address (ASLR applies). It contains implementations of certain syscalls that can be answered without entering the kernel.

```bash
# See the vDSO in any process's memory map
cat /proc/self/maps | grep vdso
# Output:
# 7ffd3b7fb000-7ffd3b7fd000 r-xp 00000000 00:00 0  [vdso]
```

### Which Calls Use the vDSO?

```
clock_gettime(CLOCK_REALTIME, &ts)   → vDSO reads kernel timekeeping struct
clock_gettime(CLOCK_MONOTONIC, &ts)  → vDSO (fast path)
gettimeofday(&tv, NULL)              → vDSO
time(NULL)                           → vDSO
getcpu(&cpu, &node)                  → vDSO
```

These functions are called extremely frequently (e.g., every log timestamp, every benchmark). The vDSO implementation reads a shared memory region called `vsyscall_gtod_data` that the kernel updates on each timer tick — no ring switch needed.

```c
// vDSO clock_gettime (conceptual, not exact source)
int __vdso_clock_gettime(clockid_t clk, struct timespec *ts)
{
    // Read from kernel-maintained shared page — no syscall
    struct vdso_data *vd = __get_vdso_data();
    u64 ns = read_seqcount_begin_and_get(vd);
    ts->tv_sec  = ns / NSEC_PER_SEC;
    ts->tv_nsec = ns % NSEC_PER_SEC;
    return 0;
}
```

If the fast path fails (sequence counter changed, indicating concurrent update), the vDSO falls back to the real syscall.

## vsyscall: The Deprecated Predecessor

Before vDSO, Linux mapped a fixed-address page (`0xffffffffff600000`) containing `gettimeofday` and `time` as callable code. This was removed because fixed addresses are a security liability (no ASLR, ROP gadget source). The vDSO replaced it with a position-independent library.

## Reducing Syscall Frequency in Practice

- **Batch I/O** — use `readv`/`writev` to transfer multiple buffers in one syscall.
- **Large buffers** — `read(fd, buf, 65536)` rather than 1-byte reads in a loop.
- **io_uring** — submit 1000 operations, call `io_uring_submit` once.
- **Avoid `clock_gettime` in hot loops** — or ensure glibc uses the vDSO (it does by default).
- **`strace -c`** — count syscalls and their time to find bottlenecks.

```bash
# Profile syscall frequency of a program
strace -c ./my_program
# Output shows count, errors, total time, avg time per syscall
```

## Benchmarking Syscall Cost

```c
#include <time.h>
// Measure raw syscall cost with clock_gettime (goes through vDSO)
// vs. getpid() which always enters the kernel
struct timespec t0, t1;
clock_gettime(CLOCK_MONOTONIC, &t0);
for (int i = 0; i < 1000000; i++)
    getpid();   // forces real syscall
clock_gettime(CLOCK_MONOTONIC, &t1);
// Divide elapsed ns by 1e6 for per-call cost
```

**Interview answer:** System calls cost 200–400 ns post-Meltdown mitigation due to privilege switch, register save, and KPTI page-table flush; the vDSO eliminates kernel entry for time-related calls by mapping a kernel-updated shared page into every process, reducing `clock_gettime` to ~3–10 ns.
