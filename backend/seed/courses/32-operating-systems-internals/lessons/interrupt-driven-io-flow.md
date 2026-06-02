# The Interrupt-Driven I/O Flow

Understanding the exact sequence of events in interrupt-driven I/O — from the moment a process calls `read()` to the moment it receives data — is essential for reasoning about OS latency, race conditions, and driver correctness.

## Step 1: The System Call

A user-space process calls `read()`. The kernel checks whether data is available. If not, it blocks the process (changes its state to `TASK_INTERRUPTIBLE` or `TASK_UNINTERRUPTIBLE`) and places it on a **wait queue** associated with the device.

```c
// Kernel side of a blocking read (simplified)
ssize_t device_read(struct file *f, char __user *buf, size_t count, loff_t *pos)
{
    wait_event_interruptible(dev->wait_queue, dev->data_ready);
    copy_to_user(buf, dev->buffer, count);
    dev->data_ready = 0;
    return count;
}
```

The scheduler now runs another process. The original process is off the CPU entirely.

## Step 2: Device Initiates the Transfer

The driver previously programmed the device: it wrote a command to the device's command register (or set up a **DMA descriptor**). The device now performs the physical I/O — spinning disk heads, receiving bytes over a wire, or executing a flash read — without any CPU involvement.

For DMA transfers, the device writes data directly into a kernel buffer in RAM. The CPU does not participate in the data movement itself.

## Step 3: The Device Asserts an Interrupt

When the operation completes, the device asserts its interrupt line. The interrupt controller (e.g., x86's APIC):

1. Receives the signal.
2. Checks whether the interrupt priority exceeds the CPU's current priority.
3. If so, signals the CPU via a dedicated pin or message (MSI on PCIe).

## Step 4: CPU Saves Context and Vectors to the ISR

The CPU:

1. Completes its current instruction.
2. Automatically pushes `SS`, `RSP`, `RFLAGS`, `CS`, `RIP` onto the kernel stack (x86-64 hardware saves these on interrupt entry).
3. Looks up the handler address in the **Interrupt Descriptor Table (IDT)** using the interrupt vector number.
4. Jumps to the ISR.

```asm
; Hardware pushes: SS, RSP, RFLAGS, CS, RIP (automatically)
; ISR prologue then saves general-purpose registers
push rax
push rbx
; ... etc.
call actual_isr_handler
pop rbx
pop rax
iretq          ; restores RIP, CS, RFLAGS, RSP, SS
```

## Step 5: ISR Executes (Top Half)

The ISR runs with interrupts disabled (or at a raised priority level). It must be fast:

- Acknowledge the interrupt to the device (clear the interrupt flag in a device register).
- Copy data out of the device buffer or note that DMA is complete.
- Enqueue work for the bottom half (softirq, tasklet, or workqueue).
- Wake up the process waiting on the device's wait queue.

```c
irqreturn_t eth_isr(int irq, void *dev_id)
{
    struct eth_dev *dev = dev_id;
    u32 status = readl(dev->base + STATUS_REG);
    writel(status, dev->base + STATUS_REG);   // acknowledge

    if (status & RX_COMPLETE) {
        napi_schedule(&dev->napi);  // defer heavy work to softirq
    }
    return IRQ_HANDLED;
}
```

## Step 6: Scheduler Runs — Process Wakes Up

`wake_up()` marks the sleeping process as `TASK_RUNNING` and places it on a run queue. The scheduler may preempt the currently running process immediately (if the woken process has higher priority) or wait for the next scheduling point.

## Step 7: Process Resumes in User Space

The process's `read()` system call returns with the data. From the process's perspective, it simply blocked for some time and woke up with the result.

## Full Flow Diagram (Text)

```
Process calls read()
  → Kernel blocks process, arms device
  → [Device performs I/O — CPU runs other work]
  → Device fires interrupt
  → CPU saves context, jumps to ISR
  → ISR acknowledges, enqueues data, wakes process
  → Scheduler puts process on run queue
  → Process resumes, read() returns data
```

## Common Pitfalls

- **Missing interrupt acknowledgment:** If the ISR does not clear the device's interrupt flag, the interrupt re-fires immediately upon `iretq`, creating an infinite loop that freezes the system.
- **Sleeping in an ISR:** Wait queues and mutexes can sleep. Sleeping inside an ISR is illegal because ISRs run with a stack that does not support blocking.
- **Shared buffer without locking:** The woken process and a subsequent ISR can race on the device buffer. Always use proper synchronization.

## Interview Answer

> **Q: Walk me through what happens when a disk read completes in an interrupt-driven system.**
>
> "The process blocks on a wait queue after issuing the read. The disk controller performs the transfer (possibly via DMA) and fires an interrupt. The CPU saves its current context, runs the ISR which acknowledges the device and wakes the waiting process, then the scheduler resumes the process and the `read()` system call returns with the data."
