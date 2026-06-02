# Polling vs Interrupt-Driven I/O

When a CPU needs data from a device — a network card, disk, keyboard — it has two fundamental strategies: keep asking until the data is ready, or do other work and let the device signal when it is done. These two approaches are **polling** and **interrupt-driven I/O**, and the tradeoff between them shapes everything from device driver design to kernel latency.

## Polling: Busy Waiting

In polling (also called **busy-waiting** or **programmed I/O**), the CPU spins in a loop, repeatedly reading a status register until the device sets a "ready" bit.

```c
// Simplified polling loop
while ((inb(STATUS_PORT) & READY_BIT) == 0) {
    /* spin */
}
data = inb(DATA_PORT);
```

The CPU is fully occupied during the wait. Nothing else runs on that core. For slow devices (hard drives, USB), this wastes enormous amounts of CPU cycles. For very fast devices completing in nanoseconds, the overhead of setting up an interrupt can actually cost *more* than just spinning.

## Interrupt-Driven I/O: Let the Device Knock

In the interrupt model the CPU initiates an I/O request, then continues executing other work. When the device finishes, it asserts an interrupt line. The CPU:

1. Finishes its current instruction.
2. Saves registers (the interrupted context).
3. Jumps to the **Interrupt Service Routine (ISR)** registered for that interrupt vector.
4. The ISR reads the data and signals a waiting process.
5. The CPU restores context and resumes the interrupted work (or schedules a different process).

```c
// Interrupt Service Routine (simplified Linux-style)
irqreturn_t my_device_isr(int irq, void *dev_id)
{
    u8 data = read_data_register();
    wake_up(&device_wait_queue);   // wake the blocked process
    return IRQ_HANDLED;
}
```

The key gain: the CPU is free between the I/O request and the ISR. Other processes run, latency hides behind useful work.

## Side-by-Side Comparison

| Property | Polling | Interrupt-Driven |
|---|---|---|
| CPU utilization (slow device) | Wasted (spin) | Free for other work |
| CPU utilization (fast device) | Efficient | ISR overhead dominates |
| Latency | Immediate response | ISR dispatch adds ~1–5 µs |
| Complexity | Simple | Requires ISR + synchronization |
| Predictability | Very predictable | Interrupt timing is non-deterministic |
| Power consumption | High (core never idles) | Low (core can sleep) |

## Common Pitfall: Forgetting to Disable Interrupts in Shared Data

An ISR can fire at any time. If an ISR and normal kernel code share a data structure without proper locking, you get a race condition — even on a single CPU.

```c
// WRONG: ISR can modify 'count' between read and write
count++;

// CORRECT on single-CPU: disable interrupts around critical section
unsigned long flags;
local_irq_save(flags);
count++;
local_irq_restore(flags);
```

## Worked Example: Keyboard Input

A keyboard controller generates an interrupt on every keypress. The ISR reads the scan code from the data port and queues it. The user-space process sleeping on `/dev/input/event0` is woken. Total CPU time spent in the ISR: a few microseconds. Without interrupts, the kernel would need to poll the keyboard port thousands of times per second even when no keys are pressed.

## Interview Answer

> **Q: What is the difference between polling and interrupt-driven I/O?**
>
> "Polling spins the CPU checking a status register until the device is ready — simple but wasteful for slow devices. Interrupt-driven I/O lets the CPU do other work and respond only when the device signals completion via a hardware interrupt, which is efficient for slow or infrequent events but adds ISR dispatch overhead."
