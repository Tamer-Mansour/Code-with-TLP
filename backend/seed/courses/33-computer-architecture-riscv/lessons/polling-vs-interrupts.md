# Polling vs Interrupt-Driven I/O

Once you can read and write device registers, the next question is *when* to do so. Two fundamental strategies exist: polling (the CPU asks "are you done yet?" repeatedly) and interrupt-driven I/O (the device taps the CPU on the shoulder when it needs attention).

## Polling (Programmed I/O)

The CPU spins in a tight loop, reading a status register until the device signals readiness:

```c
// Polling a UART transmitter — wait until TX FIFO is not full
#define UART_LSR_THRE  0x20  // Transmit Holding Register Empty

void uart_putc_poll(volatile uint8_t *lsr, volatile uint8_t *thr, char c) {
    while (!(*lsr & UART_LSR_THRE))
        ;           // busy-wait
    *thr = c;
}
```

### When Polling Wins

- **Latency is paramount and the wait is very short** — A spin loop has no context-switch overhead. If the device is almost always ready, polling avoids the overhead of setting up an interrupt.
- **Bare-metal embedded systems** — Simple microcontroller code with no OS, no other tasks. The CPU has nothing else to do.
- **Real-time systems with tight deadlines** — Interrupt latency jitter is eliminated.

### When Polling Loses

- **Long or unpredictable waits** — If a disk access takes 10 ms and the CPU runs at 3 GHz, polling wastes 30 million cycles doing nothing.
- **Multiple devices** — Polling three devices sequentially means each device waits longer than necessary.
- **Energy efficiency** — A polling loop prevents the CPU from entering a low-power idle state.

## Interrupt-Driven I/O

The CPU programs the device to raise an interrupt signal when it is ready. The CPU then resumes other work and only handles the device when interrupted:

```
Timeline:
CPU:     [compute] [compute] [compute] <IRQ> [handler] [compute] ...
Device:  [busy...............] [raises IRQ]   [ready]
```

The interrupt request (IRQ) causes the CPU to:
1. Finish the current instruction.
2. Save the program counter and CPU state (push to stack or registers).
3. Look up the interrupt vector in the Interrupt Vector Table (IVT) or PLIC.
4. Jump to the Interrupt Service Routine (ISR).
5. Execute the ISR (read/write device, acknowledge interrupt).
6. Restore saved state and resume interrupted code.

### RISC-V Interrupt Handling

RISC-V uses the PLIC (Platform-Level Interrupt Controller) for external interrupts:

```c
// Minimal RISC-V trap handler (written in C with machine-mode CSRs)
void __attribute__((interrupt("machine"))) machine_trap_handler(void) {
    uint32_t cause = read_csr(mcause);

    if (cause & (1u << 31)) {
        // It's an interrupt (MSB = 1), not an exception
        uint32_t irq_id = plic_claim();   // get pending interrupt ID
        switch (irq_id) {
            case UART0_IRQ:
                uart_irq_handler();
                break;
            // ... other devices
        }
        plic_complete(irq_id);            // acknowledge
    }
}
```

### ISR Design Rules

Keep ISRs short. The ISR should:
1. **Acknowledge** the interrupt (clear the pending bit) so the device stops asserting the line.
2. **Copy data** out of the device register into a software buffer.
3. **Set a flag** or post to a semaphore so the main loop can process the data.

What an ISR should *not* do:
- Call blocking functions (`sleep`, `malloc`, `printf` with locks).
- Perform lengthy computations.
- Enable interrupts recursively (unless the architecture safely supports nesting).

```c
// Example: UART RX ISR — short and non-blocking
#define RX_BUFFER_SIZE 256
static volatile char rx_buf[RX_BUFFER_SIZE];
static volatile int  rx_head = 0, rx_tail = 0;

void uart_rx_isr(void) {
    char c = UART0->rxdata & 0xFF;          // read byte (clears FIFO entry)
    int next = (rx_head + 1) % RX_BUFFER_SIZE;
    if (next != rx_tail) {                  // drop if buffer full
        rx_buf[rx_head] = c;
        rx_head = next;
    }
    // acknowledge via PLIC: done outside this function
}
```

## Comparison Table

| Criterion | Polling | Interrupt-Driven |
|---|---|---|
| CPU utilization | High (busy-wait) | Low (CPU free between events) |
| Latency | Minimal (no context switch) | Higher (ISR entry overhead ~10–100 ns) |
| Code complexity | Low | Medium–High (ISR, shared state, synchronization) |
| Energy efficiency | Poor | Good (CPU can sleep) |
| Suitable for | Very fast devices, bare metal, real-time | Slow or unpredictable devices, RTOS |
| Multiple devices | Poor (sequential poll) | Good (each device has its own IRQ) |

## Hybrid: Interrupt Coalescing

High-throughput network cards use a hybrid: an interrupt fires after N packets *or* after T microseconds, whichever comes first. The driver then polls the ring buffer to drain all ready packets in a batch. This is the basis of Linux's **NAPI** (New API) network architecture.

## Common Pitfalls

- **Missing interrupt acknowledgment** — If the ISR does not clear the interrupt pending bit, the CPU re-enters the ISR immediately after returning, creating an infinite loop.
- **Shared state without synchronization** — Variables written in an ISR and read in main code must be `volatile`; use atomic operations or disable interrupts briefly around multi-word updates.
- **Priority inversion** — A low-priority ISR blocking a high-priority task; use nested interrupts and priority levels carefully.

> **Interview answer:** Polling burns CPU cycles checking a status register in a loop — it is simple and has zero interrupt-overhead latency but wastes time when the device is slow. Interrupt-driven I/O lets the CPU do other work and respond only when the device raises a hardware signal; it is more efficient for slow or bursty devices but adds ISR complexity and a small latency overhead.
