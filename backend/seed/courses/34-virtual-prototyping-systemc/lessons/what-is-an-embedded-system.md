# What Is an Embedded System?

An embedded system is a computer built to perform one specific function — or a narrow set of related functions — within a larger device. Unlike a general-purpose PC, an embedded system is *dedicated*: it runs the same software indefinitely, often without a keyboard, screen, or user interaction of any kind.

You interact with dozens of embedded systems every day: the anti-lock braking controller in your car, the firmware in your Wi-Fi router, the thermostat on the wall, and the microcontroller inside your wireless earbuds.

## Defining Characteristics

| Property | Typical Value / Range |
|---|---|
| Processor type | Microcontroller (MCU) or application processor |
| RAM | Kilobytes to a few megabytes |
| Storage | Flash memory (kilobytes to gigabytes) |
| OS | None (bare-metal), RTOS, or lightweight Linux |
| Power budget | Milliwatts to a few watts |
| Real-time requirement | Often hard or soft real-time |

## Three Core Properties

**1. Purpose-built.** An embedded system is designed around one task. This specialisation allows engineers to optimise every resource — CPU cycles, memory, and power — for that task alone.

**2. Resource-constrained.** Memory is measured in kilobytes, not gigabytes. Clock speeds may be in the low megahertz. Code must be lean, predictable, and sometimes hand-optimised.

**3. Reactive.** Most embedded systems spend their lives waiting for an external stimulus — a sensor reading, a button press, a network packet — and then responding within a defined time window. Missing a deadline can mean a crashed drone, a corrupted transaction, or a failed airbag deployment.

## A Minimal Example

The simplest embedded program blinks an LED. Here is what that looks like at the register level in C (for a generic ARM Cortex-M MCU):

```c
#include <stdint.h>

// Memory-mapped GPIO base address (vendor-specific)
#define GPIO_BASE   0x48000000UL
#define GPIO_ODR    (*(volatile uint32_t *)(GPIO_BASE + 0x14))
#define LED_PIN     (1u << 5)

void delay(volatile uint32_t count) {
    while (count--) { /* burn cycles */ }
}

int main(void) {
    // Assume clock and GPIO already enabled by startup code
    while (1) {
        GPIO_ODR |=  LED_PIN;   // LED on
        delay(500000);
        GPIO_ODR &= ~LED_PIN;   // LED off
        delay(500000);
    }
}
```

No operating system. No standard library. Just your code, a clock, and hardware registers.

## Why Constraints Shape Everything

Because embedded systems cannot be upgraded with more RAM or a faster chip on a whim, software quality decisions made early in the project have long-lasting consequences. A buffer overflow in desktop software might crash a process; in an embedded medical device it might harm a patient.

This is exactly why **virtual prototypes** — software models of the hardware — are so valuable: they let you test firmware before the silicon exists, and they let you run thousands of edge-case scenarios that would be impossible or dangerous on real hardware.

## Common Pitfalls

- **Treating embedded C like desktop C.** Stack overflow is silent and catastrophic when there is no OS to catch it.
- **Ignoring startup code.** The `main()` function does not run first; a small assembly stub sets up the stack, zero-fills BSS, and copies initialised data from flash to RAM.
- **Assuming blocking is free.** A tight polling loop that burns CPU cycles may starve a critical ISR.

> **Interview answer:** An embedded system is a purpose-built computer integrated into a larger device to perform a dedicated function under strict resource and timing constraints, typically running bare-metal or RTOS firmware close to hardware.
