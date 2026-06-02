# Multi-Hart Boot and Hart 0 Coordination

RISC-V systems can have multiple **harts** (hardware threads) — the RISC-V term for a CPU core or hardware thread. In a multi-hart system, all harts typically begin executing from the same reset vector simultaneously at power-on. This creates an immediate problem: if all harts try to initialize shared hardware at the same time, the results are undefined.

## The Hart 0 Primary Pattern

The universal convention is to elect **one hart** (almost always hart 0) as the primary hart, which performs all single-threaded initialization. All other harts park themselves and wait.

```asm
_start:
    csrr a0, mhartid          # read this hart's hardware ID

    # If we are NOT hart 0, park immediately
    bnez a0, hart_park

    # Hart 0 only: do all initialization
    la   sp, _stack_top
    call firmware_main         # never returns

hart_park:
    # Secondary harts wait in WFI loop
    # They will be released by OpenSBI HSM or SMP bringup
1:  wfi
    j 1b
```

## Why WFI (Wait For Interrupt)?

`wfi` (Wait For Interrupt) is a hint instruction that pauses the hart until an interrupt or inter-processor interrupt (IPI) arrives. Secondary harts use it instead of a busy-wait spin loop because:

- It reduces power consumption significantly on battery-powered devices.
- It reduces bus traffic and cache pressure, allowing hart 0 to initialize faster.
- It is a standard idiom that firmware and OS code both understand.

## OpenSBI Hart State Machine (HSM)

OpenSBI provides the **Hart State Management (HSM)** SBI extension, which gives the kernel a clean interface for starting secondary harts:

| HSM State | Meaning |
|-----------|---------|
| STARTED | Hart is running |
| STOPPED | Hart is powered off (or WFI-parked) |
| START_PENDING | Requested to start, not yet running |
| STOP_PENDING | Requested to stop |
| SUSPENDED | Hart in a low-power sleep state |

The kernel starts a secondary hart with:

```c
// SBI call: sbi_hart_start(hartid, start_addr, opaque)
struct sbiret ret = sbi_ecall(
    SBI_EXT_HSM,          /* extension */
    SBI_EXT_HSM_HART_START,
    target_hartid,
    (unsigned long)secondary_start_addr,
    (unsigned long)hartid_to_cpu(target_hartid),
    0, 0, 0
);
```

OpenSBI wakes the parked hart, loads `a0` = hartid and `a1` = opaque value, and jumps to `secondary_start_addr` in S-mode.

## Linux SMP Bringup

Linux's secondary hart startup sequence (`arch/riscv/kernel/smpboot.c`) looks like:

```
Hart 0 (primary):              Hart N (secondary):
  sbi_hart_start(N, ...)  →    [woken by OpenSBI]
                               __secondary_start()
                               set_up_per_cpu_areas()
                               notify_cpu_starting()
                               cpu_startup_entry()  ← idle loop
```

The secondary hart only runs when there is work scheduled on it. Until then it runs the idle loop which drops back into `wfi`.

## Shared Resources During Init

The primary hart must initialize all shared resources before releasing secondary harts:

- **Interrupt controller (PLIC):** Configure priority and threshold for each hart context.
- **Coherent memory:** Flush caches and execute a memory fence (`fence`) so secondary harts see the page tables written by hart 0.
- **Kernel data structures:** All per-CPU areas must be allocated and mapped before a secondary hart tries to access its own.

```asm
# Hart 0, just before releasing secondaries
fence rw, rw         # ensure all writes are visible to other harts
sfence.vma           # ensure page table writes are visible
```

## The Rendezvous Pattern

Some firmware designs use a **rendezvous barrier** where all harts except the primary wait at an atomic flag:

```c
// Secondary harts spin on this
volatile int boot_barrier = 0;

// Primary hart, after initialization:
__atomic_store_n(&boot_barrier, 1, __ATOMIC_RELEASE);
```

Secondary harts:

```c
while (!__atomic_load_n(&boot_barrier, __ATOMIC_ACQUIRE))
    asm volatile("wfi");
// Now proceed with per-hart initialization
```

The `ACQUIRE`/`RELEASE` semantics ensure memory ordering across harts.

## Common Pitfalls

- **All harts initializing UART simultaneously.** This produces garbled output and may corrupt the UART FIFO.
- **Secondary harts accessing BSS before it's cleared.** Hart 0 must clear BSS before releasing secondary harts.
- **Forgetting per-hart CSR initialization.** Each hart has its own `mtvec`, `sscratch`, and FPU state — secondary harts must set these up themselves after wakeup.
- **Deadlock in rendezvous.** If hart 0 itself takes an exception during init and never writes the barrier flag, all other harts spin forever.

> **Interview answer:** In a multi-hart RISC-V system, secondary harts park themselves in a WFI loop after reset while hart 0 performs all shared initialization; the OS later wakes secondary harts via the SBI HSM extension one at a time.
