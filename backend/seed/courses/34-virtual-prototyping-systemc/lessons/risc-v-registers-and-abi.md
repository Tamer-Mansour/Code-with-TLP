# RISC-V Registers and ABI Names

RISC-V defines 32 general-purpose integer registers, each XLEN bits wide (32 bits for RV32, 64 bits for RV64). The hardware sees them as x0–x31. The Application Binary Interface (ABI) gives them mnemonic names that reflect their calling-convention role. Understanding both views is essential when reading disassembly, writing a simulator, or debugging a crash.

## The 32 Integer Registers

| Register | ABI Name | Role | Saved by |
|----------|----------|------|----------|
| x0       | zero     | Hard-wired zero — reads always return 0, writes ignored | — |
| x1       | ra       | Return address | Caller |
| x2       | sp       | Stack pointer | Callee |
| x3       | gp       | Global pointer | — |
| x4       | tp       | Thread pointer | — |
| x5–x7   | t0–t2    | Temporaries | Caller |
| x8       | s0 / fp  | Saved register / Frame pointer | Callee |
| x9       | s1       | Saved register | Callee |
| x10–x11  | a0–a1    | Function arguments / return values | Caller |
| x12–x17  | a2–a7    | Function arguments | Caller |
| x18–x27  | s2–s11   | Saved registers | Callee |
| x28–x31  | t3–t6    | Temporaries | Caller |

> **x0 is the most-used pseudo-instruction enabler.** Writing to x0 discards the result; reading from x0 gives zero. This lets the assembler express `NOP` as `ADDI x0, x0, 0` and `MV rd, rs` as `ADDI rd, rs, 0`.

## Why Hard-Wired Zero Matters in a Simulator

In your ISA simulator, x0 must never hold a non-zero value after any instruction. The simplest implementation: after every write, force `regs[0] = 0`.

```cpp
struct RV32Core {
    uint32_t regs[32] = {};
    uint32_t pc = 0;

    void write_reg(int rd, uint32_t val) {
        if (rd != 0) regs[rd] = val;
        // x0 writes silently dropped
    }
    uint32_t read_reg(int rs) const {
        return regs[rs]; // regs[0] is always 0 by init + write guard
    }
};
```

## Calling Convention Summary

The RISC-V calling convention (psABI) defines two classes:

**Caller-saved (call-clobbered):** ra, t0–t6, a0–a7. The caller must save these before making a function call if it needs their values afterward.

**Callee-saved (call-preserved):** sp, s0–s11. A function that uses these must save them on entry and restore them on exit.

This split is critical for debugging. If a crash corrupts sp (x2) or s0 (x8), the callee violated its contract. If a0 (x10) has a garbage return value, the callee may not have set it.

## Floating-Point Registers

When the F or D extension is present, 32 additional floating-point registers f0–f31 (ABI names ft0–ft11, fa0–fa7, fs0–fs11) appear. They are separate from the integer register file and accessed only by floating-point instructions.

## CSRs — Control and Status Registers

Beyond the 32 GPRs, RISC-V defines up to 4096 Control and Status Registers addressed by a 12-bit index. Key ones every VP must know:

| CSR name | Address | Purpose |
|----------|---------|---------|
| mstatus  | 0x300   | Machine status (interrupt enable, privilege) |
| misa     | 0x301   | ISA extensions implemented |
| mepc     | 0x341   | Machine exception PC |
| mcause   | 0x342   | Cause of last trap |
| mtvec    | 0x305   | Trap-handler base address |
| cycle    | 0xC00   | Cycle counter (read-only, user mode) |

CSRs are accessed with `CSRRW`, `CSRRS`, `CSRRC`, and their immediate variants.

## Reading Disassembly

When GCC or `objdump` produces RISC-V assembly it uses ABI names by default:

```asm
# Fibonacci inner loop (RV32I)
addi  sp, sp, -16      # allocate 16 bytes on stack
sw    ra, 12(sp)       # save return address
sw    s0,  8(sp)       # save frame pointer
mv    s0, a0           # s0 = n  (argument)
beq   a0, zero, .ret  # if n == 0 goto ret
```

Translating back: `a0 = x10`, `s0 = x8`, `ra = x1`, `sp = x2`. Your simulator's register dump should show both numeric and ABI names.

## Common Pitfall

Do not confuse the ABI name with the encoding. The instruction encodes register numbers (5-bit fields, 0–31). When the assembler writes `mv a0, a1`, it emits `ADDI x10, x11, 0`. Your decoder works entirely in register numbers; the ABI name is only for human display.

> **Interview answer:** "RISC-V has 32 integer registers x0–x31. x0 is hard-wired zero. The ABI splits them into caller-saved temporaries (t0–t6, a0–a7, ra) and callee-saved registers (s0–s11, sp). Instructions always encode the numeric index."
