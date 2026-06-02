# Top Halves, Bottom Halves, and Deferred Work

An ISR runs with interrupts disabled (or at an elevated priority). Every microsecond spent in the ISR is a microsecond where other interrupts cannot be delivered, latency accumulates, and the system feels less responsive. The solution is to split interrupt handling into two phases: a fast **top half** and a deferred **bottom half**.

## The Core Principle

The top half (the ISR itself) does the absolute minimum:

- Acknowledge the hardware interrupt.
- Read time-sensitive data from the device (data that would be lost if not captured immediately).
- Schedule the bottom half to run later.

The bottom half does the heavy lifting:

- Parse received network packets.
- Update file system structures.
- Copy data into user-space buffers.
- Anything that can tolerate a brief delay.

## Mechanisms in Linux

Linux provides three mechanisms for deferred work, each with different scheduling guarantees:

### 1. Softirqs

Softirqs (software interrupts) are statically defined, run in interrupt context (no sleeping allowed), and can run on multiple CPUs simultaneously. They run with interrupts enabled, so they do not block other ISRs.

```c
// Softirq types (defined in <linux/interrupt.h>)
enum {
    HI_SOFTIRQ = 0,       // tasklets (high priority)
    TIMER_SOFTIRQ,        // timer callbacks
    NET_TX_SOFTIRQ,       // network transmit
    NET_RX_SOFTIRQ,       // network receive
    BLOCK_SOFTIRQ,        // block I/O completion
    TASKLET_SOFTIRQ,      // tasklets (normal priority)
    SCHED_SOFTIRQ,        // scheduler
    RCU_SOFTIRQ,          // Read-Copy-Update
};
```

The network subsystem is the most important user: the NIC ISR fires `NET_RX_SOFTIRQ`, and the softirq handler processes received packets, runs through the protocol stack, and wakes waiting sockets.

### 2. Tasklets

Tasklets are built on top of softirqs and are dynamically allocated. A given tasklet runs on only one CPU at a time (serialized), making them simpler to write than softirqs. They also run in interrupt context — no sleeping.

```c
// Declare and schedule a tasklet
void my_tasklet_fn(struct tasklet_struct *t)
{
    struct my_dev *dev = from_tasklet(dev, t, tasklet);
    process_received_data(dev);
}

DECLARE_TASKLET(my_tasklet, my_tasklet_fn);

// In the ISR (top half):
tasklet_schedule(&my_tasklet);
```

### 3. Workqueues

Workqueues run in **process context** (kernel threads), which means they can sleep, hold mutexes, and call any kernel function. They are the right choice for work that might block.

```c
// Schedule work on the system workqueue
static void my_work_fn(struct work_struct *work)
{
    struct my_dev *dev = container_of(work, struct my_dev, work);
    // can sleep here, allocate memory with GFP_KERNEL, etc.
    kmalloc(4096, GFP_KERNEL);
}

INIT_WORK(&dev->work, my_work_fn);

// In the ISR (top half):
schedule_work(&dev->work);
```

## Decision Tree for Deferred Work

```
Does the work need to sleep or block?
  YES → Workqueue (process context)
  NO  → Can it run on multiple CPUs concurrently?
          YES → Softirq (complex, for high-frequency paths)
          NO  → Tasklet (simpler, serialized)
```

## Execution Context Summary

| Mechanism | Context | Can Sleep? | Parallelism | Overhead |
|---|---|---|---|---|
| Top half (ISR) | Interrupt | No | Per-IRQ | Minimal |
| Softirq | Interrupt | No | Per-CPU | Low |
| Tasklet | Interrupt | No | Serialized | Low |
| Workqueue | Process | Yes | Thread pool | Higher |

## Worked Example: Network Packet Reception

```
1. NIC fires interrupt (packet received)
2. Top half (eth_isr):
     - Acknowledge NIC interrupt
     - Note which DMA buffer has the new packet
     - napi_schedule() → arms NET_RX_SOFTIRQ
3. Bottom half (net_rx_action softirq):
     - Copies packet from DMA buffer
     - Parses Ethernet/IP/TCP headers
     - Finds the matching socket
     - Appends data to socket receive buffer
     - Wakes the process blocked in recv()
```

Steps 1–2 take ~1–2 µs with interrupts disabled. Steps 3+ can take 10–50 µs but run with interrupts enabled, so new interrupts are not delayed.

## Common Pitfall: Sleeping in Softirq/Tasklet Context

Calling `kmalloc(size, GFP_KERNEL)` (which can sleep) inside a softirq will crash the kernel or deadlock. Always use `GFP_ATOMIC` for allocations in interrupt or softirq context.

```c
// In softirq/tasklet/ISR — MUST use GFP_ATOMIC
buf = kmalloc(len, GFP_ATOMIC);  // returns NULL if memory not immediately available
```

## Interview Answer

> **Q: What are top and bottom halves in interrupt handling?**
>
> "The top half is the ISR itself — it runs with interrupts disabled, does the minimum (acknowledge hardware, save urgent data), and schedules a bottom half. The bottom half (softirq, tasklet, or workqueue) does the heavy processing with interrupts re-enabled, keeping ISR latency minimal while still doing all necessary work."
