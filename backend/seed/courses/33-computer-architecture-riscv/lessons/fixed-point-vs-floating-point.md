# Fixed-Point vs Floating-Point Numbers

Integers can only represent whole numbers. Real-world computation — physics simulations, audio processing, graphics — needs fractions. Two strategies exist: **fixed-point** and **floating-point**. Understanding the trade-offs determines which to reach for in embedded systems, financial software, and GPU shaders.

## Fixed-Point Representation

Fixed-point works by **implicitly** placing the binary point (analogous to a decimal point) at a fixed position within an integer. You choose the position at design time and stick with it.

### Notation: Q Format

A **Q(m.n)** number has `m` bits for the integer part and `n` bits for the fractional part (total width = m + n, plus possibly a sign bit).

```
Q4.4 (8-bit, unsigned): integer bits | fractional bits
                         [b7 b6 b5 b4 . b3 b2 b1 b0]

Bit weights: 8, 4, 2, 1 . 0.5, 0.25, 0.125, 0.0625

Example: 0110 1000 = 6 + 0.5 = 6.5
```

### Arithmetic in Fixed-Point

Addition and subtraction work identically to integers — the hardware does not need to know about the fractional position. Multiplication requires a right-shift to re-align the binary point:

```c
// Q8.8 fixed-point multiply (16-bit result from two Q8.8 values)
int16_t fixed_mul(int16_t a, int16_t b) {
    int32_t result = (int32_t)a * b;
    return (int16_t)(result >> 8);  // re-align binary point
}
```

### Advantages of Fixed-Point

- **Deterministic performance** — no variable-latency hardware unit needed.
- **Exact representation** of values that fit the chosen scale.
- **Hardware simplicity** — integer ALU suffices; critical for microcontrollers and DSPs.
- **Reproducibility** — same result on every platform (no rounding modes to worry about).

### Disadvantages of Fixed-Point

- **Limited dynamic range** — the scale is fixed; you cannot represent very large and very small numbers simultaneously.
- **Manual scaling** — the programmer must track the binary point position in every variable.
- **Overflow risk** — easy to overflow if the integer part is too narrow.

## Floating-Point Representation

Floating-point stores numbers in scientific notation in binary: **value = (−1)^sign × mantissa × 2^exponent**. The binary point "floats" to wherever it is needed, giving enormous dynamic range.

```
3.14 ≈ 1.10010001111 × 2¹   (binary scientific notation)
```

The trade-off is that most real numbers are **approximated** — floating-point is fundamentally imprecise unless the value happens to be a sum of exact powers of 2.

## Side-by-Side Comparison

| Property             | Fixed-Point                     | Floating-Point                  |
|----------------------|---------------------------------|---------------------------------|
| Range                | Narrow, fixed by format         | Wide (IEEE 754: ~10⁻³⁸ to 10³⁸)|
| Precision            | Uniform across range            | Relative (more near zero)       |
| Speed                | Same as integer                 | Slower without FPU; fast with   |
| Reproducibility      | Exact (bit-identical results)   | Platform/mode dependent         |
| Ease of use          | Must track binary point manually| Transparent to programmer       |
| Example use cases    | Audio DSP, financial, embedded  | Graphics, physics, ML, science  |

## Where Each Is Used

**Fixed-point** dominates in:
- **Audio processing** (e.g., 16-bit Q15 for samples in embedded DSPs)
- **Financial calculations** (exact cents, no rounding surprises)
- **Real-time control systems** where timing predictability matters

**Floating-point** dominates in:
- **3D graphics** (GPUs run billions of float operations per second)
- **Machine learning** (matrix multiplications in FP16/BF16/FP32)
- **Scientific computing** (wide dynamic range essential)

## A Pitfall With Floating-Point

```python
>>> 0.1 + 0.2
0.30000000000000004
```

`0.1` has no exact binary representation. Fixed-point (or integer cents) avoids this in financial code:

```c
// Store dollars as integer cents (fixed-point with implicit /100)
int32_t price_cents = 999;  // $9.99 — exact, no rounding
```

> **Interview answer:** Fixed-point places the binary point at a compile-time-chosen position, giving exact uniform precision but limited range; floating-point encodes a sign, exponent, and mantissa to achieve wide dynamic range at the cost of non-uniform precision and potential rounding errors. Use fixed-point when you need determinism and your values stay in a known range; use floating-point for wide-range scientific or graphics workloads.
