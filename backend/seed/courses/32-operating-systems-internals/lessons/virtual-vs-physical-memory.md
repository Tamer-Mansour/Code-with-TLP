# Virtual vs Physical Memory

Every program you run believes it owns a vast, private memory space starting at address 0. The hardware and operating system conspire to make that illusion real — this is the foundation of **virtual memory**.

## Physical Memory: What Actually Exists

Physical memory (RAM) is finite. A machine with 16 GB of RAM has exactly 16 GB of physical addresses, numbered from `0x0000_0000_0000` to roughly `0x0003_FFFF_FFFF`. These addresses map directly to physical DRAM chips on the motherboard. Every byte has exactly one physical address, and two processes cannot safely share a physical address without coordination.

## Virtual Memory: The Illusion

Each process is given its own **virtual address space** — a range of addresses that exist only from the process's point of view. On a 64-bit Linux system, a user-space process can address up to 128 TB (`0x0000_0000_0000_0000` to `0x0000_7FFF_FFFF_FFFF`). That is far larger than any physical RAM available today.

When the process reads or writes a virtual address, the **Memory Management Unit (MMU)** silently translates it to the corresponding physical address before the memory bus ever sees the request. If no translation exists, the CPU raises a **page fault** and the OS either maps physical memory on demand or terminates the process.

## The Translation Mechanism at a Glance

```
Process A                 MMU                  Physical RAM
───────────────           ──────────────        ──────────────
Virtual 0x1000  ───────►  Page table lookup ──► Physical 0xA3000
Virtual 0x2000  ───────►  Page table lookup ──► Physical 0x52000

Process B
───────────────
Virtual 0x1000  ───────►  Page table lookup ──► Physical 0xD1000
```

Both Process A and Process B use virtual address `0x1000`, but the MMU maps them to completely different physical locations. Neither process can see or corrupt the other's data.

## Key Differences at a Glance

| Property | Physical Address | Virtual Address |
|---|---|---|
| Who uses it | RAM chips, DMA, hardware | CPU instructions, compilers |
| Uniqueness | Globally unique | Unique only within one process |
| Range | Limited by installed RAM | Limited by address-bus width (48–57 bits on x86-64) |
| Persistence | Always valid | Valid only while mapping exists |
| Isolation | None inherently | Enforced by MMU + OS |

## Why This Matters for Programs

- **Deterministic linking**: The compiler and linker can always assume the program's `.text` section starts at a known virtual address (e.g., `0x400000` on Linux). The OS arranges the physical placement independently.
- **No overlap bugs**: Two processes using `malloc` that both return virtual address `0x1234_5678` are not sharing memory — they are in separate address spaces.
- **Sparse allocation**: A process can reserve a huge virtual range (e.g., for a memory-mapped file) without consuming physical RAM until pages are actually accessed.

## Common Pitfall

Beginners often assume that printing a pointer address in two different processes and seeing the same value means the processes share memory. They do not — the addresses are virtual and map to different physical locations.

```c
// In process A and process B independently:
int x = 42;
printf("%p\n", (void *)&x);   // Both might print 0x7fff...abc0
// They are NOT the same memory location!
```

**Interview answer:** Virtual addresses are per-process labels translated by the MMU to physical RAM locations at runtime, providing isolation and allowing each process to believe it owns the entire address space.
