# Mapping a Virtual Platform to a Real SoC

A virtual platform is only useful if it accurately mirrors the real chip. This lesson explains how to read a real SoC data sheet, extract what matters for a VP, and verify that the two are consistent.

## What to Extract from a Data Sheet

| Data sheet section | What the VP needs |
|---|---|
| Memory map table | Base addresses and sizes for all regions |
| Peripheral register map | Register offsets, field widths, reset values |
| Interrupt assignment table | IRQ numbers for each peripheral |
| Clock tree diagram | Clock domains and default frequencies |
| Reset chapter | Reset types (POR, warm, soft) and which registers are affected |
| DMA chapter | Channel assignments and flow-control signals |

You do not need to model every register bit — only those that firmware actually reads or writes.

## Address Map Correspondence

The VP memory map must be a strict superset of what firmware expects. Discrepancies cause hard-to-debug issues: firmware writes to an address the VP ignores, or reads an address that returns 0 instead of a reset value.

```
SoC data sheet         Virtual Platform
──────────────         ────────────────
0x00000000  Flash      RomModel(base=0x00000000, size=512KB)
0x20000000  SRAM       RamModel(base=0x20000000, size=256KB)
0x40000000  UART0      UartModel(base=0x40000000)
0x40000400  UART1      UartModel(base=0x40000400)
0x40001000  Timer0     TimerModel(base=0x40001000)
0x40001400  Timer1     TimerModel(base=0x40001400)
0xE0000000  CoreSight  CortexDebugModel(base=0xE0000000)
```

## Register Reset Values

Firmware boot code often relies on reset values. If the VP resets a register to 0 but the real chip resets it to `0x0000_0001`, the firmware may skip initialization and break in unexpected ways.

```cpp
// Always initialize registers to their data-sheet reset values
constexpr uint32_t UART_CR_RESET = 0x00000300; // 8N1, 9600 baud divisor
uint32_t CR = UART_CR_RESET;
```

## Interrupt Number Mapping

The IRQ numbering in the VP must match the vector table in the SoC:

```
UART0_IRQn  = 16   // offset 0x40 in vector table (Cortex-M convention)
UART1_IRQn  = 17
TIMER0_IRQn = 18
```

The CPU model accepts an interrupt number; it uses the number to index the vector table and fetch the ISR address.

## Peripheral Behavior Fidelity Levels

Not every peripheral needs cycle-accurate modeling:

| Level | When to use |
|---|---|
| **Stub** — always returns reset value | Peripheral not used by firmware under test |
| **Functional** — correct register semantics | Driver development and OS bring-up |
| **Timing-accurate** — models latency | DMA performance analysis |
| **Cycle-accurate** — exact pipeline behavior | Hardware/software co-verification |

Start with functional models for all peripherals; upgrade to timing-accurate only for the critical path.

## Validation Against the Real SoC

Once the VP runs firmware, compare against the real board:

1. **Register trace** — capture every register read/write on both platforms; diff the traces.
2. **Interrupt timing** — log interrupt arrival times; VP should be within 10% of real hardware for functional purposes.
3. **Memory contents** — dump RAM at key checkpoints; byte-for-byte match is the gold standard.

```bash
# Run firmware on VP and capture register trace
./vp --trace-regs firmware.elf > vp_trace.txt

# Compare with hardware trace captured via JTAG
diff vp_trace.txt hw_trace.txt
```

## Common Discrepancies

- **Unimplemented registers** — firmware reads a register not yet modeled; VP returns 0, real chip returns a non-zero status flag, causing a hang.
- **Wrong endianness** — byte-swap fields when the host and target differ.
- **Missing read-clear behavior** — some status registers clear on read; forgetting this causes firmware to see the same interrupt flag repeatedly.

**Interview answer:** Mapping a VP to a real SoC means transcribing the data sheet memory map, register reset values, and IRQ numbers into module parameters. The most common bugs come from wrong reset values, unimplemented registers that return 0, and missing read-clear semantics on status registers.
