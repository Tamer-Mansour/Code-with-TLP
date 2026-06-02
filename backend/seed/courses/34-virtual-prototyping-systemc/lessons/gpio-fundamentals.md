# GPIO: Reading and Driving Pins

General-Purpose Input/Output (GPIO) is the most fundamental peripheral in any embedded system. Every microcontroller exposes at least a handful of GPIO pins, and in virtual prototyping, modeling them correctly is the starting point for almost every peripheral above them.

## What Is GPIO?

A GPIO pin is a digitally controlled electrical connection between the processor and the outside world. Each pin can be individually configured as either:

- **Input** — the processor reads the logic level driven by external hardware.
- **Output** — the processor drives a logic level (high or low) onto the pin.
- **Alternate Function** — the pin is multiplexed to a peripheral (UART TX, SPI CLK, etc.).

A typical GPIO peripheral exposes three control registers:

| Register | Purpose |
|---|---|
| `DDR` / `DIR` | Data-direction register — sets each pin as input (0) or output (1) |
| `ODR` / `DR` | Output data register — value driven onto output pins |
| `IDR` / `PIN` | Input data register — current logic level read from the pin |

## Driving a Pin (Output Mode)

To light an LED on pin 5 of port A:

```c
// Set pin 5 as output
GPIOA->DDR |= (1u << 5);

// Drive the pin HIGH
GPIOA->ODR |= (1u << 5);

// Drive the pin LOW
GPIOA->ODR &= ~(1u << 5);
```

The key pitfall here is a **read-modify-write hazard**: if two tasks modify different bits of the same register concurrently without a mutex, one may clobber the other. In real hardware this can cause flickering outputs; in virtual platforms it surfaces as non-deterministic simulation.

## Reading a Pin (Input Mode)

```c
// Set pin 3 as input
GPIOA->DDR &= ~(1u << 3);

// Read the current level
uint8_t level = (GPIOA->IDR >> 3) & 0x1;
```

**Pull-up and pull-down resistors** are critical here. A floating input — one with no external driver and no internal pull — reads unpredictably. Most GPIO peripherals include an internal pull-up enable bit:

```c
GPIOA->PUR |= (1u << 3);   // Enable pull-up on pin 3
```

## SystemC Model Sketch

In a virtual platform, GPIO is typically modeled as a `sc_module` with `sc_signal` ports representing pin state:

```cpp
SC_MODULE(GPIOPort) {
    sc_in<bool>  pin_in[8];
    sc_out<bool> pin_out[8];
    sc_in<bool>  clk;

    uint8_t ddr_reg = 0x00; // all inputs by default
    uint8_t odr_reg = 0x00;

    void drive_outputs() {
        for (int i = 0; i < 8; ++i) {
            if (ddr_reg & (1u << i))
                pin_out[i].write((odr_reg >> i) & 0x1);
        }
    }

    SC_CTOR(GPIOPort) {
        SC_METHOD(drive_outputs);
        sensitive << clk.pos();
    }
};
```

This is intentionally simplified. A production model also handles open-drain mode, glitch filtering, and interrupt generation on rising/falling edges.

## Interrupts on GPIO

Most GPIO peripherals can generate an interrupt when a pin changes state. The interrupt configuration involves:

1. Selecting the trigger type: rising edge, falling edge, or both.
2. Enabling the interrupt mask bit for that pin.
3. The ISR reads the interrupt-status register and clears it (write-1-to-clear is common).

Forgetting to clear the interrupt flag is a classic bug: the ISR re-enters immediately and the CPU spins forever.

## Common Pitfalls

- **Forgetting to set direction** before driving — the output value is latched in `ODR` but nothing appears on the pin until `DDR` marks it as output.
- **Floating inputs** causing metastability — always enable a pull resistor or add an external one.
- **Shadow register aliasing** — some MCUs have "set" and "clear" registers (`BSRR` on STM32) to allow atomic bit manipulation without read-modify-write.

> **Interview answer:** A GPIO pin is a software-controllable digital I/O line. Direction is set via a DDR register; the output value via ODR; and the current level is sampled from IDR. Key concerns are floating inputs, read-modify-write hazards, and clearing interrupt flags in the ISR.
