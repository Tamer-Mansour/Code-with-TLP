# Trap-and-Emulate and Sensitive Instructions

Before hardware virtualization extensions existed, hypervisors relied on a software technique called **trap-and-emulate** to safely run guest operating systems. Understanding it reveals exactly why hardware support was later needed.

## CPU Privilege Rings (Quick Recap)

x86 CPUs provide four privilege rings (0–3). The OS kernel normally runs in **ring 0** (most privileged); user applications run in **ring 3**.

In a classic VMM without hardware support:

- The **VMM** runs in ring 0.
- The **guest OS** is pushed down to ring 1 (or ring 3 in some designs).
- Guest **user processes** run in ring 3.

## What Are Sensitive Instructions?

A **sensitive instruction** is one whose behavior depends on, or can change, the privilege level or global hardware state. There are two sub-categories:

| Category | Definition | Example |
|---|---|---|
| **Privileged** | Traps (faults) when executed outside ring 0 | `HLT`, `LGDT`, `LIDT` |
| **Control-sensitive** | Changes hardware configuration | Writing to CR3 (page table base) |
| **Behavior-sensitive** | Behaves differently by privilege level | `POPF` (flags register, IF bit) |

**Goldberg's theorem:** A machine is virtualizable if and only if every sensitive instruction is also a privileged instruction.

## How Trap-and-Emulate Works

```
Guest OS tries to execute a privileged instruction
        │
        ▼
  CPU detects ring mismatch → raises a fault (trap)
        │
        ▼
  VMM's trap handler gains control
        │
        ▼
  VMM inspects the instruction, emulates its effect
  in a safe, controlled manner
        │
        ▼
  VMM returns control to the guest (as if nothing happened)
```

The guest OS never knows it was intercepted. From its perspective, the instruction executed normally.

### Example: Guest Writing to CR3

```asm
; Guest OS wants to switch page tables
mov cr3, rax      ; privileged — writing CR3 only allowed in ring 0
```

1. Guest (in ring 1) executes `MOV CR3, RAX`.
2. CPU raises a General Protection Fault — rings 1–3 cannot write CR3.
3. VMM's fault handler runs.
4. VMM updates its **shadow page table** to reflect the guest's desired mapping.
5. VMM writes the _real_ CR3 with the shadow table address.
6. Guest resumes, believing CR3 was written directly.

## The x86 Problem: Non-Virtualizable Instructions

Classic x86 has **17 instructions** (identified by Garfinkel & Rosenblum, 2003) that are sensitive but **not** privileged — they silently behave differently in user mode instead of trapping. The most notorious:

- **`POPF`** — restoring the Interrupt Flag (`IF`) from the stack is silently ignored in ring 3; no trap is raised.
- **`SGDT` / `SIDT`** — store the GDT/IDT address; they succeed in any ring and leak real VMM addresses.
- **`PUSHF`** — pushes flags; in ring 3 the `IF` bit is always shown as 0, so a guest reading flags gets wrong data.

Because these instructions don't trap, pure trap-and-emulate **cannot** virtualize x86 correctly without extra tricks.

## Workarounds Before VT-x

- **Binary translation (BT):** The VMM scans guest code before execution, replaces non-virtualizable instructions with safe call-outs. VMware Workstation used this until VT-x became common.
- **Paravirtualization:** Modify the guest OS to call a hypercall API instead of using sensitive instructions directly (Xen's original approach).

## Performance Implication

Every trap is a ring transition: save all registers, switch stacks, run VMM handler, restore state, return. A guest OS running thousands of traps per second (e.g., during I/O or context switches) incurs measurable overhead — typically hundreds of nanoseconds per trap.

Hardware extensions (VT-x/AMD-V) solve this by adding a dedicated **guest mode** that eliminates the ring-compression problem entirely.

> **Interview answer:** "Trap-and-emulate pushes the guest OS down a privilege ring. Privileged instructions trap to the VMM, which emulates them safely. Classic x86 breaks this because some sensitive instructions don't trap — VMware solved this with binary translation until Intel VT-x added a proper guest execution mode."
