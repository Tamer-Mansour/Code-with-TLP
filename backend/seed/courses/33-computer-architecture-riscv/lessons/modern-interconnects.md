# Modern Interconnects: PCIe, AXI, TileLink

Classical parallel buses hit a wall in the early 2000s. Clock skew, pin count, and signal integrity made it impossible to push speeds beyond ~66 MHz over a shared PCB bus. The industry responded by moving to **serial point-to-point switched interconnects** for board-level connections and **multi-channel protocol-based fabrics** for on-chip. Three architectures dominate today: PCIe, AMBA AXI, and TileLink.

## PCIe: PCI Express

**PCI Express** (PCIe) replaced the parallel PCI bus starting in 2004. Instead of a wide parallel bus, PCIe uses narrow **serial lanes** (called x1, x4, x8, x16) where each lane is a pair of differential signal wires in each direction — full-duplex.

### Key Concepts

- **Lane**: one differential TX pair + one differential RX pair. Full-duplex, no arbitration needed.
- **Link**: one or more lanes bonded together (x1 to x16).
- **Packet-based**: data travels in **Transaction Layer Packets (TLPs)** — each packet contains a header (address, type, length) and payload.
- **Switched fabric**: a PCIe switch connects multiple endpoints; routing is by address, not shared-bus arbitration.

### Bandwidth per Generation

| Generation | Rate per lane | x16 bandwidth (each direction) |
|------------|--------------|-------------------------------|
| PCIe 1.0   | 2.5 GT/s     | ~4 GB/s                       |
| PCIe 3.0   | 8 GT/s       | ~16 GB/s                      |
| PCIe 4.0   | 16 GT/s      | ~32 GB/s                      |
| PCIe 5.0   | 32 GT/s      | ~64 GB/s                      |
| PCIe 6.0   | 64 GT/s      | ~128 GB/s                     |

**Interview answer:** PCIe is a serial, packet-switched, full-duplex interconnect where bandwidth scales by adding lanes, and transactions are routed by address through switches — no shared bus, no arbitration.

### Encoding

PCIe uses **8b/10b** encoding up to Gen 3 (20% overhead) and **128b/130b** in Gen 3+ (≈1.5% overhead). The encoding ensures DC balance and provides enough transitions for clock recovery.

## AMBA AXI: On-Chip High-Performance Interconnect

**AXI** (Advanced eXtensible Interface, part of ARM's AMBA spec) is the dominant on-chip interconnect for SoCs. It separates the transaction into five independent channels:

| Channel | Abbreviation | Direction | Purpose |
|---------|-------------|-----------|---------|
| Read Address  | AR | Master → Slave | Send read address + burst info |
| Read Data     | R  | Slave → Master | Return read data (possibly multiple beats) |
| Write Address | AW | Master → Slave | Send write address + burst info |
| Write Data    | W  | Master → Slave | Send write data beats |
| Write Response| B  | Slave → Master | Acknowledge write completion |

### Why Five Channels?

Separating address and data lets the master pipeline multiple outstanding transactions. A master can send addresses for transactions 1, 2, and 3 before receiving data for transaction 1 — increasing throughput when the interconnect or slave has non-zero latency.

```
Cycle:    1    2    3    4    5    6
AR:       [T1] [T2] [T3]
R:                   [D1] [D2] [D3]
```

AXI uses **valid/ready** handshake on every channel — a sender asserts `VALID` when it has data; the receiver asserts `READY` when it can accept. The transfer occurs on the cycle when both are high simultaneously.

```
VALID: ─────────┐        ┌─────
                └────────┘
READY: ─────────────┐    ┌─────
                    └────┘
XFER:              ↑  (this cycle)
```

## TileLink: Open RISC-V Interconnect

**TileLink** is an open, patent-free interconnect developed at UC Berkeley for RISC-V SoCs. It defines three conformance levels:

- **TL-UL** (Uncached Lightweight): simple get/put operations, no bursts. Used for APB-class peripherals.
- **TL-UH** (Uncached Heavyweight): bursts, atomics (AMO). Used for DMA and high-throughput masters.
- **TL-C** (Cached): adds acquire/release/probe messages for cache-coherent shared memory.

TL-C's coherence protocol is comparable to AMBA ACE — it supports a directory-based or snooping coherence model without proprietary licensing.

### TileLink vs AXI

| Feature | AXI4 | TileLink TL-C |
|---------|------|---------------|
| License | ARM proprietary | Open source |
| Coherence | ACE extension | Built into TL-C |
| Ecosystem | Dominant in industry | RISC-V / academic |
| Complexity | Moderate | Higher (coherence) |

## Practical Takeaway

The trend in all three standards is the same: **move from shared buses to switched, packet-based networks**. PCIe does this at the board level; AXI and TileLink do it on-chip. Each transaction carries its own address, allowing the fabric to route, pipeline, and reorder without the coordination overhead of a classical shared bus.
