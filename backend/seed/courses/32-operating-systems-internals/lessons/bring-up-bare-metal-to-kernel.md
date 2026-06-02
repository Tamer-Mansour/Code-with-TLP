# Bring-Up: From Bare Metal to a Booting Kernel

OS bring-up is the sequence of steps that takes a processor from reset (executing from ROM) to running the first user-space process. Every step must succeed in order — a single misconfigured register or wrong memory map can silently prevent the kernel from ever printing its first log line.

## The Boot Sequence at a Glance

```
Power-On Reset
     │
     ▼
ROM / BootROM (on-chip)
  - Initialize clocks, DDR controller
  - Load second-stage bootloader from flash/eMMC
     │
     ▼
SPL / U-Boot SPL (Secondary Program Loader)
  - Train DRAM
  - Load full bootloader
     │
     ▼
U-Boot (or EDK II / coreboot)
  - Configure peripherals
  - Load kernel image + DTB + initrd into DRAM
  - Set up boot arguments
     │
     ▼
Kernel Entry (Linux: arch/riscv/kernel/head.S)
  - Set up early stack
  - Enable virtual memory (satp / TTBR0)
  - Call start_kernel()
     │
     ▼
start_kernel() → init process (PID 1)
```

## Stage 1: Reset Vector and BootROM

On RISC-V, after reset the hart begins executing at the **reset vector** (typically `0x00001000` in many QEMU/virtual prototype configurations, or a vendor-defined address). The BootROM is the root of trust: it is read-only, already initialized, and its job is to set up just enough to load the next stage.

```asm
# RISC-V reset vector (simplified)
_start:
    csrr  a0, mhartid          # which hart am I?
    la    sp, _stack_top       # set up stack
    la    a1, _dtb_addr        # Device Tree Blob pointer
    call  spl_main             # jump to C code
```

RISC-V passes two arguments to the next stage by convention: `a0 = hart ID`, `a1 = DTB base address`. Every stage in the boot chain must preserve and forward these.

## Stage 2: DRAM Initialization

DRAM is not usable until the memory controller is configured and the PHY is trained. This is the longest and most hardware-specific step. On a virtual prototype, DRAM is usually modeled as a pre-initialized flat memory array, so this step is skipped — but you must still ensure the DTB describes the DRAM base address and size correctly.

## Stage 3: Bootloader — U-Boot

U-Boot loads the kernel, sets up the boot command line, and jumps to the kernel entry point. On RISC-V Linux, U-Boot calls the kernel with:

```c
// U-Boot kernel handoff (simplified)
typedef void (*kernel_entry_t)(ulong hartid, ulong dtb_pa);
kernel_entry_t kernel = (kernel_entry_t) kernel_load_addr;
kernel(gd->arch.boot_hart, (ulong)fdt_addr);
```

The kernel image format is typically a compressed **Image** (raw binary) or **FIT image** (Flattened Image Tree with metadata).

## Stage 4: Kernel Initialization

`head.S` runs before any C code:

1. Clear BSS.
2. Set up the initial stack.
3. Set `satp` to enable paging (Sv39 on 64-bit RISC-V, Sv32 on 32-bit).
4. Relocate to the virtual address space.
5. Call `start_kernel()`.

`start_kernel()` then:

- Parses the DTB (`setup_arch`).
- Initializes memory (`mm_init`).
- Starts the scheduler (`sched_init`).
- Brings up secondary CPUs (`smp_init`).
- Runs initcalls (driver probe, filesystems).
- Launches PID 1 (`/sbin/init` or initramfs `/init`).

> **Interview answer:** Boot bring-up proceeds BootROM → SPL → bootloader → kernel entry → start_kernel; each stage hands off hart ID, DTB pointer, and a known CPU/memory state to the next; the kernel enables the MMU, initializes subsystems, and finally runs PID 1.

## Debugging a Hang on a Virtual Prototype

| Symptom | Likely cause |
|---|---|
| No output at all | UART not modeled or wrong MMIO base |
| "DRAM init failed" | Memory map in DTB does not match prototype |
| Kernel boots, then hangs | Timer interrupt not delivered (CLINT/PLIC misconfigured) |
| Page fault at early boot | Kernel linked at wrong virtual address |
| SMP hangs after BSP | Secondary hart IPI not modeled |

## Common Pitfalls

- **Wrong DTB** — using a DTB that does not match the virtual prototype's memory map causes the kernel to access non-existent peripherals.
- **Mismatched entry address** — if U-Boot loads the kernel to one address but the image is linked at another, the very first instruction page-faults.
- **Stack alignment** — many calling conventions require 16-byte stack alignment; a misaligned stack in head.S causes cryptic crashes in the first C function call.
- **Cache coherency** — on real silicon, the DRAM must be flushed after the image is loaded so the CPU's instruction cache sees the correct bytes. Virtual prototypes often skip caches, masking this bug until real hardware.

Methodical bring-up — one stage at a time, with a UART print at each boundary — is the only reliable approach on both virtual prototypes and real hardware.
