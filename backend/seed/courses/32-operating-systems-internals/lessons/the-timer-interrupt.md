# The Timer Interrupt and the System Tick

If there is one interrupt that every operating system depends on more than any other, it is the **timer interrupt**. It is the heartbeat of the kernel — the periodic signal that allows the OS to regain control of the CPU, track time, and enforce scheduling policies.

## The Hardware Timer

A programmable timer chip (on x86: the **PIT** — Programmable Interval Timer — or the **HPET** — High Precision Event Timer, or the per-CPU **LAPIC timer**) is loaded with a countdown value. When the counter reaches zero, it fires an interrupt and reloads automatically. This repeating signal is called the **system tick**.

```
Timer chip loaded with N (e.g., 10 ms worth of cycles)
  → Counter decrements each clock cycle
  → Counter reaches 0 → interrupt fires
  → Counter reloads → cycle repeats
```

## The Tick Rate (HZ)

The Linux kernel is compiled with a constant `HZ` that defines ticks per second.

| HZ value | Tick period | Typical use |
|---|---|---|
| 100 | 10 ms | Embedded / low-power |
| 250 | 4 ms | Desktop (older Linux) |
| 1000 | 1 ms | Desktops and servers (common) |

```c
// kernel/time.h (conceptual)
#define HZ  1000          // 1000 ticks per second → 1 ms tick
#define TICK_NSEC (1000000000UL / HZ)  // nanoseconds per tick
```

A higher `HZ` gives finer-grained scheduling and timers but increases interrupt overhead. At 1000 Hz the timer ISR fires 1000 times per second — on 4 cores that is 4000 ISR entries per second just for the clock.

## What the Timer ISR Does

Each tick, the timer ISR (called `tick_handle_periodic` in Linux) performs a fixed list of housekeeping tasks:

1. **Update `jiffies`** — the kernel's running tick counter (a `u64` on 64-bit systems).
2. **Update wall-clock time** — increment `xtime` or the timekeeper structure.
3. **Call `update_process_times()`** — charge the current process for the CPU time used this tick, decrement its time-slice counter.
4. **Run expired timers** — fire callbacks for `hrtimer` or `timer_list` entries whose deadline has passed.
5. **Trigger the scheduler** — set `need_resched` flag if the current process's time slice has expired.
6. **Run per-CPU accounting** — update load averages, CPU usage stats.

```c
// Conceptual timer ISR body (Linux simplified)
void tick_handle_periodic(struct clock_event_device *dev)
{
    jiffies++;
    update_wall_time();
    update_process_times(user_mode(get_irq_regs()));
    run_local_timers();
    scheduler_tick();   // may set TIF_NEED_RESCHED
}
```

## jiffies: The Kernel's Tick Counter

`jiffies` is a global variable incremented once per tick. Code throughout the kernel uses it for coarse-grained time measurement:

```c
unsigned long timeout = jiffies + msecs_to_jiffies(500); // 500 ms from now
// ...
if (time_after(jiffies, timeout)) {
    /* 500 ms have elapsed */
}
```

The resolution of `jiffies` is one tick (1 ms at HZ=1000). For sub-millisecond precision, the kernel uses `ktime_get()` which reads the hardware clock directly.

## Tickless Kernels (NO_HZ)

Modern Linux supports **tickless** (or "dynamic tick") mode. When a CPU is idle or a single process is running with no pending timers, the tick is suppressed entirely — saving power by allowing the CPU to enter deep sleep states.

```
CONFIG_NO_HZ_IDLE   — suppress ticks on idle CPUs
CONFIG_NO_HZ_FULL   — suppress ticks on CPUs running a single task
                       (used in real-time and HPC workloads)
```

The trade-off: accounting for elapsed time on return from a long tickless sleep requires reconstructing missed jiffies, adding a small burst of work on wakeup.

## Common Pitfall: Timer Resolution vs. Timer Precision

Software timers (e.g., `sleep(1)`) wake up on the next tick boundary — not exactly after 1 second. If `HZ=100`, a 100 ms sleep might wait anywhere from 100 ms to 200 ms. High-resolution timers (`hrtimer`) bypass this by programming the hardware timer for the exact wakeup time.

## Interview Answer

> **Q: What is the timer interrupt and what does it do?**
>
> "The timer interrupt is a periodic hardware interrupt fired by a programmable timer chip (e.g., LAPIC timer on x86) at a fixed rate (HZ ticks per second). Each tick, the kernel updates `jiffies`, charges the current process for CPU time, fires expired timers, and sets a flag to trigger rescheduling if the time slice has expired — making it the fundamental mechanism behind preemptive multitasking and timekeeping."
