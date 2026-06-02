# The Memory Management Unit (MMU)

The **Memory Management Unit (MMU)** is a hardware component — on modern CPUs it is integrated directly on-die — whose sole job is to translate virtual addresses emitted by the CPU core into physical addresses before they reach the memory bus. Without the MMU, virtual memory is just a software fiction; with it, the translation is enforced in hardware on every single memory access.

## Where the MMU Sits

```
CPU Core
 ├─ Instruction fetch (virtual addr) ──► MMU ──► L1 I-cache (physical addr)
 ├─ Load/Store unit  (virtual addr) ──► MMU ──► L1 D-cache (physical addr)
 └─ (PTBR register points MMU at current page table)
                                          │
                                     TLB (fast cache)
                                          │
                              Page Table Walk (on TLB miss)
                                          │
                                    Physical RAM
```

The OS writes the base address of the current process's page table into the **Page Table Base Register** (called `CR3` on x86-64). On every context switch the OS updates `CR3` to the new process's page table, instantaneously changing the entire virtual-to-physical mapping.

## The Translation Lookaside Buffer (TLB)

Walking a multi-level page table for every memory access would be prohibitively slow. The MMU caches recent translations in a small, fully-associative cache called the **TLB**.

- **TLB hit** (~1 cycle): The translation is found in the cache. No table walk needed.
- **TLB miss** (~10–100 cycles): The hardware page-table walker reads the page table from RAM, loads the result into the TLB, and retries.
- **TLB flush**: On a context switch, stale translations must be evicted. x86-64 does this by reloading `CR3`. Modern CPUs add **PCID (Process-Context Identifiers)** to tag entries per-process and avoid a full flush.

Typical TLB sizes:

| Level | Entries (approx.) | Covers |
|---|---|---|
| L1 iTLB | 128–256 | Instructions |
| L1 dTLB | 64–128 | Data |
| L2 TLB (unified) | 1,024–4,096 | Both |

## Page Fault Handling

When the MMU cannot find a valid translation — either because the page is not present or because the access violates permissions — it raises a **page fault exception**, transferring control to the OS page-fault handler.

```
┌──────────────────────────────────────────┐
│             Page Fault Handler           │
│  Is the virtual address valid?           │
│    No  → SIGSEGV (segfault)              │
│    Yes → Is page on disk (swapped out)?  │
│            Yes → Read from swap, map,    │
│                  return (major fault)    │
│            No  → Allocate new frame,     │
│                  zero it, map, return    │
│                  (minor fault)           │
└──────────────────────────────────────────┘
```

### Fault Types

| Type | Cause | Typical cost |
|---|---|---|
| Minor fault | Page not yet mapped; no disk I/O needed | ~1 µs |
| Major fault | Page swapped to disk; requires I/O | ~5–15 ms |
| Protection fault | Access violates R/W/X permissions | → SIGSEGV |

## Permissions the MMU Enforces

Each page table entry carries permission bits:

- **Present (P):** Page is in RAM; translation is valid.
- **Writable (W):** Store instructions are allowed.
- **User/Supervisor (U/S):** User-mode code may access this page.
- **Execute-Disable (XD/NX):** CPU may not fetch instructions from this page.

These bits implement **W^X** (write XOR execute) policies, making it much harder for an attacker to inject and run shellcode.

## Common Pitfall

Developers sometimes assume that touching a freshly `malloc`-ed buffer is free. In reality the first write to each 4 KB page triggers a minor page fault, requiring the OS to zero the physical frame and update the page table. For latency-sensitive code, pre-faulting (e.g., `mlock`) eliminates this surprise.

```c
// Pre-fault all pages to avoid runtime minor faults:
char *buf = malloc(1 << 20);   // 1 MB, not yet backed
mlock(buf, 1 << 20);           // OS maps all pages now
```

**Interview answer:** The MMU is on-die hardware that translates every virtual address to a physical address using the process's page table, with the TLB caching recent translations for speed, and raises a page fault exception whenever a mapping is absent or a permission is violated.
