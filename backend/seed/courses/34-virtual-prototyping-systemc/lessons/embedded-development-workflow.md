# The Embedded Development Workflow End to End

Embedded software development follows a structured lifecycle that differs significantly from web or desktop software. Every phase touches hardware, timing constraints, and safety considerations that simply do not exist in application software.

## The Full Workflow

```
1. Requirements
      │
      ▼
2. Architecture & HW Selection
      │
      ▼
3. Virtual Prototype / Simulation Model
      │
      ▼
4. Firmware Development (BSP → Drivers → Application)
      │
      ▼
5. Unit & Integration Testing (on VP and hardware)
      │
      ▼
6. Hardware Bring-Up
      │
      ▼
7. System Testing & Validation
      │
      ▼
8. Qualification / Certification (if safety-critical)
      │
      ▼
9. Production Programming & Release
      │
      ▼
10. Field Updates (OTA/DFU) & Maintenance
```

## Phase 1–2: Requirements and Architecture

Before a line of code is written, engineers define:

- **Functional requirements:** What the system does (measure, control, communicate).
- **Non-functional requirements:** Timing budgets, power targets, memory limits, temperature range, safety integrity level (SIL/ASIL).
- **Hardware selection:** MCU family, peripherals needed, memory sizing, power domain design.

Poor requirements are the root cause of most project overruns. Underspecifying timing budgets, for example, leads to redesigns when integration reveals the firmware cannot meet the deadline.

## Phase 3–4: Virtual Prototype and Firmware Development

With a VP available, firmware development proceeds in layers:

| Layer | What It Contains |
|---|---|
| **Startup / BSP** | Vector table, clock init, linker script, startup.s |
| **HAL (Hardware Abstraction Layer)** | Thin wrappers around MMIO register access |
| **Drivers** | GPIO, UART, SPI, I2C, ADC — protocol logic on top of HAL |
| **Middleware** | FreeRTOS, USB stack, TCP/IP stack, filesystem |
| **Application** | Business logic, state machines, algorithms |

Starting at the BSP keeps each layer testable in isolation. A driver can be validated on the VP before the physical board arrives.

## Phase 5: Testing Strategies

Embedded testing is multi-level:

**Unit tests on host (native):**
Abstract hardware behind interfaces; test application logic compiled as native x86 code using a framework like Unity or Catch2. Fast and CI-friendly.

```c
// Example: test a CRC function without any hardware
void test_crc32_known_value(void) {
    uint8_t data[] = {0x01, 0x02, 0x03};
    uint32_t result = crc32(data, sizeof(data));
    TEST_ASSERT_EQUAL_HEX32(0x55BC801D, result);
}
```

**Integration tests on VP:**
Run the full firmware binary on the virtual prototype. Inject stimuli (UART messages, GPIO pulses) and verify outputs. Deterministic and scriptable.

**Hardware-in-the-loop (HIL) tests:**
Run the firmware on the real MCU. Inject inputs from a test harness (e.g., a Raspberry Pi generating I2C traffic). Catch issues that only appear on real silicon (electrical noise, clock jitter, DMA races).

## Phase 6: Hardware Bring-Up

When first silicon arrives, the first task is verifying the hardware itself:

1. Power-on test: measure all voltage rails.
2. Clock bring-up: verify oscillators with an oscilloscope.
3. JTAG/SWD connectivity: confirm the debug probe connects.
4. Minimal firmware: blink an LED to confirm the CPU executes code.
5. Peripheral tests: exercise each peripheral one at a time.

Common bring-up pitfalls:
- Clock not configured before peripheral init (peripheral runs on wrong clock → wrong baud rate).
- Pull-up/pull-down resistors missing on I2C SCL/SDA (bus stuck low).
- Incorrect linker script for the actual flash size (overflow not detected at link time).

## Phase 7–8: System Validation and Certification

System testing validates end-to-end behaviour against requirements. For safety-critical products (medical, automotive, aerospace), a formal certification process applies:

- **IEC 62443** — industrial cybersecurity
- **IEC 61508 / ISO 26262 (ASIL)** — functional safety
- **DO-178C** — aviation software
- **IEC 62304** — medical device software

These standards require traceability from requirement to code to test, static analysis, coverage metrics, and formal reviews.

## Phase 9–10: Production and Maintenance

Production programming flashes the verified firmware binary to each unit using a production programmer (e.g., Segger Flasher, Dediprog, or a custom fixture). A golden test sequence validates the programmed unit.

Post-shipment, field updates via OTA/DFU let you push bug fixes and new features without physical access. A robust OTA design includes:

- Signed firmware images (prevents loading malicious code).
- A/B (dual-bank) flash layout (prevents bricking on failed update).
- Rollback logic if the new image fails its self-test.

## Common Pitfalls

- **Skipping the VP phase.** Firms that skip VPs consistently spend the first 3 months of hardware availability just on bring-up and bug fixes that could have been found earlier.
- **Late integration.** Developing BSP, drivers, and application in isolation, then trying to integrate them on hardware for the first time, produces avalanche failures.
- **No version control for hardware artefacts.** Linker scripts, startup files, and memory maps must be in source control with the firmware — a mismatch between them and the silicon revision causes silent failures.

> **Interview answer:** Embedded development flows from requirements through architecture, virtual-prototype-based firmware development, multi-level testing, hardware bring-up, and system validation — with each layer building on the previous to catch bugs as early and cheaply as possible.
