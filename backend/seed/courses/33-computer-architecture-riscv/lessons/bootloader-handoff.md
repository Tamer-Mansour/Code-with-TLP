# Bootloader to Kernel Handoff

The handoff from the bootloader (or firmware) to the OS kernel is one of the most protocol-sensitive moments in the boot sequence. Both sides must agree on the machine state at the moment of the jump — privilege level, register values, and which hardware information has been communicated. Getting any of these wrong produces a kernel panic before the first line of OS code runs.

## The SBI Handoff Contract

When OpenSBI (or U-Boot/GRUB acting as SBI wrapper) transfers control to the Linux kernel, the RISC-V Linux boot protocol defines these requirements:

| Register | Value at kernel entry |
|----------|-----------------------|
| `a0` | hart ID (which hardware thread is jumping) |
| `a1` | physical address of the Flattened Device Tree (FDT) |
| all others | undefined / don't care |

The kernel immediately reads `a0` and `a1` in its entry asm before touching anything else. If `a1` is wrong, the kernel cannot discover memory, clocks, or devices — a guaranteed hang.

## Privilege Level at Entry

The kernel must enter at **S-mode** (Supervisor mode). OpenSBI performs the privilege drop by:

1. Writing the kernel entry address into `mepc` (Machine Exception Program Counter).
2. Writing `MPP=01` (S-mode) into `mstatus.MPP`.
3. Executing `mret` — this atomically switches to S-mode and jumps to `mepc`.

```asm
# OpenSBI kernel hand-off (simplified)
la   t0, kernel_entry_addr
csrw mepc, t0

li   t1, MSTATUS_MPP_S     # MPP field = 01 (Supervisor)
csrs mstatus, t1

# Load hart ID and FDT pointer per Linux boot protocol
mv   a0, s0                # hart ID (saved earlier)
mv   a1, s1                # FDT physical address (saved earlier)

mret                       # jump to kernel in S-mode
```

## U-Boot as Second-Stage Bootloader

In many production systems, OpenSBI hands off to **U-Boot** (in S-mode), which then:

- Parses environment variables from flash/MMC.
- Downloads a kernel image over TFTP or reads it from a file system.
- Optionally modifies the device tree (adds bootargs, sets MAC addresses).
- Hands off to the kernel using the same `a0`/`a1` protocol.

The chain looks like:

```
OpenSBI (M-mode) → U-Boot (S-mode) → Linux kernel (S-mode)
```

U-Boot may also bring its own SPL (Secondary Program Loader) before OpenSBI, making the full chain:

```
ZSBL → FSBL/SPL → OpenSBI → U-Boot proper → Linux
```

## Kernel Entry Code

The Linux RISC-V kernel entry point (`arch/riscv/kernel/head.S`) begins:

```asm
_start:
    /* a0 = hartid, a1 = dtb pointer */
    /* Mask all interrupts */
    csrw sie, zero

    /* Set up a temporary stack in the kernel image */
    la sp, init_thread_union + THREAD_SIZE

    /* Save hartid and DTB pointer */
    mv s0, a0
    mv s1, a1

    /* Initialize page tables and enable paging */
    call setup_vm
    ...
```

Notice the very first instruction disables all S-mode interrupts. The kernel is not ready to handle any interrupt until it sets up the IDT-equivalent (`stvec`).

## What Must Be True Before the Jump

The firmware is responsible for ensuring:

- **MMU is off.** The kernel starts with paging disabled and enables it itself.
- **Caches are coherent.** If the FSBL wrote the kernel image to DRAM with the cache on, it must flush/invalidate before jumping so the CPU fetches the correct bytes.
- **FDT is in accessible memory.** The FDT must not overlap with the kernel image or the kernel's expected BSS region.
- **Only one hart enters.** All secondary harts should be parked in a WFI (wait-for-interrupt) loop until the primary hart releases them via SBI HSM.

## Common Pitfalls

- **Passing a stale FDT address.** If the FDT was in SRAM and SRAM is reclaimed, the kernel reads garbage.
- **Entering in the wrong privilege mode.** Entering M-mode causes an immediate illegal-instruction trap when the kernel tries to access S-mode CSRs.
- **Cache coherency.** Writing the kernel image with dcache enabled then jumping to it without a fence causes the I-cache to fetch stale data.

> **Interview answer:** The bootloader jumps to the kernel entry in S-mode with `a0` = hart ID and `a1` = FDT physical address; the MMU must be off, caches coherent, and all secondary harts parked before the jump.
