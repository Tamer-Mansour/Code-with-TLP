# How the Timer Interrupt Enables Preemptive Scheduling

Without the timer interrupt, a process could monopolize the CPU forever. A buggy or malicious program could spin in an infinite loop and starve every other process. The timer interrupt is what makes the OS the ultimate authority over CPU time — it ensures the kernel gets to run periodically, no matter what user-space code is doing.

## Cooperative vs. Preemptive Scheduling

In **cooperative** (non-preemptive) scheduling, a process runs until it voluntarily yields — by calling `sleep()`, `yield()`, or performing a blocking I/O operation. Early Windows (3.x) and classic Mac OS used this model. A single misbehaving program could freeze the entire system.

In **preemptive** scheduling, the OS forcibly removes a process from the CPU when its time slice expires. This requires a mechanism to periodically interrupt and check — which is exactly the timer interrupt.

## The Preemption Mechanism, Step by Step

```
1. Process P runs in user space
2. Timer fires → CPU jumps to timer ISR (with interrupts disabled)
3. ISR calls scheduler_tick()
4. scheduler_tick() decrements P's remaining time slice
5. If time slice == 0:
     set_tsk_need_resched(P)  → sets TIF_NEED_RESCHED flag
6. ISR returns (iretq)
7. Kernel checks TIF_NEED_RESCHED on the return path to user space
8. If set → calls schedule() → picks next process Q
9. Context switch: P's registers saved, Q's registers restored
10. Q runs in user space
```

The critical insight: step 7 happens **on every return to user space** — after every system call and every interrupt. The flag is the signal; the actual switch happens at a safe point.

## Kernel Preemption

Classic kernels (Linux before 2.5) were **non-preemptible in kernel mode**: a process running kernel code could not be preempted, even if `TIF_NEED_RESCHED` was set. This helped latency for long system calls (e.g., a `write()` copying gigabytes).

**CONFIG_PREEMPT** (enabled by default on most distros) allows preemption at almost any point in kernel code, as long as the code is not inside a spinlock critical section or has not explicitly called `preempt_disable()`.

```c
// preempt_disable/enable pair — prevents kernel preemption
preempt_disable();
/* critical section — will not be preempted here */
preempt_enable();   // if TIF_NEED_RESCHED is set, schedule() is called here
```

**CONFIG_PREEMPT_RT** (real-time patch) goes further: it converts most spinlocks to sleeping mutexes, making nearly all kernel code preemptible. This achieves worst-case latencies under 100 µs on modern hardware.

## Time Slice Expiry and Priority

Linux's **CFS (Completely Fair Scheduler)** does not use fixed time slices in the traditional sense. Instead, it tracks a virtual runtime (`vruntime`) per process and always runs the process with the lowest `vruntime`. The timer tick updates `vruntime` and triggers a resched check:

```c
// CFS tick (simplified)
void task_tick_fair(struct rq *rq, struct task_struct *curr, int queued)
{
    update_curr(cfs_rq);       // advance curr->vruntime by elapsed time
    check_preempt_tick(cfs_rq, curr);  // if curr ran long enough, resched
}
```

Higher-priority tasks (lower `nice` value) accumulate `vruntime` more slowly, so they get selected more often — the timer tick is what makes this accounting continuous.

## Interrupt Context vs. Process Context

The timer ISR runs in **interrupt context**: no process is current, sleeping is forbidden, and the call stack is on the interrupted process's stack. The actual context switch (`schedule()`) runs in **process context** — after the ISR returns and the kernel checks the resched flag on the return path.

```
[Interrupt context] timer ISR → sets TIF_NEED_RESCHED
       ↓
[Process context]  return-to-user path → checks flag → calls schedule()
       ↓
[Process context]  context_switch(prev, next) → next process runs
```

## Pitfall: Priority Inversion and Timer Granularity

If a high-priority process is waiting for a lock held by a low-priority process, the timer tick alone does not fix this — that requires priority inheritance. Also, timer granularity (1 ms at HZ=1000) limits how fine-grained preemption can be; with `CONFIG_HZ=100` a process might run up to 10 ms before any preemption check, unacceptable for real-time workloads.

## Interview Answer

> **Q: How does the timer interrupt enable preemptive scheduling?**
>
> "The timer ISR fires periodically, updates the running process's accounting, and sets `TIF_NEED_RESCHED` if the time slice has expired. When the ISR returns, the kernel checks this flag on the return path to user space and calls `schedule()` if set, which context-switches to the next process — ensuring no process can hold the CPU indefinitely."
