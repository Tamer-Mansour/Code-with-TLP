# What Is a Virtual Prototype?

A **virtual prototype (VP)** is a software model of a hardware system that is accurate enough to run the same unmodified software — firmware, drivers, operating systems, and applications — that will eventually execute on the real chip or board. It is not a schematic, not a CAD rendering, and not a gate-level netlist. It is an executable model that behaves like the target hardware from the perspective of the software running on it.

## The Core Idea

Think of a virtual prototype as a **flight simulator for hardware**. A flight simulator does not contain a real jet engine; it models engine behavior well enough that a pilot learns to fly without ever leaving the ground. A virtual prototype does not contain real transistors; it models processor registers, memory maps, peripheral registers, and interrupt lines well enough that a software engineer can boot an OS and debug a device driver.

The model typically runs on a standard workstation or server and is written in a high-level language — most commonly **SystemC with the TLM-2.0 standard** — or in a C/C++ instruction-set simulator (ISS).

## Key Characteristics

| Characteristic | Description |
|---|---|
| Executable | Runs software directly, including boot loaders and OSes |
| Functional | Captures input/output behavior, not electrical details |
| Timed or untimed | May include approximate timing or be purely functional |
| Composable | Built from reusable models of individual IP blocks |
| Debuggable | Exposes internal state that is invisible on real silicon |

## What a Virtual Prototype Is NOT

- It is **not an RTL simulation** — RTL (Register Transfer Level) models every clock edge and every bit; VPs abstract timing to run 100x–10,000x faster.
- It is **not an emulator** — Hardware emulators (FPGAs programmed with RTL) run at near-real-time but cost millions of dollars and require completed RTL.
- It is **not a schematic** — A schematic shows how components connect electrically; a VP models what those components do functionally.

## A Minimal Mental Model

Imagine a simple microcontroller with a UART peripheral. On real hardware, writing `0x41` to address `0x4000_0000` sends the ASCII character `'A'` through the serial port. A virtual prototype intercepts that write at the model level and either prints `'A'` to a host terminal or stores it in a buffer — same observable behavior, zero real hardware needed.

```cpp
// Simplified TLM-2.0 transport method in a UART model
void uart_model::b_transport(tlm::tlm_generic_payload &trans, sc_time &delay) {
    if (trans.get_command() == tlm::TLM_WRITE_COMMAND) {
        uint8_t data = *trans.get_data_ptr();
        std::cout << static_cast<char>(data); // "send" to console
    }
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## Why the Term "Virtual"?

The word *virtual* emphasizes that no physical device exists. The prototype fulfills the same engineering role as an early physical breadboard — it lets engineers explore, test, and validate ideas — but it exists only in software. This makes it infinitely reproducible, easy to share across teams, and available before the first chip is fabricated.

## Interview Answer

> "A virtual prototype is a software model of a hardware system, accurate enough to boot and run unmodified target software, built from composable IP models and typically written in SystemC/TLM-2.0."

## Common Pitfalls

- **Confusing a VP with RTL simulation.** RTL simulates every clock cycle for every gate; a VP operates at a higher abstraction (transaction level) and is orders of magnitude faster.
- **Assuming bit-exact accuracy.** Most VPs are functionally accurate but do not model every timing edge or power rail. Timing accuracy is a separate, explicit design choice.
- **Forgetting the software perspective.** The measure of a VP's accuracy is whether the software running on it behaves identically to software running on real hardware — not whether the internal hardware state is perfectly reproduced.
