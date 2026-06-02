# Boot Flow in a Virtual Platform

A virtual platform (VP) must faithfully replicate the sequence of events that occur from the moment power is applied until the operating system is running. Understanding this sequence — commonly called the **boot flow** — is essential for both platform validation and software bring-up.

## Why Boot Flow Matters in a VP

In real silicon, the boot sequence is fixed by hardware. In a VP, every step is a model decision: which components exist, how they respond to reset, and what addresses are valid at each stage. Getting this wrong means software running on the VP diverges from behavior on real hardware, defeating the purpose of early software validation.

**Interview answer:** A VP boot flow is a cycle-approximate or transaction-accurate simulation of the hardware reset-to-OS sequence, allowing software teams to validate firmware and bootloaders before silicon is available.

## The Major Stages

| Stage | Component | Responsibility |
|---|---|---|
| 1 | CPU reset | Set PC to reset vector, clear registers |
| 2 | Boot ROM | First trusted code; minimal hardware init |
| 3 | SPL / Stage-1 loader | Initialize DRAM, load next stage |
| 4 | Bootloader (U-Boot) | Peripheral init, load kernel + DTB |
| 5 | Kernel handoff | Jump to kernel entry point |
| 6 | Linux init | Device discovery via device tree |

## Modeling the Reset State

When the VP's `sc_main` calls `sc_start()`, every module that implements `end_of_elaboration()` or `start_of_simulation()` initializes itself. The CPU model must present a defined architectural state:

```cpp
void ArmCortexA55::start_of_simulation() {
    // ARMv8 reset state: EL3, AArch64
    m_pc   = RESET_VECTOR;   // e.g. 0x0000_0000 or platform-specific
    m_cpsr = PSTATE_D | PSTATE_A | PSTATE_I | PSTATE_F; // all interrupts masked
    m_sp   = 0;              // undefined until firmware sets it
}
```

## Address Map at Reset

A key difference between boot and runtime is the **address map**. Many SoCs remap memory at boot:

- The reset vector points into Boot ROM (e.g., `0x0000_0000` maps to ROM, not DRAM)
- After early init, the SoC remaps so DRAM is visible at `0x8000_0000`

In a VP, this is modeled with a **router** or **memory map controller** that swaps target bindings:

```cpp
// Before remap: address 0x0 → boot_rom
router.bind(0x0000_0000, 0x0000_FFFF, boot_rom_socket);

// After software writes REMAP register:
void on_remap_write() {
    router.rebind(0x0000_0000, 0x0000_FFFF, dram_socket);
}
```

## Simulation vs. Real Hardware Speed

VP boot can run faster or slower than real hardware depending on model abstraction:

- **Instruction-accurate ISS**: near-real-time, slow for CI
- **Approximately timed TLM**: 10–100x faster, typical for bring-up
- **Loosely timed / functional**: can boot Linux in seconds, limited timing accuracy

For software bring-up, loosely timed models are most common; they get software running quickly and allow debugging before cycle-accurate models are needed.

## Common Pitfalls

- **Wrong reset vector**: CPU starts fetching from an unmapped address → bus error. Always verify the reset vector matches your target SoC specification.
- **Missing clock/reset modeling**: Some bootloaders poll a clock-ready bit before proceeding. If the VP's clock model never asserts `clk_ready`, the bootloader loops forever.
- **Peripheral register defaults**: Bootloaders read hardware straps and fuse values at reset. The VP must return the correct default values or software takes the wrong code path.
- **Endianness mismatch**: ARM can boot in big- or little-endian. Ensure the ISS and memory models agree on endianness from the first fetch.

## Key Takeaway

The VP boot flow is not just a software concern — it is a contract between the hardware model and the firmware team. Every default register value, every reset signal, and every address-map transition must be specified and implemented before software bring-up can succeed.
