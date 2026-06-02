# Kernel Handoff and Early Initialization

The moment the bootloader jumps to the kernel entry point, the kernel has no OS beneath it — it must bootstrap every subsystem from scratch using only the raw hardware and the information the bootloader passed. This phase is called **early initialization** and it is among the most delicate code in any OS.

## What the Bootloader Passes to the Kernel

Before jumping to the kernel, the bootloader fills a **boot parameters** structure. For Linux on x86-64, this is `struct boot_params` (defined in `arch/x86/include/uapi/asm/bootparam.h`):

```c
struct boot_params {
    struct screen_info   screen_info;   // display resolution
    uint8_t              apm_bios_info[20];
    uint64_t             tboot_addr;
    struct setup_header  hdr;           // kernel setup header
    struct e820_entry    e820_table[E820_MAX_ENTRIES];  // memory map
    // ... more fields
};
```

Key fields:
- **e820 memory map** — describes which physical address ranges are usable RAM, reserved for BIOS/ACPI, or memory-mapped I/O
- **initrd address and size** — where the bootloader placed the initial RAM disk
- **kernel command line pointer** — `root=/dev/sda2 ro quiet`
- **EFI system table pointer** (UEFI path)

**Interview answer:** At kernel handoff, the bootloader provides a memory map, the initramfs location, the kernel command line, and (on UEFI) a pointer to the EFI system table; the kernel uses these to bootstrap without relying on firmware.

## The Linux x86-64 Boot Entry Points

The compressed kernel (`vmlinuz`) contains a 16-bit setup stub followed by the compressed payload:

```
vmlinuz on disk:
┌──────────────────────────────────────────┐
│ 16-bit setup code (arch/x86/boot/header.S)│  ← BIOS bootloaders jump here
│ 32-bit decompressor (arch/x86/boot/compressed/)│
│ Compressed bzImage payload               │
└──────────────────────────────────────────┘
```

Modern bootloaders (GRUB 2, systemd-boot) use the **64-bit entry point** (`startup_64` in `arch/x86/boot/compressed/head_64.S`) and skip the 16-bit setup entirely. The decompressor:

1. Verifies the magic number in the kernel header (`0x53726448` = "HdrS")
2. Sets up a minimal stack and page tables
3. Calls `decompress_kernel()` — inflates the payload to its final load address
4. Jumps to `startup_64` in the decompressed kernel

## start_kernel(): The C Entry Point

After decompression and initial page table setup, execution reaches `start_kernel()` in `init/main.c`. This function initializes every kernel subsystem in strict order:

```c
// Simplified ordering (actual Linux source is more detailed)
asmlinkage __visible void __init __no_sanitize_address start_kernel(void)
{
    set_task_stack_end_magic(&init_task);  // set up initial thread
    smp_setup_processor_id();
    boot_cpu_init();
    setup_arch(&command_line);            // arch-specific: parse e820, init paging
    setup_log_buf(0);
    sort_main_extable();
    trap_init();                          // set up IDT: exceptions + syscall gate
    mm_init();                            // memory allocator (buddy, slab)
    sched_init();                         // scheduler data structures
    rcu_init();
    init_IRQ();                           // interrupt controller (APIC/GIC)
    tick_init();                          // timer subsystem
    timekeeping_init();
    time_init();
    printk_late_init();
    calibrate_delay();                    // BogoMIPS calculation
    console_init();                       // early console (serial/VGA)
    acpi_early_init();
    rest_init();                          // spawn init thread, enter idle loop
}
```

`rest_init()` spawns two kernel threads:
- **PID 1 (`kernel_init`)** — will eventually `exec` `/sbin/init`
- **PID 2 (`kthreadd`)** — the kernel thread manager; all other kernel threads are its children

The original `start_kernel` context (the boot CPU's init stack) becomes the **idle thread (PID 0)** and loops forever calling `cpu_idle()`.

## Memory Layout After Early Init

```
Physical memory (x86-64, simplified):
0x0000_0000 - 0x0000_0FFF  : IVT + BDA (legacy; identity-mapped)
0x0000_1000 - 0x0009_FFFF  : Low memory (used for DMA buffers)
0x0010_0000 - 0x00FF_FFFF  : 16 MB zone (ISA DMA legacy)
0x0100_0000 - ...           : Main RAM
  ↳ kernel text/data/bss
  ↳ initramfs
  ↳ page allocator buddy lists

Virtual memory (x86-64 kernel):
0xFFFF_8000_0000_0000 +     : Direct physical map (all RAM accessible here)
0xFFFF_FFFF_8000_0000 +     : Kernel text/data (loaded here by the linker)
```

## The initramfs Handoff

Once `start_kernel()` completes subsystem setup, `kernel_init` mounts the initramfs:

```c
// kernel/init/main.c (simplified)
static int __ref kernel_init(void *unused)
{
    kernel_init_freeable();   // more subsystem init (driver probing, etc.)

    // Try to exec /init from initramfs
    if (!try_to_run_init_process("/init"))
        return 0;

    // Fallback: try /sbin/init, /etc/init, /bin/init, /bin/sh
    panic("No working init found.");
}
```

The `/init` process inside the initramfs is now **PID 1** in user space. From this point, the kernel is a passive service provider — it responds to system calls but does not drive boot.

## Worked Example: Tracing Early Dmesg

```bash
# Read kernel ring buffer from current boot
$ dmesg | head -40

# Key lines to look for:
# [    0.000000] Linux version 6.8.0-31-generic ...
# [    0.000000] Command line: root=/dev/sda2 ro quiet splash
# [    0.000000] BIOS-provided physical RAM map:
# [    0.000000] BIOS-e820: [0x0000000000000000-0x000000000009fbff] usable
# [    0.045231] Booting paravirtualized kernel on bare hardware
# [    0.198713] PCI: Using configuration type 1 for base access
# [    0.312445] clocksource: tsc-early: mask 0xffffffffffffffff
# [    1.234567] Run /init as init process
```

The timestamps show microseconds since boot. Anything before `[    0.01]` is during memory setup with disabled clocks and uses `[    0.000000]` as a placeholder.

## Common Pitfalls

- Confusing the **kernel's PID 1** (`kernel_init` thread) with **user-space PID 1** (`/sbin/init`) — PID 1 is reused.
- Forgetting that `start_kernel` must not call any function that requires subsystems not yet initialized — the ordering of init calls is a strict invariant.
- Assuming all drivers are available immediately — most drivers probe asynchronously after `start_kernel` returns, through the bus subsystem and module loading.
