# Register Dumps and Interpreting Them

A register dump is a snapshot of the CPU's register file at a specific point in time. On a virtual prototype, you can request one at any moment without hardware probes. Knowing how to read a dump quickly — in under 30 seconds — is an essential embedded debugging skill.

## How to Obtain a Register Dump

**Via gdb:**

```
(gdb) info registers
r0             0x00000001     1
r1             0x20001000     536874000
r2             0x00000000     0
r3             0x40010000     1073807360
...
pc             0x000102c4     0x102c4 <uart_putchar+8>
cpsr           0x60000010     1610612752
```

**Via ISS API** (C++ model code):

```cpp
void Cpu::dump_registers(std::ostream& out) const {
    for (int i = 0; i < 16; i++)
        out << "r" << i << " = 0x" << std::hex << regs[i] << "\n";
    out << "pc   = 0x" << pc   << "\n";
    out << "cpsr = 0x" << cpsr << "\n";
}
```

**Via a monitor command in your RSP stub:**

```
(gdb) monitor regs
```

## Reading the ARM CPSR

The Current Program Status Register (CPSR) encodes the most critical CPU state:

```
Bit 31: N (Negative)
Bit 30: Z (Zero)
Bit 29: C (Carry)
Bit 28: V (Overflow)
Bit  7: I (IRQ disable)  — 1 = disabled
Bit  6: F (FIQ disable)  — 1 = disabled
Bits 4-0: Mode — 10000=User, 10011=SVC, 10111=Abort, 11111=System
```

Example CPSR value `0x600000D3`:

```
0x600000D3 = 0110 0000 0000 0000 0000 0000 1101 0011
              NZ..                                  mode=SVC, I=1, F=1
```

Interpretation: CPU is in Supervisor mode, both IRQ and FIQ disabled, Z and C flags set. If you expected to be in User mode with interrupts enabled, something went wrong during exception entry.

## Reading the RISC-V CSRs

RISC-V separates status into multiple CSRs. The most important for debugging:

| CSR | Name | Key bits |
|---|---|---|
| `mstatus` | Machine status | MIE (bit 3) = global interrupt enable |
| `mcause` | Machine cause | Exception code + interrupt bit (bit 63) |
| `mepc` | Machine exception PC | Address of the faulting instruction |
| `mtval` | Machine trap value | Faulting address for load/store faults |

```
mcause = 0x0000000000000005  →  Load access fault (code 5, interrupt=0)
mepc   = 0x0000000000010234  →  Faulting instruction address
mtval  = 0x0000000000000000  →  The address that caused the fault (NULL!)
```

## A Worked Register-Dump Triage

Scenario: the simulation stops with a data abort. The dump shows:

```
r0  = 0xDEADBEEF    ← suspicious sentinel value
r1  = 0x20001800    ← stack pointer region?
r2  = 0x00000000
pc  = 0x00000018    ← data abort vector
lr  = 0x000105A4    ← return address = instruction after the faulting one
cpsr= 0x600000D7    ← Abort mode, I+F disabled
```

Checklist:
1. `lr - 4 = 0x000105A0` — the faulting instruction. Disassemble that address.
2. `r0 = 0xDEADBEEF` — a classic uninitialized-memory sentinel. The code used an uninitialized pointer.
3. `cpsr` mode `10111` (Abort) confirms we entered the abort handler.

## Stack Pointer Sanity Check

A corrupted stack pointer is a common source of mysterious crashes. Check `sp` against the linker-script stack region:

```
sp = 0x20001FF8   ← top of 8 KB SRAM stack ending at 0x20002000  ✓
sp = 0x1FFFF3E0   ← below the bottom of SRAM                     ✗ overflow!
```

## Common Pitfalls

- **Mistaking lr for pc.** After a fault, `pc` is in the vector table; `lr - 4` (in ARM) is the faulting address. Confusing them leads to looking at the wrong instruction.
- **Mode bits overlooked.** Seeing `cpsr` in Abort mode when you expected User mode is itself a bug report — something faulted even if the handler seems to "recover."
- **Banked registers.** ARM has banked `sp` and `lr` per mode. `info registers all` in gdb shows the banked copies; plain `info registers` only shows the current mode's view.

> **Interview answer:** "I read the PC to find where execution stopped, the status register to determine CPU mode and interrupt state, and the link register to find the faulting caller — then cross-reference with the symbol table to get function names."
