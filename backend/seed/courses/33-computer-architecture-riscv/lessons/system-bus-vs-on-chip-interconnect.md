# System Bus vs On-Chip Interconnect

As computers evolved from discrete boards to dense SoCs (System-on-Chip), the fabric connecting components moved from external copper traces to on-die metal layers. The two environments have radically different constraints, which drove the development of entirely different interconnect paradigms.

## The System Bus Era

A **system bus** runs on a printed circuit board (PCB) between separate chips. The classic example is the ISA bus connecting an Intel 8088 CPU to memory and I/O cards, or PCI connecting a processor to expansion slots.

Key constraints of the system bus environment:
- **Propagation delay** — signals must travel centimeters to inches; at 33 MHz a quarter-wavelength is ~22 cm (just barely manageable on a motherboard).
- **Pin count** — every signal requires a physical pin on the chip package and a trace on the board. Packages in the 1990s had 200–500 pins; every pin is expensive.
- **Impedance and termination** — board traces act as transmission lines; stubs cause reflections. Parallel buses require careful termination resistors.
- **Multiple vendors** — the bus must be standardized (ISA, PCI, SCSI) so cards from different manufacturers interoperate.

These constraints pushed system buses toward **wide parallel buses at low clock rates** — PCI used 32 or 64 parallel lines at 33–66 MHz.

## The On-Chip Interconnect Era

When an SoC integrates CPU cores, GPU, memory controllers, and dozens of peripherals on a single die, the interconnect moves entirely on-chip. On-chip metal wires have:

- **Nanosecond-scale delays** — millimeter-length wires at the speed of light in silicon.
- **Thousands of wires available** — chip routing has far more metal layers and available wires than a PCB.
- **No pin count constraint** — on-chip connections do not need to leave the die.
- **One vendor controls everything** — no interoperability requirement.

These freedoms enable **narrow-but-fast serial point-to-point links**, deep pipelining, and complex protocols like AMBA AXI that would be impractical across a PCB.

## AMBA and AXI

ARM's **AMBA** (Advanced Microcontroller Bus Architecture) defines the most widely used on-chip interconnect family:

| Bus | Full Name | Key Characteristic |
|-----|-----------|-------------------|
| APB | Advanced Peripheral Bus | Simple, low-frequency, for slow peripherals (UART, GPIO) |
| AHB | Advanced High-performance Bus | Single-channel, moderate bandwidth |
| AXI | Advanced eXtensible Interface | Separate read/write channels, out-of-order, high performance |
| ACE | AXI Coherency Extensions | Cache-coherent multi-core |
| CHI | Coherent Hub Interface | Mesh-based, for many-core coherent SoCs |

AXI separates the address and data phases into five independent channels (AR, R, AW, W, B), allowing multiple outstanding transactions — far more efficient than the one-at-a-time model of a classic bus.

```
AXI Master                  AXI Slave
   AR ──────────────────►  (Read Address)
   R  ◄──────────────────  (Read Data)
   AW ──────────────────►  (Write Address)
   W  ──────────────────►  (Write Data)
   B  ◄──────────────────  (Write Response)
```

## RISC-V and TileLink

The RISC-V ecosystem uses **TileLink** as its open-source, patent-free on-chip interconnect. TileLink defines:

- **TL-UL** (Uncached Lightweight) — simple, for low-bandwidth peripherals.
- **TL-UH** (Uncached Heavyweight) — supports burst and atomic operations.
- **TL-C** (Cached) — full cache-coherence protocol.

The Rocket Chip and Chipyard frameworks use TileLink extensively. Its open nature makes it attractive for academic and open-source RISC-V SoC development.

## Hierarchical Interconnect

Modern SoCs use **hierarchical** interconnects — a high-speed mesh or crossbar connects the major subsystems (CPU cluster, GPU, memory controller), while a simpler, slower bus (APB, AHB) fans out to simple peripherals. This avoids the overhead of running every UART through a high-performance AXI network.

```
[CPU cluster] ──AXI/CHI──► [Crossbar] ──AXI──► [Memory Controller]
                                       ──AHB──► [DMA Controller]
                                       ──APB──► [UART, GPIO, Timers]
```

**Interview answer:** System buses run between chips on a PCB and are constrained by pin count, propagation delay, and multi-vendor compatibility; on-chip interconnects like AXI and TileLink exploit the abundance of on-die wires to implement multi-channel, pipelined, out-of-order protocols that would be impossible on a PCB.
