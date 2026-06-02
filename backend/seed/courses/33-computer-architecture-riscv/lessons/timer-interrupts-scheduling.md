# Timer Interrupts and Preemptive Scheduling

Without timer interrupts, a CPU-bound process could run forever and starve all others. Preemptive scheduling solves this by forcing periodic control transfers back to the kernel — even when the running process never calls the OS voluntarily.

## The Hardware Timer on RISC-V

RISC-V specifies two memory-mapped registers for machine-mode timer support:

| Register | Description |
|----------|-------------|
| `mtime`  | Free-running 64-bit counter, increments at a platform-defined frequency |
| `mtimecmp` | Comparison register — a timer interrupt fires when `mtime >= mtimecmp` |

Both registers live in the CLINT (Core Local INTerruptor), a memory-mapped peripheral at a well-known physical address (e.g., `0x0200_0000` on many RISC-V boards).

To arm a timer interrupt 10 ms in the future (assuming a 10 MHz `mtime` clock):

```c
#define CLINT_MTIME     0x0200BFF8UL
#define CLINT_MTIMECMP  0x0200_4000UL
#define TIMER_INTERVAL  100000  // 10 ms at 10 MHz

volatile uint64_t *mtime    = (uint64_t *)CLINT_MTIME;
volatile uint64_t *mtimecmp = (uint64_t *)CLINT_MTIMECMP;

void set_timer(void) {
    *mtimecmp = *mtime + TIMER_INTERVAL;
}
```

## Delivering the Timer Interrupt to S-Mode

The timer interrupt originates in M-mode (`mcause` bit 63 set, code = 7). Most RISC-V OSes run in S-mode, so the M-mode firmware (OpenSBI) must **delegate** or **forward** the interrupt upward.

The standard approach (used by xv6-riscv):

1. M-mode trap handler fires on timer interrupt.
2. Re-arms `mtimecmp` for the next interval.
3. Sets the supervisor software interrupt pending bit (`sip.SSIP = 1`) to inject a fake S-mode interrupt.
4. Returns with `mret`.

The kernel's S-mode handler then sees `scause = 0x8000_0000_0000_0001` (supervisor software interrupt) and knows a timer tick occurred.

## The Scheduler Tick Path

```
mtime >= mtimecmp
  → M-mode timer trap
    → re-arm mtimecmp
    → sip.SSIP = 1
      → S-mode interrupt fires in kernel
        → usertrap() / kerneltrap()
          → yield() if process has run long enough
            → sched() → swtch() → scheduler loop
```

## Enabling Timer Interrupts in the Kernel

```c
// Enable supervisor timer interrupt (bit 5 in sie)
w_sie(r_sie() | SIE_STIE);

// Or for supervisor software interrupt (bit 1, used with xv6 timer scheme)
w_sie(r_sie() | SIE_SSIE);

// Enable global supervisor interrupt delivery
intr_on();   // sets SIE bit in sstatus
```

If interrupts are disabled (e.g., the kernel holds a spinlock), the timer interrupt is held pending and delivered as soon as `SIE` is restored — preemption inside critical sections is prevented automatically.

## Quantum and Preemption

The OS configures the timer interval to define the **scheduling quantum** (time slice). A typical quantum is 1–10 ms. When the timer fires:

- If the current thread is in user space, `usertrap()` calls `yield()`.
- If the current thread is in kernel space (e.g., inside a syscall), many kernels defer the yield until the syscall exits — a **non-preemptive kernel** design. Linux and modern kernels are **preemptible** even inside kernel code.

## Common Pitfalls

- Not re-arming `mtimecmp` before returning from the M-mode handler — the interrupt fires again immediately.
- Enabling `SIE` in `sstatus` before installing a valid `stvec` — the first timer interrupt crashes the kernel.
- Confusing `mtime`/`mtimecmp` (M-mode, hardware) with the OS's software notion of "jiffies" or "ticks".
- Forgetting that `mtimecmp` is per-hart — on a multicore system, each hart has its own `mtimecmp` at `CLINT_MTIMECMP + 8 * hartid`.

> **Interview answer:** RISC-V timer interrupts use `mtime` and `mtimecmp` in the CLINT; when `mtime >= mtimecmp` the hardware fires an M-mode interrupt, which firmware re-arms and forwards as an S-mode software interrupt; the kernel's timer handler calls `yield()` on the current process to invoke the scheduler, implementing preemptive multitasking.
