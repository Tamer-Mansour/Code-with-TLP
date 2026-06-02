# Microcontroller vs Microprocessor: Key Differences

The terms are often used interchangeably in casual conversation, but they describe fundamentally different silicon architectures. Choosing the right one is the first hardware decision on any embedded project.

## The Core Distinction

A **microprocessor (MPU)** is a CPU core on a chip. It needs external components — RAM, ROM, oscillators, I/O controllers — to form a working system.

A **microcontroller (MCU)** is a *system on a chip*. The CPU core, flash memory, SRAM, timers, UART, SPI, I2C, ADC, and GPIO are all integrated on the same die. Power it up, and it boots immediately.

```
Microprocessor system
┌───────┐  bus  ┌──────┐  ┌────────┐  ┌───────┐
│  MPU  │──────▶│ RAM  │  │  ROM   │  │  I/O  │
└───────┘       └──────┘  └────────┘  └───────┘

Microcontroller (everything on one die)
┌─────────────────────────────────────┐
│  CPU │ Flash │ SRAM │ Timers │ GPIO │
└─────────────────────────────────────┘
```

## Side-by-Side Comparison

| Dimension | Microcontroller (MCU) | Microprocessor (MPU) |
|---|---|---|
| Integration | All-in-one | CPU only |
| External RAM | Not usually needed | Required |
| Typical clock | 8 MHz – 480 MHz | 500 MHz – 3+ GHz |
| Typical RAM | 2 KB – 2 MB on-chip | 256 MB – 32 GB external DDR |
| OS support | Bare-metal / RTOS | Linux, Android, RTOS |
| Power draw | µA – tens of mA | Hundreds of mA – watts |
| Cost (unit) | $0.50 – $10 | $5 – $200+ |
| Examples | STM32, AVR, PIC, RP2040 | Raspberry Pi BCM, i.MX8, AM335x |

## Where Each Shines

**Choose an MCU when:**
- You need to control hardware directly (GPIO, PWM, ADC).
- Power budget is tight (wearables, IoT sensors, battery devices).
- Deterministic real-time response is required (motor control, safety systems).
- BOM cost matters at scale.

**Choose an MPU when:**
- You need a rich OS (Linux, Android) for networking, filesystems, or UI.
- The application demands significant computational throughput (video decoding, ML inference).
- You need virtual memory and process isolation.

## The Fuzzy Middle: Application Processors and SoCs

Modern System-on-Chips (SoCs) blur the line. An NXP i.MX RT "crossover" MCU runs at 1 GHz with megabytes of on-chip RAM but still has the peripheral set and determinism of a classic MCU. Conversely, application processors like the STM32MP1 combine a Cortex-A MPU core with a Cortex-M MCU core on the same die, letting you run Linux on one core and hard real-time code on the other.

## Worked Example: Selecting a Part

Suppose you are building a wireless temperature logger that wakes every 30 seconds, reads a sensor over I2C, and transmits data over BLE. Requirements:

- Average current: < 10 µA
- No display, no filesystem
- Simple periodic task, no Linux needed

**Decision:** MCU (e.g., Nordic nRF52840). It has built-in BLE, I2C, and deep-sleep modes in the single-digit µA range. An MPU running Linux would draw hundreds of mA just at idle — a non-starter on a coin cell.

## Common Pitfalls

- **Assuming more MHz = better.** A 480 MHz MCU that wakes from sleep in 1 µs may outperform a 1.5 GHz MPU that takes 2 seconds to boot Linux for a simple sensing task.
- **Forgetting boot time.** MCUs start executing code within microseconds; MPUs running Linux may take seconds.
- **Ignoring peripheral integration.** Adding an external ADC, timers, and UART chips to a bare MPU often costs more in board space and BOM than switching to an MCU.

> **Interview answer:** A microcontroller integrates CPU, memory, and peripherals on a single chip for low-power, real-time control tasks; a microprocessor is just the CPU core and requires external memory and peripherals, offering higher performance for OS-level workloads.
