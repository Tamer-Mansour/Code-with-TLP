# Floating-Point Registers and the F/D Extensions

The base RISC-V ISA (RV32I / RV64I) contains only integer operations. Floating-point support is added through optional standard extensions:

- **F extension** — adds 32 single-precision (32-bit) floating-point registers and single-precision arithmetic.
- **D extension** — extends those same 32 registers to 64-bit (double-precision). D is a superset of F.
- **Q extension** — adds 128-bit quad-precision (rare, mostly for HPC).

A processor is designated **RV32IFD** or **RV64GC** (G = IMAFD bundled) to indicate which extensions are present.

## The Floating-Point Register File

The FP register file is completely separate from the integer register file. There are **32 FP registers**, named **f0–f31**, each 64 bits wide when D is present (32 bits when only F is implemented).

| Register range | ABI Names | Role | Preserved? |
|----------------|-----------|------|-----------|
| f0–f7 | ft0–ft7 | FP temporaries | No (caller-saved) |
| f8–f9 | fs0–fs1 | FP saved registers | Yes (callee-saved) |
| f10–f17 | fa0–fa7 | FP arguments / return values | No (caller-saved) |
| f18–f27 | fs2–fs11 | FP saved registers | Yes (callee-saved) |
| f28–f31 | ft8–ft11 | FP temporaries | No (caller-saved) |

The naming mirrors the integer ABI: `fa` = FP arguments, `fs` = FP saved, `ft` = FP temporaries.

## The Floating-Point Control and Status Register (fcsr)

`fcsr` is a 32-bit CSR that bundles:

- **fflags** (bits [4:0]) — sticky exception flags: NV (invalid), DZ (divide by zero), OF (overflow), UF (underflow), NX (inexact).
- **frm** (bits [7:5]) — rounding mode: RNE (round to nearest even), RTZ, RDN, RUP, RMM.

```asm
csrr  t0, fcsr      # read entire fcsr
csrw  fcsr, t0      # write entire fcsr
csrwi fflags, 0     # clear all FP exception flags
```

## Key F/D Instructions

### Loads and Stores

```asm
flw  fa0, 0(a0)     # load single-precision float from memory into fa0
fsw  fa0, 0(a0)     # store fa0 to memory (single-precision)
fld  fa0, 0(a0)     # load double-precision float
fsd  fa0, 0(a0)     # store double-precision float
```

### Arithmetic

```asm
fadd.s  fa0, fa1, fa2   # fa0 = fa1 + fa2 (single)
fmul.d  fa0, fa1, fa2   # fa0 = fa1 * fa2 (double)
fdiv.s  fa0, fa1, fa2   # fa0 = fa1 / fa2 (single)
fsqrt.d fa0, fa1        # fa0 = sqrt(fa1) (double)
```

### Fused Multiply-Add (FMA)

RISC-V natively supports FMA in one instruction — critical for high-throughput numerical code:

```asm
fmadd.s  fa0, fa1, fa2, fa3  # fa0 = fa1*fa2 + fa3
fmsub.s  fa0, fa1, fa2, fa3  # fa0 = fa1*fa2 - fa3
fnmadd.s fa0, fa1, fa2, fa3  # fa0 = -(fa1*fa2 + fa3)
```

FMA computes a multiply and an add with only one rounding step, improving both accuracy and throughput compared to separate `fmul` + `fadd`.

### Conversions

```asm
fcvt.w.s   a0, fa0         # convert float → signed 32-bit int
fcvt.s.w   fa0, a0         # convert signed 32-bit int → float
fcvt.d.s   fa0, fa0        # convert single → double (widening)
fcvt.s.d   fa0, fa0, rtz   # convert double → single (truncate)
```

Conversions are explicit — there is no implicit type promotion between integer and FP registers.

### Comparisons

```asm
feq.s  t0, fa0, fa1    # t0 = 1 if fa0 == fa1 (ordered)
flt.s  t0, fa0, fa1    # t0 = 1 if fa0 <  fa1 (ordered)
fle.s  t0, fa0, fa1    # t0 = 1 if fa0 <= fa1 (ordered)
```

Results land in integer registers (`t0`), enabling conditional branches with `beq`/`bne`.

## Calling Convention for FP Registers

- `fa0`–`fa7` pass the first eight FP arguments; `fa0`/`fa1` return FP results.
- A function receiving mixed integer + FP arguments uses both the `a` and `fa` banks simultaneously.
- `fs0`–`fs11` must be preserved by the callee (saved on the stack if used).

## Worked Example: Computing the Dot Product

```c
double dot(double *a, double *b, int n);
```

```asm
dot:
    fmv.d.x  fa0, x0       # accumulator = 0.0
    li       t0, 0          # i = 0
loop:
    bge      t0, a2, done   # if i >= n, done
    slli     t1, t0, 3      # byte offset = i * 8
    add      t2, a0, t1
    fld      ft0, 0(t2)     # load a[i]
    add      t3, a1, t1
    fld      ft1, 0(t3)     # load b[i]
    fmadd.d  fa0, ft0, ft1, fa0  # acc += a[i] * b[i]
    addi     t0, t0, 1
    j        loop
done:
    ret                     # result in fa0
```

## Common Pitfalls

- **Using integer loads (`lw`) to load FP values.** FP loads require `flw`/`fld` — the data goes into the FP register file, not the integer file.
- **Forgetting to save `fs` registers.** FP saved registers have the same obligation as integer `s` registers.
- **Mixing `.s` and `.d` instructions.** Using `fadd.s` on a value loaded with `fld` silently operates on the lower 32 bits of the 64-bit register.
- **Ignoring `fcsr` sticky flags.** Exceptional conditions (like divide by zero) set sticky flags that persist until explicitly cleared.

> **Interview answer:** The F and D extensions add 32 floating-point registers (f0–f31, 64-bit each with D) separate from the integer file. The calling convention mirrors integers: `fa0`–`fa7` for arguments, `fa0`/`fa1` for return values, and `fs0`–`fs11` are callee-saved. `fcsr` holds rounding mode and sticky exception flags.
