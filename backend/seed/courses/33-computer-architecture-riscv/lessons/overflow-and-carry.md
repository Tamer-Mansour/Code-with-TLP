# Overflow, Carry, and Saturation

When arithmetic produces a result too large for the destination register, something must give. Understanding overflow, carry, and the hardware flags that detect them is essential for writing correct low-level code and for designing ALUs.

## Carry vs Overflow: The Core Distinction

These two words are often confused, but they describe different conditions:

- **Carry** — the result of treating bits as **unsigned** extended beyond the available width. It is an extra bit that would be needed to represent the result correctly.
- **Overflow** — the result of treating bits as **signed two's complement** is wrong — the mathematical result is outside the signed representable range.

Both can happen independently. A single addition can produce carry without overflow, overflow without carry, both, or neither.

## Unsigned Carry (Carry Flag)

For unsigned n-bit addition, carry occurs when the mathematical result ≥ 2ⁿ.

```
8-bit unsigned:
  200 + 100 = 300  →  300 mod 256 = 44
  1100 1000
+ 0110 0100
-----------
  0010 1100  ← stored result (44)
  ↑ carry-out from bit 7 set — carry flag = 1
```

The result 44 is **wrong** if interpreted as a full mathematical sum. The carry flag signals the lost bit.

## Signed Overflow (Overflow Flag)

For signed n-bit addition, overflow occurs when two operands of the **same sign** produce a result with the **opposite sign**.

```
8-bit signed:
  100 + 50 = 150  →  overflows int8 (max = 127)
  0110 0100  (+100)
+ 0011 0010  (+50)
-----------
  1001 0110  (-106 in two's complement!) ← overflow!
```

Both inputs were positive but the result has MSB=1 (negative) — overflow flag = 1.

```
  100 + (-50) = 50  →  no overflow possible with opposite signs
```

## Detecting Overflow in Hardware

Overflow for addition is detected by XOR-ing the carry into and out of the MSB:

```
overflow = carry_into_MSB XOR carry_out_of_MSB
```

In RISC-V, there is no dedicated overflow flag. Software must detect overflow explicitly:

```c
// Detect signed 32-bit overflow of a + b
bool adds_overflows(int32_t a, int32_t b) {
    int64_t result = (int64_t)a + b;
    return result > INT32_MAX || result < INT32_MIN;
}
```

## The Four Flag Combinations

| Carry | Overflow | What happened (8-bit example)                    |
|-------|----------|--------------------------------------------------|
| 0     | 0        | Normal: 50 + 50 = 100 (fits both signed/unsigned)|
| 1     | 0        | Unsigned wrap: 200 + 200 = 400 (unsigned wrong)  |
| 0     | 1        | Signed overflow: 100 + 100 = 200 (signed wrong)  |
| 1     | 1        | Both: 200 + 100 = 300 (wrong in both)            |

## Saturation Arithmetic

Instead of wrapping, **saturation** clamps the result to the maximum (or minimum) representable value. This is standard in signal processing and graphics, where a pixel brightness overflowing to black would look worse than clamping to white.

```c
// Saturating 8-bit unsigned add
uint8_t sat_add_u8(uint8_t a, uint8_t b) {
    uint16_t result = (uint16_t)a + b;
    return result > 255 ? 255 : (uint8_t)result;
}

sat_add_u8(200, 100)  // → 255, not 44
```

RISC-V's **packed SIMD** extensions (proposal P-extension) include saturating arithmetic. ARM's NEON and x86's SSE/AVX include it for multimedia operations.

## Subtraction and Borrow

Subtraction is addition with a negated operand. The carry flag in subtraction context is often called the **borrow** flag. In two's complement: `a − b = a + (~b) + 1`.

```
8-bit: 50 − 60 = -10  (signed, no overflow: -10 ∈ [-128, 127])

  0011 0010  (50)
+ 1100 0100  (~60 = 195)
+ 0000 0001  (+1)
-----------
  1111 0111  (-10 as two's complement) ✓
```

## Practical Implications

- **C signed overflow is undefined behavior.** The compiler may optimize away overflow checks written in C for signed types. Use `__builtin_add_overflow` (GCC/Clang) or widen to 64-bit to check safely.
- **Unsigned overflow is defined** (wraps modulo 2ⁿ) and is widely used for hash functions, CRCs, and ring buffers.
- **RISC-V lacks overflow trap.** Unlike MIPS (which has `ADD` vs `ADDU`), RISC-V provides no trapping add. Overflow detection is the programmer's responsibility.

```asm
# RISC-V: no built-in overflow detection
add  t0, t1, t2        # wraps silently on overflow

# Software overflow check for signed 32-bit:
add  t0, t1, t2
xor  t3, t1, t2        # check same sign inputs
blt  t3, zero, done    # inputs have different signs → no overflow possible
xor  t4, t0, t1        # result vs input sign
bge  t4, zero, done    # same sign → no overflow
# overflow detected here
done:
```

> **Interview answer:** Carry indicates the unsigned result exceeded the bit width (an extra bit was generated); overflow indicates the signed result is wrong (two same-sign inputs produced an opposite-sign result). They are independent: carry uses unsigned arithmetic, overflow uses signed. Saturation clamps rather than wraps, used in DSP and graphics.
