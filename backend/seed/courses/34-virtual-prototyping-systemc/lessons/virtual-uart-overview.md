# What a Virtual UART Must Model

A Universal Asynchronous Receiver/Transmitter (UART) is one of the oldest and most ubiquitous serial interfaces in embedded systems. When building a virtual platform in SystemC, the UART model must faithfully replicate enough hardware behavior that real firmware and drivers run without modification.

## The Role of a UART in a Virtual Platform

A virtual UART serves three audiences simultaneously:

- **Firmware under test** — the driver code running on the simulated CPU needs accurate register semantics.
- **Verification engineers** — the model must produce correct interrupts, status flags, and timing so test benches can validate software behavior.
- **Developers** — the model is connected to the host console, a PTY, or a socket so that printf output appears on screen and interactive input works.

## Core Behaviors to Replicate

A minimal UART model must capture the following:

| Feature | Why It Matters |
|---|---|
| Register map (THR, RHR, LSR, IER, LCR, FCR…) | The driver reads/writes these to control the device |
| TX and RX FIFOs | Buffering prevents data loss when the CPU is busy |
| Baud-rate divisor | Some drivers stall until the baud clock matches |
| Line Status Register (LSR) | Signals TX empty, RX data ready, and error conditions |
| Interrupt generation | Keeps the CPU from busy-polling the status register |
| Line Control Register (LCR) | Selects word length, stop bits, and parity |

## What You Can Safely Omit in Simulation

Not every real UART feature needs faithful simulation. You can safely approximate:

- **Exact bit timing** — SystemC time can be modeled at transaction level; you rarely need cycle-accurate baud-rate clocking unless testing a bit-bang driver.
- **Hardware parity checking** — parity errors can be injected on demand rather than computed from every transmitted byte.
- **Flow control pins (CTS/RTS/DTR/DSR)** — unless the driver polls these, stub them as always-asserted.

## Minimal vs. Full-Featured Model

```
Minimal model (TLM-2.0 initiator/target):
  ┌──────────────────────────────┐
  │  TLM target socket           │
  │  b_transport → reg decode    │
  │  TX path: THR write → fifo → host I/O │
  │  RX path: host I/O → fifo → RHR read  │
  │  LSR update after each op    │
  └──────────────────────────────┘

Full model adds:
  - Accurate FIFO depth (16 or 64 bytes)
  - Interrupt controller connection
  - Baud-rate divisor latch (DLL/DLM registers)
  - FIFO trigger levels (FCR bits)
  - Loopback mode
```

## A Crisp Mental Model

Think of the virtual UART as a **bidirectional, buffered pipe** with a register window on one end (facing the CPU bus) and a character stream on the other end (facing the host or the test bench). The register interface is the contract; everything else is implementation.

**Interview answer:** A virtual UART must model the register map (THR, RHR, LSR, IER), TX/RX FIFOs, interrupt generation, and LSR status updates — the minimum set that lets an unmodified driver transmit and receive characters correctly.

## Common Pitfalls

- **Missing TX-empty interrupt** — many UART drivers block until the interrupt fires; if the model never raises it, the driver stalls forever.
- **Wrong LSR initial state** — hardware typically powers up with TX FIFO empty (LSR bit 5 and bit 6 set). Forgetting this causes drivers to spin before the first write.
- **Shared FIFO pointer bugs** — if RX and TX share a single deque in the model, a busy TX path can corrupt RX data; keep them strictly separate.
- **Baud-rate divisor ignored** — drivers that write DLL/DLM before using the UART will crash if those writes fault instead of being silently accepted.
