# Synchronous vs Asynchronous Buses

How devices on a bus agree on *when* a signal is valid is a fundamental design choice. Two broad strategies exist: **synchronous** buses lock all participants to a shared clock, while **asynchronous** buses use a handshake protocol and need no common clock at all.

## Synchronous Buses

In a synchronous bus, a **clock signal** is broadcast to every device. All signal changes and samples happen at defined clock edges. The master drives the address on cycle 1, data appears on cycle 2 (or later, with wait states), and the master samples the data on a specific rising edge.

```
CLK:    ┌─┐ ┌─┐ ┌─┐ ┌─┐
        │ │ │ │ │ │ │ │
        ┘ └─┘ └─┘ └─┘ └─
ADDR:   ──[  VALID  ]────
DATA:   ────────[VALID]──
```

**Advantages:**
- Simple to design — every event is synchronized to a known edge.
- High throughput — no handshake overhead between cycles.
- Pipelining is straightforward.

**Disadvantages:**
- All devices must operate at the **same clock frequency** (or an integer fraction).
- The clock must propagate to every corner of the board with minimal **skew**. As boards get larger or frequencies get higher, skew becomes a critical constraint.
- Slow peripherals must insert wait states, stalling the whole bus.

**Examples:** PCI (33/66 MHz), ISA, the classical DRAM bus, AXI with a single clock domain.

## Asynchronous Buses

An asynchronous bus uses a **request/acknowledge handshake** instead of a clock. The master signals that data is ready; the slave signals that it has received it. No clock is needed — each transaction completes at whatever rate both parties can sustain.

```
Master asserts REQ  ─────────────────────────────────
Slave asserts ACK   ────────────────────────────
Master sees ACK, deasserts REQ ──────────
Slave sees REQ deasserted, deasserts ACK ────
```

This four-phase "full handshake" (also called "four-cycle asynchronous") guarantees no signal is missed regardless of how slow either side is.

**Advantages:**
- Works with devices of **different speeds** — no wait states, no clock domain problem.
- Tolerates any propagation delay — the handshake adapts automatically.
- No clock distribution network required.

**Disadvantages:**
- Lower peak throughput — each handshake costs multiple wire transitions.
- More complex logic — both master and slave must implement the handshake state machine.
- Harder to debug — no clock edges to scope against.

**Examples:** Original VMEbus control signals, some early microcontroller peripheral buses, the Caltech Async group's research chips.

## Semi-synchronous Buses

Real systems often blend both approaches. **PCI** is synchronous but allows a slow device to assert `TRDY#` (target ready) low to insert wait cycles — effectively a one-bit asynchronous "not ready" signal within an otherwise clocked protocol. This gives the simplicity of synchronous design with the flexibility to accommodate slow devices.

## Clock Skew: The Synchronous Bus Killer

Clock skew is the difference in arrival time of the clock signal at two different devices. If the skew is a significant fraction of the clock period, a device may sample data one cycle early or late — causing data corruption.

```
Max frequency ≈ 1 / (propagation_delay + setup_time + clock_skew)
```

This is why PCI topped out at 66 MHz for parallel buses — higher frequencies made skew management impractical across a shared backplane. PCIe solved this by going serial (one pair per lane) and embedding the clock in the data stream.

## Comparison Table

| Property | Synchronous | Asynchronous |
|----------|-------------|--------------|
| Clock | Required, shared | Not needed |
| Speed matching | All must match | Automatic |
| Throughput | High (no handshake overhead) | Lower |
| Design complexity | Low | Higher |
| Scalability | Limited by skew | Excellent |

**Interview answer:** Synchronous buses use a shared clock for simplicity and high throughput but suffer from clock skew and require all devices to run at the same rate; asynchronous buses use request/acknowledge handshakes that allow any-speed devices but add handshake overhead and design complexity.
