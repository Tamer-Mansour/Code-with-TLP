# Polled vs Interrupt-Driven Driver Design

Every driver must answer a fundamental question: how does it know the hardware has finished an operation? Two strategies exist — *polling* (the driver asks) and *interrupt-driven* (the hardware tells). Choosing the right one shapes latency, CPU usage, and scalability.

## Polling

The driver repeatedly reads a status register until the hardware reports completion.

```c
/* Polled read — spin until data ready */
ssize_t polled_read(struct my_dev *dev, char *buf, size_t n)
{
    int timeout = 10000;

    /* Kick off the hardware operation */
    writel(CMD_START, dev->base + REG_CMD);

    /* Busy-wait for completion */
    while (!(readl(dev->base + REG_STATUS) & STATUS_DONE)) {
        if (--timeout == 0)
            return -ETIMEDOUT;
        cpu_relax();   /* hint to avoid pipeline stalls */
    }

    /* Read result */
    return hw_copy_data(dev, buf, n);
}
```

### When Polling Wins

| Scenario | Reason |
|---|---|
| Ultra-low-latency operations | Interrupt latency (microseconds) is too slow |
| Very frequent completions | ISR overhead dominates over polling cost |
| Embedded systems with a dedicated core | Blocking one core is acceptable |
| NAPI networking (receive) | Hybrid: interrupt to wake, then poll until drained |

## Interrupt-Driven Design

The driver starts an operation and then releases the CPU. The hardware raises an interrupt when done; the ISR wakes a sleeping thread.

```c
/* Start operation and sleep until ISR wakes us */
ssize_t irq_read(struct my_dev *dev, char *buf, size_t n)
{
    dev->done = false;

    /* Kick off the hardware operation */
    writel(CMD_START, dev->base + REG_CMD);

    /* Sleep until interrupt handler sets dev->done */
    if (wait_event_interruptible_timeout(dev->wq, dev->done,
                                         msecs_to_jiffies(1000)) <= 0)
        return -ETIMEDOUT;

    return hw_copy_data(dev, buf, n);
}

/* ISR: called by kernel when hardware raises IRQ */
static irqreturn_t my_isr(int irq, void *data)
{
    struct my_dev *dev = data;
    writel(IRQ_ACK, dev->base + REG_STATUS);
    dev->done = true;
    wake_up(&dev->wq);
    return IRQ_HANDLED;
}
```

### When Interrupts Win

| Scenario | Reason |
|---|---|
| Long I/O operations (disk, network) | CPU does other work while waiting |
| Many concurrent devices | One ISR per event vs N polling loops |
| Battery-constrained systems | CPU can sleep between events |
| Unpredictable completion times | No wasted cycles spinning |

## The NAPI Hybrid (Networking)

High-speed NICs use a hybrid approach called NAPI:

1. NIC raises an **interrupt** when the first packet arrives.
2. ISR **disables further interrupts** from the NIC and schedules a poll.
3. Polling loop **drains all available packets** in one pass.
4. When the queue is empty, polling stops and **interrupts are re-enabled**.

This prevents "interrupt storms" (thousands of interrupts/second per packet) while avoiding pure-poll CPU waste at idle.

```
Idle → Interrupt → Disable NIC IRQ → Poll loop
  ↑                                        |
  └── Re-enable IRQ (queue empty) ←────────┘
```

## Quantitative Comparison

| Metric | Polling | Interrupt-Driven |
|---|---|---|
| Latency | Very low (no context switch) | Higher (ISR + wakeup overhead) |
| CPU usage (busy) | 100% of one core | Near zero between events |
| CPU usage (idle) | 100% of one core | Near zero |
| Scalability | Poor (O(n) cores for n devices) | Good (one IRQ line per device) |
| Code complexity | Low | Higher (concurrency, ISR design) |

## Common Pitfalls

- **Forgetting `cpu_relax()` in tight poll loops** — on x86 this emits a `PAUSE` instruction, improving HyperThreading efficiency and reducing power.
- **Infinite polling without a timeout** — a broken device will hang the thread forever; always set a deadline.
- **Interrupt coalescing misconfiguration** — NICs can batch interrupts; setting the coalesce interval too high increases latency, too low causes interrupt storms.
- **Sleeping while polling** — if you poll in an atomic context (ISR, spinlock held), you cannot schedule; use a timeout counter, not `msleep`.

## Interview Answer

> **Q: When would you prefer polling over interrupt-driven I/O?**
>
> **Interview answer:** Polling is preferred when the expected completion time is very short (microseconds) and interrupt overhead would dominate, or when an operation completes so frequently that ISR overhead becomes the bottleneck — for example, RDMA completions or ultra-low-latency NVMe command processing.
