# The Performance Cost of Entering the Kernel

Crossing the user/kernel boundary is not free. Every system call, interrupt, and exception burns CPU cycles that your application could have spent doing real work. Knowing where the cost comes from — and how to minimize it — is a skill that separates senior engineers from juniors.

## Where the Cycles Go

A single system call on a modern Linux x86-64 machine costs roughly **100–300 ns** under normal conditions. Here is the breakdown:

| Cost Component | Why It Exists |
|---|---|
| `SYSCALL` instruction itself | Saves `rip`, `rflags` into `rcx`/`r11`; loads kernel `rsp` from MSR |
| Register save/restore | Kernel must preserve all user registers it clobbers |
| Stack switch | Switch from user stack to per-thread kernel stack |
| Page table switch (KPTI) | Swap CR3 from user shadow table to full kernel table; TLB flush |
| Syscall dispatch | Look up handler by syscall number, validate arguments |
| Actual work | The thing you asked for (e.g., writing to a file descriptor) |
| Return path | Reverse of entry: restore registers, switch page table, `SYSRETQ` |

## The KPTI Tax

Before the **Meltdown** fix (KPTI, 2018), the kernel was mapped into every process's page table. No page-table switch was needed on syscall entry. After KPTI:

- Entry: switch `CR3` from the user-shadow page table to the full kernel page table.
- Exit: switch back.

Switching `CR3` invalidates TLB entries (on CPUs without PCID support), causing TLB misses for a while after the return. Workloads that make many syscalls — web servers, databases, shells — saw **5–30% slowdowns** on some benchmarks.

```bash
# Measure raw syscall overhead (Linux)
# 'getpid' is nearly a no-op — measures call overhead alone
perf stat -e cs ./syscall_bench   # cs = context switches

# Or time a tight loop of getpid():
python3 -c "
import os, time
N = 1_000_000
t0 = time.perf_counter()
for _ in range(N): os.getpid()
print(f'{(time.perf_counter()-t0)/N*1e9:.1f} ns/call')
"
```

## TLB Pressure

The **Translation Lookaside Buffer (TLB)** caches virtual→physical address translations. A kernel entry that changes `CR3` can flush the TLB (unless **PCID — Process Context Identifiers** are in use). After the flush, the first accesses to kernel and then user pages cause TLB misses that fetch from page tables in main memory — adding latency.

CPUs with PCID (essentially all modern x86-64 CPUs) tag TLB entries with a process ID, allowing `CR3` switches without a full flush. Linux enables PCID when available, recovering much of the KPTI overhead.

## Cache Pollution

The kernel's instruction and data cache footprint is different from the user program's. Entering the kernel evicts some of the program's hot cache lines. When returning to user mode, the program suffers cache misses until the working set warms up again.

## Strategies to Reduce Syscall Frequency

| Technique | How It Helps |
|---|---|
| **Batching** | `writev` instead of multiple `write` calls; `sendmmsg` for UDP |
| **Large I/O buffers** | One `read(fd, buf, 65536)` instead of 65536 `read` calls of 1 byte |
| **`io_uring`** | Submit/complete I/O via shared ring buffers; batch many ops in one syscall or zero-syscall with SQ polling |
| **`mmap` for file I/O** | Memory-mapped files avoid `read`/`write` syscalls; page faults handle I/O lazily |
| **`vDSO` (virtual Dynamic Shared Object)** | Maps kernel code into user space so certain syscalls (`gettimeofday`, `clock_gettime`) run without a privilege switch at all |
| **`sendfile` / `splice`** | Move data from kernel buffer to socket without copying to user space |

## vDSO: Syscalls Without a Privilege Switch

The kernel exports a small shared library into every process's address space. Functions like `clock_gettime()` can be satisfied entirely from user space by reading a kernel-maintained page — no `SYSCALL` instruction, no mode switch.

```bash
# See the vDSO mapped in a process
cat /proc/self/maps | grep vdso
# 7ffd5a7f1000-7ffd5a7f3000 r-xp 00000000 00:00 0  [vdso]
```

## Common Pitfalls

- **"System calls are cheap enough to ignore"**: For most apps, yes. For high-frequency trading, game engines, or high-throughput servers, syscall overhead is a real optimization target.
- **"Avoiding all syscalls is the goal"**: No — necessary syscalls cannot be avoided. The goal is to batch and minimize unnecessary ones.
- **"Context switches are the only kernel-entry cost"**: A syscall that returns immediately (no context switch) still pays the entry/exit tax.

## Interview Answer

> **Q: Why are system calls expensive, and how can you reduce the cost?**
>
> **Interview answer:** System calls require a privilege mode switch (saving registers, switching stacks, and since Meltdown mitigations, switching page tables and potentially flushing the TLB), plus cache disruption on return. Cost is reduced by batching syscalls (large buffers, `writev`, `io_uring`), using memory-mapped I/O, and leveraging vDSO for time-related calls that the kernel exports to user space.
