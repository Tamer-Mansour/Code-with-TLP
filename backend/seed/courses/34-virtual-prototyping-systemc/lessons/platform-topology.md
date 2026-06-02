# Platform Topology and Wiring

Topology is the graph of modules and the connections between them. Getting it right before writing a single line of `sc_main` saves hours of debugging later.

## Common VP Topologies

### Star (Single Bus)

```
CPU ─┐
     ├─── [AHB Bus] ─── ROM
DMA ─┘                ├── RAM
                      ├── UART
                      └── Timer
```

Simple to implement; every transaction must traverse one central router. Suitable for simple MCU-class platforms.

### Multi-Layer (Crossbar)

```
CPU ─────────────── [High-speed crossbar] ─── Cache/DDR
DSP ─┘                                   └── DMA engine
          └─── [Peripheral bus bridge] ─── UART, GPIO, Timer
```

Real SoC designs separate high-bandwidth paths (CPU ↔ DDR) from low-bandwidth control paths (CPU ↔ peripherals). The **bridge** converts between bus protocols and frequency domains.

### Hierarchical

Large VPs nest sub-platforms:

```
[Platform top]
  ├── [CPU subsystem]       ← its own sc_module
  │     ├── CPU core
  │     └── L1 cache
  ├── [Memory subsystem]
  └── [Peripheral cluster]
```

Each subsystem exposes only a few sockets to the top level, hiding internal wiring.

## Wiring Rules

1. **Every initiator socket binds to exactly one target socket** (or a router that fans out). Unbound sockets cause a fatal error at `sc_start`.
2. **Address ranges must be non-overlapping** in each router's decode table.
3. **Base-address subtraction** — the router must subtract the target's base address before forwarding so the target sees a local offset, not a global bus address.
4. **Clock domain crossing** — if initiator and target run at different frequencies, insert a bus bridge or a TLM-2.0 AT model with appropriate timing annotations.

## Wiring in Code

Binding is done in the constructor or in `sc_main` using SystemC's `bind` method:

```cpp
// In sc_main
cpu.i_socket.bind(bus.target_socket[0]);
bus.initiator_socket[0].bind(rom.t_socket);
bus.initiator_socket[1].bind(ram.t_socket);
bus.initiator_socket[2].bind(uart.t_socket);
```

A common pattern is to wrap the binding logic in a helper function per subsystem:

```cpp
void connect_peripheral_cluster(Bus &bus, UART &uart, Timer &tmr) {
    bus.initiator_socket[UART_IDX].bind(uart.t_socket);
    bus.initiator_socket[TMRR_IDX].bind(tmr.t_socket);
}
```

## Topology Documentation

Before coding, draw the topology as a table:

| Socket pair | Base address | Size | Protocol |
|---|---|---|---|
| `cpu → bus[0]` | — | — | TLM-2.0 LT |
| `bus[0] → rom` | `0x0000_0000` | 64 KB | TLM-2.0 LT |
| `bus[0] → ram` | `0x2000_0000` | 128 KB | TLM-2.0 LT |
| `bus[0] → uart` | `0x4000_0000` | 4 KB | TLM-2.0 LT |

This table becomes the VP's **memory map specification** — the single source of truth used by both the VP authors and the firmware team.

## Pitfalls

- **Dangling sockets** — a socket declared but never bound will cause a runtime error. Always check by running `sc_start(SC_ZERO_TIME)` as a wiring smoke test.
- **Wrong index** — binding `initiator_socket[2]` to ROM when the decode table says index 0 silently routes all ROM traffic to the wrong device.

**Interview answer:** VP topology is the graph of initiator/target socket pairs plus a decode table. It must be documented as a memory map before coding, because binding errors often appear only at runtime and can be hard to trace without a reference table.
