# Signed vs Unsigned Loads (LBU, LHU)

When loading a value narrower than the register width, the CPU must decide what to put in the upper bits. RISC-V provides two distinct behaviors: **sign extension** and **zero extension**. Choosing the wrong one is a subtle but serious bug.

## The Problem: Extending a Narrow Value

A 64-bit register holds 64 bits. When you load an 8-bit byte, 56 bits are "empty." The hardware must fill them. There are two choices:

- **Sign extension**: Copy bit 7 (the sign bit) into all upper bits.
- **Zero extension**: Fill all upper bits with zeros.

These produce wildly different results for values with bit 7 set:

| Byte value | Hex | Sign-extended (64-bit) | Zero-extended (64-bit) |
|---|---|---|---|
| 127 | `0x7F` | `0x000000000000007F` | `0x000000000000007F` |
| 128 | `0x80` | `0xFFFFFFFFFFFFFF80` | `0x0000000000000080` |
| 255 | `0xFF` | `0xFFFFFFFFFFFFFFFF` | `0x00000000000000FF` |

For values 0–127 (bit 7 = 0), both produce the same result. The difference only matters for 128–255.

## RISC-V Unsigned Load Instructions

| Mnemonic | Width | Behavior |
|---|---|---|
| `LBU` | 8 bits | Zero-extends byte to XLEN |
| `LHU` | 16 bits | Zero-extends halfword to XLEN |
| `LWU` | 32 bits | Zero-extends word to 64 bits (RV64 only) |

The signed counterparts `LB`, `LH`, `LW` were covered in the previous lesson.

## When to Use Which

Use **signed loads** when the memory value represents a signed integer type:
- `int8_t`, `int16_t`, `int32_t` in C → `LB`, `LH`, `LW`
- Array of signed pixel deltas or audio samples

Use **unsigned loads** when the memory value is an unsigned type or bit pattern:
- `uint8_t`, `uint16_t`, `uint32_t` in C → `LBU`, `LHU`, `LWU`
- Network packet headers (lengths, flags, checksums)
- Character data (`char` is unsigned on most RISC-V ABIs)

## Worked Example: The Bug

```c
uint8_t color = 0xFF;   // red channel at max = 255
```

```asm
# Bug: using signed load for unsigned data
lb   x2, 0(x1)    # x2 = 0xFFFFFFFFFFFFFFFF (-1, not 255!)

# Correct: using unsigned load
lbu  x2, 0(x1)    # x2 = 0x00000000000000FF (255)
```

If you then compare `x2` to a threshold (say 200) using a signed branch:

```asm
li  x3, 200
blt x2, x3, too_dark   # With LB: -1 < 200 = TRUE → wrong branch taken!
                        # With LBU: 255 < 200 = FALSE → correct
```

This class of bug is common in graphics, networking, and embedded code where `char` or byte data represents unsigned values.

## C-Level Correspondence

```c
// C compiler generates LBU for:
uint8_t a = *ptr;

// C compiler generates LB for:
int8_t b = *ptr;

// C compiler may generate either for plain char
// depending on the ABI (-fsigned-char vs -funsigned-char)
char c = *ptr;
```

You can verify this with `objdump -d` or `riscv64-unknown-elf-objdump`.

## The `LWU` Special Case

On RV64, `LW` sign-extends a 32-bit word to 64 bits. `LWU` zero-extends it. The difference matters for values `>= 0x80000000`:

```asm
# Value at memory: 0xDEADBEEF (bit 31 = 1)
lw   x2, 0(x1)   # x2 = 0xFFFFFFFFDEADBEEF  (sign-extended, negative!)
lwu  x2, 0(x1)   # x2 = 0x00000000DEADBEEF  (zero-extended, positive)
```

## Common Pitfall

Forgetting that RISC-V has no "load unsigned word" on RV32 — because on a 32-bit machine, a word *fills the entire register*, so zero vs sign extension is irrelevant. `LWU` only exists in RV64.

> **Interview answer:** `LBU` and `LHU` zero-extend the loaded byte or halfword into the full register width, treating the memory value as unsigned. The signed variants `LB` and `LH` copy the sign bit into all upper bits. Using the wrong variant for unsigned data (like `uint8_t`) causes values >= 128 to appear negative.
