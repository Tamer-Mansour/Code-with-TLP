# Quiz: Embedded Systems Foundations

Test your understanding of the core concepts covered in this module. Each question has exactly one correct answer.

---

**Q1. What is the primary reason a pointer to a hardware register must be declared `volatile` in C?**

- [ ] To allocate the variable in SRAM instead of a register file
- [ ] To prevent the linker from removing the symbol during garbage collection
- [x] To prevent the compiler from caching the value or optimising away the read/write
- [ ] To enable 16-bit instead of 32-bit bus access to the peripheral

*The compiler is allowed to assume a non-volatile memory location does not change between accesses. For a hardware register that can be altered by the peripheral at any time, that assumption is wrong — `volatile` tells the compiler to always emit a real load or store instruction.*

---

**Q2. A bare-metal super-loop design is being replaced with an RTOS. Which situation is the strongest justification for this migration?**

- [ ] The firmware needs to set a GPIO pin within 100 ns of an interrupt
- [ ] The total firmware size exceeds 32 KB of flash
- [x] Three independent subsystems each need to block waiting for different I/O events simultaneously
- [ ] The MCU runs at 8 MHz and the team wants higher throughput

*An RTOS shines when multiple activities need to block independently. A super-loop cannot block in one path without stalling everything else. Tight ISR latency (option A) is often better served by bare-metal. Flash size and clock speed are not directly addressed by adding an RTOS.*

---

**Q3. In a Cortex-M linker script, the `.data` section is specified as `> SRAM AT > FLASH`. What does this mean?**

- [ ] The section is placed entirely in flash and never copied to SRAM
- [ ] The section is placed entirely in SRAM with no flash copy
- [x] The section's runtime address (VMA) is in SRAM, but it is stored (LMA) in flash and must be copied by startup code
- [ ] The section is duplicated in both SRAM and flash automatically by the linker

*VMA (Virtual Memory Address) is where the CPU expects the data at runtime — SRAM. LMA (Load Memory Address) is where it physically resides in the image — flash. Startup code reads the LMA copy from flash and writes it to the VMA in SRAM before `main()` is called.*

---

**Q4. Which of the following is a hard real-time system?**

- [ ] A video streaming server that occasionally drops a frame
- [ ] A web browser that renders a page within 200 ms most of the time
- [x] An automotive airbag controller that must fire within 15 ms of a crash signal
- [ ] A background data synchronisation service that runs when the device is idle

*Hard real-time means missing a deadline is a system failure. An airbag that fires 20 ms late instead of 15 ms may not protect the occupant — that is a safety-critical failure. The other options describe soft real-time or best-effort systems where occasional latency is acceptable.*

---

**Q5. A microcontroller and a microprocessor both perform computation. What is the defining advantage of a microcontroller for battery-powered sensor applications?**

- [ ] A microcontroller runs at a higher clock frequency
- [ ] A microcontroller supports more complex operating systems
- [x] A microcontroller integrates CPU, flash, SRAM, and peripherals on one die, reducing power and BOM cost
- [ ] A microcontroller always has a hardware floating-point unit

*Integration is the key advantage. On a coin-cell battery, pulling in external RAM, oscillator chips, and I/O expanders would consume more current and PCB area. The MCU's on-chip peripherals and deep-sleep modes allow µA-range average currents.*

---

**Q6. What is the primary purpose of a virtual prototype in an embedded development programme?**

- [ ] To replace RTL simulation for verifying gate-level timing
- [ ] To generate production-ready firmware automatically from hardware specifications
- [x] To provide an executable model of the hardware that lets firmware development begin before silicon is available
- [ ] To eliminate the need for hardware bring-up and system testing

*A virtual prototype is a fast, functional software model of the SoC — not an RTL simulator or a code generator. Its value is enabling parallel hardware and firmware development and supporting CI-based regression testing. It does not replace physical validation.*
