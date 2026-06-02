# The Interrupt Service Routine (ISR)

When an interrupt fires, the CPU hands control to a small, carefully written piece of code called the **Interrupt Service Routine** (ISR), also called an **interrupt handler**. Writing a correct ISR is one of the most constraint-laden tasks in systems programming — every microsecond and every CPU register matters.

---

## What an ISR Must Do

An ISR has one job: **respond to the interrupt quickly, safely, and leave the CPU in exactly the state it was in before the interrupt arrived**.

Minimal ISR lifecycle:

1. **Save state** — all registers that the ISR will modify must be pushed onto the (kernel) stack.
2. **Acknowledge the interrupt** — tell the hardware the IRQ has been received (e.g., write EOI to the PIC/APIC).
3. **Do the minimal work** — read data from the device, queue a job for a bottom-half handler.
4. **Restore state** — pop saved registers.
5. **Return with `iret`** — restores the interrupted code's EFLAGS, CS, and EIP atomically.

---

## ISR Constraints

| Constraint | Reason |
|------------|--------|
| Must NOT sleep or block | Sleeping would deadlock the kernel |
| Must NOT call `malloc` | Memory allocation may sleep or require locks |
| Must be re-entrant safe | Higher-priority IRQs can nest |
| Must be as short as possible | While the ISR runs, lower-priority IRQs may be missed |
| Must acknowledge the hardware | Else the hardware keeps asserting the IRQ line |

---

## Top Half vs Bottom Half

Because ISRs must be fast, Linux and most kernels split work into two layers:

- **Top half (ISR)** — runs immediately with interrupts disabled. Acknowledges the hardware and queues the data.
- **Bottom half** — runs later, with interrupts re-enabled, when it is safe to do more work.

Bottom-half mechanisms in Linux:

| Mechanism | Characteristics |
|-----------|----------------|
| Softirq | Runs in interrupt context; pre-allocated, high priority |
| Tasklet | Built on softirq; serialized per-tasklet |
| Workqueue | Runs in process context; can sleep |

---

## x86 ISR Example (Bare-metal C)

```c
// Minimal x86 ISR for IRQ0 (8253 timer)
// Compiled with -mgeneral-regs-only; no FPU/SSE in ISR
__attribute__((interrupt))
void timer_isr(struct interrupt_frame *frame) {
    // 1. Work — increment tick counter
    system_ticks++;

    // 2. Send End-Of-Interrupt to the APIC
    *((volatile uint32_t *)LAPIC_EOI) = 0;

    // 3. Return — compiler emits 'iret' automatically
}
```

The `__attribute__((interrupt))` hint tells GCC to emit the proper prologue/epilogue (save all caller-saved registers + use `iret` instead of `ret`).

---

## Linux Kernel ISR Registration

```c
// Register a handler for IRQ 10 (e.g., a NIC)
int err = request_irq(
    10,               // IRQ number
    my_nic_handler,   // ISR function pointer
    IRQF_SHARED,      // allow IRQ sharing
    "my_nic",         // name shown in /proc/interrupts
    dev               // device cookie passed to handler
);

// The ISR signature Linux expects:
irqreturn_t my_nic_handler(int irq, void *dev_id) {
    struct nic_dev *nic = dev_id;
    // top-half: read status, schedule NAPI poll
    napi_schedule(&nic->napi);
    return IRQ_HANDLED;
}
```

---

## Common ISR Pitfalls

- **Forgetting the EOI** — the interrupt line stays asserted; the CPU loops re-entering the ISR forever.
- **Using floating-point registers** — FPU state belongs to the interrupted task; corrupting it causes hard-to-reproduce bugs.
- **Holding a spinlock too long** — other CPUs spinning on that lock waste cycles during your ISR.
- **Calling printk/printf at high frequency** — serial output is slow; use ring buffers instead.

---

## Worked Example

A keyboard ISR on an embedded system:

```c
__attribute__((interrupt))
void kbd_isr(struct interrupt_frame *f) {
    uint8_t scancode = inb(0x60);   // read scancode from I/O port
    ring_buf_push(&kbd_queue, scancode);  // queue for userspace
    outb(0x20, 0x20);               // EOI to PIC
}
```

The ISR reads one byte, queues it, and exits. The actual key-mapping and echo happen in a separate kernel thread that drains `kbd_queue`.

> **Interview answer:** An ISR is the handler the CPU calls when an interrupt fires. It must save CPU state, acknowledge the hardware, do minimal work, restore state, and return via `iret`. ISRs must not sleep, must not use blocking locks, and should delegate heavy work to a bottom-half mechanism like a workqueue.
