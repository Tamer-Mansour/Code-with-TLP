# The Role of the CPU Scheduler and the Dispatcher

Modern operating systems run many more processes than there are CPU cores. The CPU scheduler decides which ready process gets to use a core next. Without a scheduler, processes would either monopolize the CPU or starve indefinitely.

## What the Scheduler Does

The **CPU scheduler** (also called the short-term scheduler) selects one process from the **ready queue** and hands it to a CPU core. This decision happens in microseconds and may occur thousands of times per second. The scheduler itself is just a policy — it answers the question "who runs next?"

The scheduler operates on processes in the **READY** state. It does not touch processes that are waiting for I/O (BLOCKED state) or processes that have not yet been admitted (NEW state).

## The Dispatcher

Once the scheduler picks a process, the **dispatcher** does the mechanical work of handing the CPU to it. Dispatcher responsibilities include:

- **Context switch** — saving the CPU state (registers, program counter, stack pointer) of the outgoing process into its PCB and loading the saved state of the incoming process.
- **Switching to user mode** — transitioning from kernel privilege level back to user space via a privileged return instruction.
- **Jumping to the correct instruction** — restoring the program counter so the incoming process resumes exactly where it left off.

```
Scheduler picks → Dispatcher acts
     (policy)          (mechanism)
```

## Scheduler vs. Dispatcher — Key Distinction

| Component  | Role            | Runs in       | Frequency          |
|------------|-----------------|---------------|--------------------|
| Scheduler  | Chooses next process | Kernel  | On every scheduling event |
| Dispatcher | Executes the switch  | Kernel  | Once per context switch |

The scheduler is pure decision-making logic. The dispatcher is the execution engine that carries out the decision. They are always paired but are conceptually separate.

## Where the Ready Queue Lives

The ready queue is a data structure (often a linked list or priority queue) maintained in kernel memory. Each entry points to a **Process Control Block (PCB)** — the kernel's record for one process. When a process becomes runnable (after being created, after an I/O completes, or after a time slice is preempted), its PCB moves into the ready queue.

```c
// Simplified PCB fields relevant to scheduling
struct pcb {
    int   pid;
    int   priority;
    enum  state { READY, RUNNING, BLOCKED } state;
    struct cpu_context saved_regs;  // registers saved on context switch
    int   burst_estimate;           // used by some schedulers
};
```

## Why This Matters

Every millisecond the scheduler wastes on a low-priority process is a millisecond stolen from a high-priority interactive task. Poor scheduling decisions make a system feel sluggish even when the CPU is underloaded. This is why real kernels (Linux CFS, Windows scheduler) invest enormous engineering into scheduler accuracy and fairness.

## Common Pitfalls

- Confusing the **long-term scheduler** (admission control — moves jobs from disk into memory) with the **short-term scheduler** (picks the next running process). The short-term scheduler is what textbooks mean when they say "the scheduler."
- Assuming the dispatcher is free. The dispatcher's overhead — the **dispatch latency** — is real and must be minimized. Each context switch costs hundreds to thousands of CPU cycles.
- Thinking the ready queue is always FIFO. It can be a priority queue, a multi-level structure, or a red-black tree (Linux CFS), depending on the scheduling algorithm.

## Interview Answer

> "The CPU scheduler selects which ready process runs next; the dispatcher performs the actual context switch. The scheduler is policy, the dispatcher is mechanism."
