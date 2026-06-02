# The Full Interrupt Handling Flow

Handling an interrupt is a precisely choreographed sequence involving hardware, firmware, and the OS kernel. Understanding this flow end-to-end is essential for debugging timing issues, writing device drivers, and reasoning about OS behavior under load.

---

## High-Level Overview

```
Device asserts IRQ line
        │
        ▼
Interrupt Controller (PIC/APIC) arbitrates and sends vector to CPU
        │
        ▼
CPU finishes current instruction, checks IF flag
        │
        ▼
CPU saves state (RFLAGS, CS, RIP, optional error code) on kernel stack
        │
        ▼
CPU looks up handler in IDT using vector number
        │
        ▼
CPU switches to kernel privilege level (CPL 0) and jumps to ISR
        │
        ▼
ISR runs: acknowledges hardware, does minimal work
        │
        ▼
ISR executes IRET — CPU restores state and resumes interrupted code
```

---

## Step 1 — Device Raises an IRQ

A hardware device (e.g., NIC, keyboard, timer) asserts a **hardware interrupt request** line. On a modern system, this is routed through the **APIC** (Advanced Programmable Interrupt Controller) rather than the legacy 8259A PIC.

The APIC assigns a vector number and signals the CPU via the system bus.

---

## Step 2 — CPU Completes the Current Instruction

The CPU checks for pending interrupts **at instruction boundaries**. It will not interrupt mid-instruction. If `IF=0` (interrupts masked), the CPU defers the interrupt; otherwise it proceeds.

---

## Step 3 — CPU Saves Interrupted State

The hardware automatically pushes onto the **kernel stack**:

```
┌──────────────┐  ← old RSP (user stack top)
│    SS        │  (only if privilege level change)
│    RSP       │  (only if privilege level change)
│   RFLAGS     │
│    CS        │
│    RIP       │
│  Error Code  │  (only for some exceptions, e.g., #PF)
└──────────────┘  ← new RSP (kernel stack)
```

This happens **atomically in hardware** — no software instruction is executed between the interrupt firing and the push completing.

---

## Step 4 — CPU Reads the IDT

Using the vector number as an index into the IDT (base stored in IDTR), the CPU reads the 16-byte gate descriptor, extracts the 64-bit handler address, and verifies the `P` (present) bit and `DPL` (privilege level).

For an **interrupt gate**, the CPU also **clears IF** (disables further maskable interrupts).

---

## Step 5 — Privilege Level Switch

If the interrupted code was running at CPL 3 (user mode) and the handler requires CPL 0 (kernel mode):

1. CPU reads the kernel stack pointer from the **TSS** (Task State Segment).
2. CPU switches to the kernel stack.
3. CPU pushes the user-mode SS and RSP (saved from before the switch).

If already in CPL 0, no stack switch occurs — the ISR uses the same kernel stack.

---

## Step 6 — ISR Executes

The ISR runs in kernel context. It:

- Saves any additional registers it will use (the hardware only saves RFLAGS/CS/RIP).
- Sends **EOI** (End Of Interrupt) to the APIC (`mov [LAPIC_EOI], 0`).
- Performs the minimal required work.
- Queues deferred work if needed (softirq, tasklet, workqueue).
- Restores saved registers.

---

## Step 7 — IRET Returns Control

`iret` (or `iretq` in 64-bit) **atomically** pops RFLAGS, CS, and RIP from the kernel stack and, if there was a privilege change, also pops RSP and SS. The CPU resumes executing the interrupted code at the exact instruction that was next.

```asm
; ISR epilogue (64-bit)
pop  rdi
pop  rsi
pop  rax
iretq        ; restores RFLAGS (including IF), CS, RIP, RSP, SS
```

---

## Worked Example: Timer Tick on Linux x86-64

```
1. APIC timer fires → vector 0xEF sent to CPU core 0
2. CPU finishes current user instruction
3. Hardware pushes RFLAGS, CS=user, RIP=user_addr, SS, RSP onto kernel stack
4. CPU sets RSP = kernel_stack (from TSS)
5. CPU jumps to timer_interrupt() via IDT[0xEF]
6. ISR: update jiffies, run scheduler tick, call run_local_timers()
7. APIC EOI written
8. If schedule() needed: context switch; else iretq back to user
```

---

## Common Pitfalls

- **Missing EOI** — the APIC never clears the interrupt; the ISR is called in a tight loop.
- **Wrong stack after privilege switch** — forgetting to set up the TSS correctly causes a triple fault on first user-mode interrupt.
- **RFLAGS corruption** — if the ISR modifies RFLAGS without restoring it, interrupts may stay disabled after `iret`.

> **Interview answer:** When an interrupt fires, the CPU finishes its current instruction, checks the IF flag, then the hardware atomically saves RFLAGS/CS/RIP onto the kernel stack, switches privilege levels if needed, reads the IDT entry for the vector, and jumps to the ISR. The ISR acknowledges the hardware, does minimal work, and executes IRET to atomically restore the interrupted state.
