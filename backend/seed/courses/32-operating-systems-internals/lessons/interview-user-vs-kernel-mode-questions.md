# Interview Drill: Common User/Kernel Mode Questions

This lesson collects the most frequently asked interview questions on user/kernel mode, privilege levels, and the kernel boundary. For each question you will find: the core concept being tested, pitfalls that trip up candidates, and a crisp answer you can deliver under pressure.

---

## Q1. What is the difference between user mode and kernel mode?

**Concept tested:** Basic privilege separation.

**Pitfall:** Saying "the kernel is a separate program" — it is part of every process's address space, just not accessible from Ring 3.

> **Answer:** User mode (Ring 3) restricts code to its own virtual address space and blocks privileged CPU instructions. Kernel mode (Ring 0) has unrestricted access to hardware, memory, and all CPU instructions. The boundary is enforced by the CPU in hardware — an illegal operation in Ring 3 raises a hardware exception before executing.

---

## Q2. How does a process make a system call on Linux x86-64?

**Concept tested:** Syscall mechanics.

**Pitfall:** Describing the old `INT 0x80` path (32-bit legacy) instead of the modern `SYSCALL` instruction.

> **Answer:** The process places the syscall number in `rax` and arguments in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`, then executes the `SYSCALL` instruction. The CPU atomically saves `rip`/`rflags` into `rcx`/`r11`, switches to Ring 0 using the address in the `LSTAR` MSR, and the kernel's entry point dispatches to the appropriate handler. On return, `SYSRETQ` restores state and resumes user code.

---

## Q3. What is a privilege level / protection ring?

**Concept tested:** CPU ring architecture.

**Pitfall:** Claiming Linux uses all four rings — it uses only 0 and 3.

> **Answer:** Protection rings are hardware-defined privilege levels. x86 defines rings 0–3; ring 0 can execute any instruction and access all memory, ring 3 is fully restricted. Linux uses ring 0 for the kernel and ring 3 for user processes. Rings 1 and 2 are unused in mainstream OSes.

---

## Q4. What is the difference between a mode switch and a context switch?

**Concept tested:** Distinguishing two related but separate events.

**Pitfall:** Saying "every system call causes a context switch" — most do not.

> **Answer:** A mode switch changes the CPU's privilege level (Ring 3 → Ring 0 → Ring 3) while keeping the same thread running. A context switch replaces the running thread entirely, saving its register state and loading another's. A context switch always passes through kernel mode, but a mode switch need not cause a context switch.

---

## Q5. What happens when Ring-3 code executes a privileged instruction like `HLT`?

**Concept tested:** How privileged instructions are enforced.

**Pitfall:** Saying the OS "intercepts" it — the CPU raises the exception before any software runs.

> **Answer:** The CPU does not execute the instruction. It raises a General Protection Fault (#GP, vector 13), saves execution context on the kernel stack, and jumps to the kernel's #GP handler. The kernel typically sends `SIGSEGV` to the process and terminates it. The enforcement is entirely in hardware; no OS code filters the instruction stream.

---

## Q6. What is kernel space vs user space?

**Concept tested:** Virtual address space layout.

**Pitfall:** Thinking kernel space is a separate physical memory region — it is a virtual address range mapped into every process's page table.

> **Answer:** Both are regions within a process's virtual address space. User space holds the process's code, heap, and stack and is accessible from Ring 3. Kernel space is mapped at a high virtual address range in every process's page table but marked supervisor-only (U/S bit = 0), so any Ring-3 access triggers a page fault. Post-Meltdown (KPTI), most kernel pages are unmapped while the CPU is in user mode.

---

## Q7. How does the MMU enforce that Process A cannot read Process B's memory?

**Concept tested:** Hardware memory isolation.

**Pitfall:** Saying "the OS checks access at runtime in software."

> **Answer:** Each process has its own page table, loaded into `CR3` when scheduled. Process B's physical frames are simply not present in Process A's page table. On any access, the MMU translates through the current `CR3`; it cannot reach an unmapped physical frame. Page table entries also carry permission bits (R/W, U/S, NX) enforced by the MMU on every access.

---

## Q8. Why are system calls more expensive after Meltdown/Spectre mitigations?

**Concept tested:** Performance impact of security fixes.

**Pitfall:** Vague answer — be specific about KPTI and CR3 switching.

> **Answer:** Kernel Page-Table Isolation (KPTI) removed the kernel's full mapping from user-mode page tables. Now, every syscall entry must switch `CR3` to the kernel's page table, and every return must switch back. Changing `CR3` can flush the TLB (unless PCID is used), causing TLB misses that add latency. Workloads with high syscall rates saw 5–30% throughput regressions.

---

## Q9. What is a vDSO and why does it matter?

**Concept tested:** Optimization strategies for kernel boundary crossing.

> **Answer:** The virtual Dynamic Shared Object (vDSO) is a kernel-provided shared library mapped into every process's user-space address space. It exports functions like `clock_gettime()` that can be satisfied by reading a kernel-maintained page in user space — no `SYSCALL` instruction needed, no mode switch. This makes time-reading calls as cheap as a function call rather than a full syscall.

---

## Q10. Can kernel code crash the system? Why or why not?

**Concept tested:** What kernel mode privilege actually means.

**Pitfall:** "No, the OS is safe by design."

> **Answer:** Yes. Kernel mode removes hardware restrictions but does not make code correct. A null pointer dereference in a kernel driver, writing past a kernel buffer, or taking an unhandled exception in Ring 0 can trigger a kernel panic (Linux) or Blue Screen of Death (Windows). There is no outer privilege level to catch kernel bugs on a non-virtualized system.

---

## Quick Reference Table

| Topic | One-Line Answer |
|---|---|
| User vs kernel mode | Privilege level enforced in hardware; Ring 3 vs Ring 0 |
| Mode switch | Same thread, privilege level changes |
| Context switch | Different thread runs; full register save/restore |
| Privileged instruction | CPU raises #GP before executing it |
| Page fault in user space | MMU catches it; kernel sends SIGSEGV or fixes mapping |
| Cost of syscall | ~100–300 ns; higher with KPTI due to CR3 + TLB |
| vDSO | Kernel code in user space; avoids syscall for time calls |
| KPTI | Removed kernel mapping from user page tables; fixed Meltdown |
