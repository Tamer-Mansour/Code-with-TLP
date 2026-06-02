# Pre-Silicon Software Development

Pre-silicon software development is the practice of writing, integrating, and validating embedded software — bootloaders, firmware, device drivers, BSPs, and application layers — before the physical chip or board is available. It is the primary reason the semiconductor industry adopted virtual prototypes.

## Why It Matters

Historically, the software team could not start real work until engineering validation test (EVT) boards arrived. That might be 12–18 months into a chip program. If the software took another 12 months to stabilize, the total development window was 2–3 years — and software was always the critical path.

Pre-silicon development collapses this timeline by giving software engineers a functional target from day one of chip design.

## The Software Stack That Needs to Run Pre-Silicon

| Layer | Examples |
|---|---|
| Bootloader | U-Boot, custom ROM code, TF-A (Trusted Firmware) |
| RTOS / OS | FreeRTOS, Zephyr, Linux kernel, Android |
| Board Support Package (BSP) | Clock init, memory controller setup, pin mux |
| Device drivers | UART, SPI, I2C, USB, Ethernet, display, camera |
| Middleware | File systems, networking stacks, codecs |
| Application | User-facing software, safety monitors |

Every layer depends on hardware behavior. Pre-silicon development means all of these can be written and tested against a VP.

## What "Ready" Means for a Pre-Silicon VP

A VP is ready for software development when it can:

1. **Boot the target processor** — the ISS models the reset vector and begins fetching instructions.
2. **Initialize memory** — RAM and ROM are mapped at the correct addresses.
3. **Service interrupts** — the interrupt controller model routes IRQs correctly.
4. **Handle peripheral register I/O** — at minimum: UART (for printf debugging), timer (for delays), and the memory controller.

```cpp
// Minimal platform VP: CPU ISS + ROM + RAM + UART
int sc_main(int argc, char* argv[]) {
    arm_iss   cpu("cpu");
    rom_model rom("rom");
    ram_model ram("ram");
    uart_model uart("uart");

    // Connect via TLM sockets
    cpu.isa_socket(rom.target);
    cpu.data_socket(ram.target);
    cpu.data_socket(uart.target); // memory-mapped at 0x4000_0000

    sc_start(); // run simulation
    return 0;
}
```

## Practical Workflow

```
Week 1:  Hardware architects define memory map → SW team gets address layout
Week 2:  First VP with CPU ISS + memory → bootloader printf works
Week 4:  Timer and interrupt controller models → RTOS tick available
Week 8:  Full peripheral set → all driver development begins
Week 16: Feature-complete software → ready to test on first silicon
```

## Debugging Pre-Silicon: The Advantages

On real hardware, a printf from a broken driver might produce corrupted output or hang the system with no clue why. On a VP:

- **Execution trace** — every instruction the CPU executes is logged.
- **Memory access log** — every read/write to every peripheral register is recorded.
- **Deterministic replay** — the same bug reproduces every run (no hardware race conditions from power-up variability).

```bash
# Enable trace in a QEMU-based VP
qemu-system-arm -d cpu,exec,int -kernel firmware.elf 2>trace.log
```

## Software-Hardware Co-Validation

Pre-silicon is also a two-way street. Software running on the VP validates the hardware spec:

- If a register offset is wrong in the VP model, the driver will fail — catching a hardware spec bug before it is committed to RTL.
- If an interrupt routing is ambiguous in the datasheet, the software engineer clarifies it with the hardware team before RTL is finalized.

This feedback loop — software testing hardware specs via the VP — is called **co-validation** and is one of the most valuable aspects of pre-silicon development.

## Interview Answer

> "Pre-silicon software development means writing and validating firmware and drivers against a virtual prototype before the chip is fabricated. It eliminates the historical dependency between software start date and hardware availability, compressing time-to-market by months."

## Common Pitfalls

- **Starting the VP too late.** If the VP is not available until RTL is complete, most of the schedule benefit is lost.
- **Ignoring interrupt behavior early.** RTOS ports depend heavily on timer and interrupt controller accuracy; these models must be prioritized.
- **Trusting a broken VP.** If the VP model has bugs, software engineers write firmware against incorrect behavior — creating hardware-dependent bugs that only appear on real silicon.
- **Skipping VP–hardware correlation.** When first silicon arrives, always run the same test suite on both VP and hardware and diff the results to quantify VP accuracy.
