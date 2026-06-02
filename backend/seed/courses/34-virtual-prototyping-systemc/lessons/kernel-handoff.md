# Handoff to the Linux Kernel

The handoff from bootloader to Linux kernel is a precisely defined ABI. If any part of this contract is violated — wrong CPU state, wrong register values, missing hardware initialization — the kernel will crash or hang, often with no useful error message. Understanding this handoff is essential for VP bring-up.

## The ARM64 Kernel Entry ABI

For a 64-bit ARM (AArch64) kernel, the Linux boot protocol requires the following CPU state at entry:

| Requirement | Detail |
|---|---|
| Exception level | EL1 (or EL2 if kernel uses VHE) |
| MMU | Disabled |
| D-cache | Disabled or clean/invalidated |
| I-cache | Disabled or clean/invalidated |
| Interrupts (DAIF) | All masked (D=1, A=1, I=1, F=1) |
| x0 | Physical address of the DTB |
| x1, x2, x3 | Zeroed (reserved) |
| PC | Kernel entry address (base of `Image`) |

**Interview answer:** On ARM64, the bootloader must jump to the kernel entry point at EL1 or EL2 with MMU and caches disabled, x0 holding the DTB physical address, and x1–x3 zeroed.

## How U-Boot Performs the Handoff

U-Boot's `booti` command orchestrates the handoff:

```
U-Boot> booti 0x40000000 - 0x4FA00000
```

- `0x40000000` — kernel Image load address
- `-` — no initrd (use `-` or omit)
- `0x4FA00000` — DTB address

Internally, U-Boot:
1. Validates the kernel Image header magic (`ARM64_IMAGE_MAGIC = 0x644D5241`)
2. Disables the MMU and caches
3. Sets `x0 = 0x4FA00000` (DTB address)
4. Zeroes `x1`, `x2`, `x3`
5. Branches to `0x40000000`

## The Linux Image Header

The ARM64 kernel `Image` file begins with a 64-byte header. The VP can validate this before simulation to catch loading errors:

```cpp
struct Arm64ImageHeader {
    uint32_t code0;          // Executable code (branch instruction)
    uint32_t code1;          // Executable code
    uint64_t text_offset;    // Image load offset from start of RAM
    uint64_t image_size;     // Effective image size
    uint64_t flags;          // Kernel flags
    uint64_t res2, res3, res4;
    uint32_t magic;          // 0x644D5241 = "ARM\x64"
    uint32_t res5;
};

void Platform::validate_kernel(const std::string& path) {
    Arm64ImageHeader hdr;
    std::ifstream f(path, std::ios::binary);
    f.read(reinterpret_cast<char*>(&hdr), sizeof(hdr));
    if (hdr.magic != 0x644D5241) {
        SC_REPORT_FATAL("Platform", "Invalid kernel Image magic");
    }
}
```

## What the Kernel Does First

On entry, the Linux kernel:

1. Saves the DTB pointer from `x0`
2. Sets up a minimal stack
3. Initializes the MMU using an identity map
4. Calls `start_kernel()` in C
5. Parses the DTB to discover devices
6. Mounts the initrd root filesystem
7. Spawns `init` (PID 1)

From a VP perspective, the key observation is that the kernel immediately starts reading from the DTB address. If the DTB is at the wrong address or is corrupt, the kernel crashes at `early_init_dt_scan()` with no console output (the console driver has not been initialized yet).

## Modeling the EL Transition

If the VP starts the CPU in EL3 (as ARM Trusted Firmware does), the firmware must transition through EL3 → EL2 → EL1 before jumping to the kernel. The VP's CPU ISS must correctly model `ERET` and the `ELR_ELn`/`SPSR_ELn` registers:

```cpp
void CpuModel::execute_eret() {
    // Pop exception level
    uint64_t target_pc   = read_sysreg(ELR_EL3);
    uint64_t target_pstate = read_sysreg(SPSR_EL3);
    m_current_el = (target_pstate >> 2) & 0x3; // EL field
    m_pc = target_pc;
    write_pstate(target_pstate);
}
```

## Common Pitfalls

- **Kernel entered at wrong exception level**: If U-Boot jumps to the kernel at EL3, the kernel's EL1 setup code runs at the wrong level, corrupting system registers and causing an early fault.
- **DTB address not in x0**: Some custom bootloaders forget to set `x0`. The kernel reads a DTB from address `0x0`, which may be the Boot ROM — the kernel then misparses it and panics with `No valid DTB found`.
- **Cache not cleaned before handoff**: If the D-cache is enabled and not cleaned, the kernel's cache invalidation sequence may expose stale data, causing memory corruption.
- **text_offset ignored**: The kernel's `text_offset` field specifies how far from the DRAM base the Image should be loaded. Loading at DRAM base `0x4000_0000` is only correct if `text_offset` is zero (which it often is for modern kernels with `CONFIG_ARM64_KERNELPIE=n`).
