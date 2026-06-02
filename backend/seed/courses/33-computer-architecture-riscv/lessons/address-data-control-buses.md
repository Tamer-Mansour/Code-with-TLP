# Address, Data, and Control Buses

Every bus transaction involves three distinct kinds of information: **where** to read or write, **what** data to transfer, and **how** the transfer should happen. These three concerns map directly to the three sub-buses that every real bus architecture uses.

## The Address Bus

The address bus carries the **memory address or I/O port** that the CPU wants to access. It is driven exclusively by the bus master (usually the CPU or a DMA controller) and flows in one direction — outward from the master.

- Width determines the **addressable space**: a 32-bit address bus can address 2³² = 4 GiB.
- Lines are stable before the data transaction begins — the address is "set up" first.
- Peripheral devices decode a subset of address lines to determine if a transaction is meant for them.

```
Address bus (32 lines) ──►  0x2000_0400  ──► [RAM decoder sees match]
```

## The Data Bus

The data bus carries the actual payload — bytes being read from or written to a device. Unlike the address bus, it is **bidirectional**: the CPU drives it for writes; the addressed device drives it for reads.

Bidirectional lines use **tristate buffers** — a third logic state (high-impedance, "Z") that electrically disconnects a driver so another device can take over without a short circuit.

| Operation | Who drives address bus | Who drives data bus |
|-----------|------------------------|---------------------|
| CPU read  | CPU                    | Target device       |
| CPU write | CPU                    | CPU                 |
| DMA read  | DMA controller         | Memory              |

A typical data bus width matches the CPU's word size: 8, 16, 32, or 64 bits. Wider data buses increase **bandwidth** without changing the address space.

## The Control Bus

The control bus is a collection of individual signals that orchestrate the transaction. Common lines include:

- **R/W̄** (Read/Write-bar) — high = read, low = write.
- **MREQ̄** (Memory Request) — asserted when accessing memory (vs. I/O space).
- **IORQ̄** (I/O Request) — asserted for I/O port access.
- **CLK** — the bus clock that all participants synchronize to.
- **READY / WAIT** — a device asserts WAIT to insert wait states when it cannot respond in time.
- **BUSREQ / BUSACK** — handshake lines for bus arbitration (requesting and granting bus ownership).
- **IRQ / NMI** — interrupt request lines from peripherals to the CPU.
- **RESET** — system-wide reset signal.

Each control line is typically active-low (bar notation), meaning a device pulls the line to 0 V to assert it.

## A Complete Read Transaction

Here is a simplified timeline for a CPU memory-read:

```
Clock edge 1:  CPU drives address on address bus
               CPU asserts MREQ̄, deasserts R/W̄ (read mode)
Clock edge 2:  Memory sees its address, begins fetching data
               Memory may assert WAIT if it needs more time
Clock edge N:  Memory drives data onto data bus
               Memory deasserts WAIT
Clock edge N+1: CPU samples data bus, deasserts MREQ̄
```

## Multiplexed Buses

Some bus designs **multiplex** address and data onto the same physical wires to reduce pin count. The Intel 8086 used a 16-bit multiplexed address/data bus (AD0–AD15). An external latch (like the 8282) captured the address during the first bus cycle, freeing the lines for data in subsequent cycles.

- **Advantage:** fewer pins on the chip package.
- **Disadvantage:** adds latency (need an extra cycle for the address phase) and external latch logic.

## Common Pitfall

A wider data bus does **not** increase the address space — those are independent. A 64-bit data bus on a 32-bit address bus still only addresses 4 GiB. Confusing bus width with address width is a classic interview trap.

**Interview answer:** The address bus selects the target location, the data bus carries the payload, and the control bus provides signals (R/W, clock, wait, interrupt) that tell all parties how and when to participate in a transaction.
