# Exercise: Simulate Reads/Writes to an MMIO Register Map

In real embedded systems you cannot run device driver code without actual hardware. This exercise replaces the physical device with a software-simulated register map, letting you practice the read/write/flag-check patterns used in every device driver.

## What You Will Implement

You will simulate a **minimal UART peripheral** modelled as a flat array of 32-bit registers. The simulator accepts a sequence of operations on stdin — register reads and writes — and must correctly model:

- A **TX data register** (offset 0): writing a byte queues a character; the simulator echoes the character as output.
- A **TX status register** (offset 4): bit 0 is the "TX ready" flag. It starts as `1`. After a write to TX data it clears to `0`, then automatically sets back to `1` on the next operation (simulating the transmitter draining).
- An **RX data register** (offset 8): each read returns the next pre-loaded RX byte (provided in the initial setup). Bit 31 is the "RX empty" flag, set to `1` when no more RX data is available.
- An **interrupt enable register** (offset 12): a simple R/W register; no side effects.
- A **general read** of any register returns its current 32-bit value in decimal.
- **Write-1-to-clear** semantics on a dedicated **interrupt status register** (offset 16): writing a value clears only the bits that are `1` in the written value.

Your program reads operation lines from stdin and prints results to stdout. This simulates how an OS driver would interact with MMIO registers, just without the hardware.

## Skills Practiced

- Bit masking and shifting to inspect and set register flags.
- Read/write side-effect modelling.
- Write-1-to-clear register semantics.
- Simulating a finite RX FIFO with an empty flag.

## Getting Started

The prompt file `arch-mmio-register-simulator.prompt.md` contains the full input/output specification, constraints, and sample test cases.

Your solution should read all input from standard input and write all results to standard output. Use only the Python standard library — no third-party packages.
