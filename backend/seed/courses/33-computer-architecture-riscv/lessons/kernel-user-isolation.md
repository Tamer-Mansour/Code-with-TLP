# Kernel/User Isolation and Page Permissions

Isolation between user processes and the kernel is the cornerstone of operating system security. On RISC-V, isolation is enforced by a combination of privilege levels, page table permissions, and Physical Memory Protection (PMP). Understanding how these layers work together — and where each one can fail — is fundamental to OS security.

## Two Lines of Defense

RISC-V uses two complementary mechanisms:

1. **Privilege levels** — hardware checks whether the current mode is allowed to execute a given instruction or access a given CSR.
2. **Virtual memory + page permissions** — the MMU checks whether the current privilege level is allowed to access a given virtual address.

Either mechanism alone would be insufficient. Privilege levels without virtual memory would allow any U-mode code to forge physical addresses. Virtual memory without privilege levels would allow malicious kernel code to be called directly from user space.

## Page Table Permission Bits

Every leaf page table entry (PTE) on RISC-V Sv39 carries these permission bits:

| Bit | Name | Meaning |
|-----|------|---------|
| V   | Valid | This PTE is active |
| R   | Read | Page is readable |
| W   | Write | Page is writable |
| X   | Execute | Page is executable |
| U   | User | U-mode code can access this page |
| G   | Global | Mapping exists in all address spaces |
| A   | Accessed | Hardware sets on any access |
| D   | Dirty | Hardware sets on write |

**Critical rule:** A page without the `U` bit set is accessible only to Supervisor mode. A page with the `U` bit set is accessible in U-mode but inaccessible to S-mode **unless** `sstatus.SUM` is set.

```
Kernel text:  R=1 X=1 W=0 U=0  → S-mode only, executable
Kernel data:  R=1 X=0 W=1 U=0  → S-mode only, writable
User text:    R=1 X=1 W=0 U=1  → U-mode can execute
User stack:   R=1 X=0 W=1 U=1  → U-mode can read/write
```

## The SUM Bit and Kernel Safety

By default, when the kernel accesses a U-mode virtual address (e.g., to copy data from a user buffer), the hardware raises a page fault because the `U` bit is set. To allow this, the kernel sets `sstatus.SUM`:

```c
// xv6-riscv: temporarily allow kernel to access user pages
void copyout(pagetable_t pt, uint64 dstva, char *src, uint64 len) {
    // walks page table, sets SUM if needed, copies, clears SUM
}
```

Keeping `SUM` set permanently would be a security vulnerability — a kernel pointer bug could then silently read/write user memory.

## The RISC-V Guard Page Pattern

Stack overflows are caught by placing an unmapped (V=0) "guard page" just below the lowest valid stack page:

```
+-------------------+  <- stack top (highest address)
|   stack (R/W/U)   |
+-------------------+  <- stack bottom
|   guard page (V=0)|  <- access here → page fault → kernel kills process
+-------------------+
|   heap            |
```

The kernel's page fault handler checks whether the fault address falls in the guard page region and sends `SIGSEGV` to the process.

## Physical Memory Protection (PMP)

PMP is a M-mode mechanism to restrict what physical addresses S-mode (and U-mode) code can access, even if the page table would otherwise allow it. PMP entries are configured via CSRs (`pmpaddr0`–`pmpaddr15`, `pmpcfg0`–`pmpcfg3`):

```asm
# Allow S-mode full access to all physical memory (common OpenSBI setup)
li   t0, -1         # all bits set = top of address space
csrw pmpaddr0, t0
li   t0, 0x1F       # cfg: NAPOT, R+W+X, S+U access
csrw pmpcfg0,  t0
```

PMP is the last line of defense — it prevents even a compromised kernel from accessing firmware memory.

## Meltdown and the Lesson for RISC-V

The Meltdown vulnerability (x86, 2018) exploited the fact that kernel page mappings were present in every process's page table — speculative execution could transiently read kernel data before the permission check fired. The fix was Kernel Page Table Isolation (KPTI): kernel mappings are absent from user-mode page tables entirely. RISC-V designs can apply the same principle — removing kernel PTEs from the U-mode page table at the cost of a full TLB flush on every syscall and trap return.

## Common Pitfalls

- Mapping kernel text as `U=1` accidentally — allows user code to call kernel functions.
- Forgetting to set `W=0` on executable pages — enables code injection (W^X violation).
- Leaving `SUM` set in `sstatus` after a `copyin`/`copyout` — weakens isolation.
- Using identity-mapped physical addresses for user data — bypasses virtual memory protection entirely.

> **Interview answer:** RISC-V enforces kernel/user isolation via privilege levels (U vs S mode) and page table U-bits — kernel pages lack the U bit so user code raises a page fault accessing them; the kernel must set `sstatus.SUM` to transiently access user pages, and PMP provides an additional M-mode layer restricting physical memory access for S-mode code.
