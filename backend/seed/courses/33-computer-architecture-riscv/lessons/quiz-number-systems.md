# Quiz: Number Systems and Binary Representation

Test your understanding of binary, hexadecimal, signed integer encodings, and floating-point formats.

---

**Q1. What is the decimal value of the 8-bit two's complement bit pattern `1111 0110`?**

- [ ] 246
- [ ] -9
- [x] -10
- [ ] -6

The MSB weight is -128. Remaining bits: 64+32+16+4+2 = 118. Total: -128 + 118 = -10. Alternatively, flip → 0000 1001 = 9, add 1 → 10, so the value is -10.

---

**Q2. Which hexadecimal value corresponds to the binary string `1011 0111`?**

- [ ] 0xB3
- [x] 0xB7
- [ ] 0x73
- [ ] 0x37

Group into nibbles: `1011` = B, `0111` = 7. Result: 0xB7.

---

**Q3. A C program compares `int a = -1` with `unsigned int b = 1` using `a < b`. What is the result?**

- [ ] true, because -1 < 1
- [ ] compile error — cannot compare signed and unsigned
- [ ] undefined behavior
- [x] false, because -1 is implicitly converted to a large unsigned value (4294967295)

In C, when signed and unsigned are mixed in a comparison, the signed value is converted to unsigned. -1 becomes UINT_MAX (4294967295), which is greater than 1.

---

**Q4. In IEEE 754 single precision, what does a bit pattern with all-1s exponent and a non-zero fraction field represent?**

- [ ] Positive infinity
- [ ] The maximum finite float value
- [ ] A subnormal (denormalized) number
- [x] NaN (Not a Number)

All-1s exponent (255) with non-zero fraction = NaN. All-1s exponent with zero fraction = ±Infinity. All-0s exponent with non-zero fraction = subnormal.

---

**Q5. When sign-extending the 8-bit signed value `0x8A` (-118) to 16 bits, what is the result?**

- [ ] 0x008A
- [ ] 0xFF00
- [x] 0xFF8A
- [ ] 0x7F8A

The MSB of `0x8A` is 1, so sign extension fills the upper byte with 1s: `0xFF8A`. Zero-extension would give `0x008A`, which incorrectly represents +138 instead of -118.

---

**Q6. For 32-bit signed integers, what is the result of negating the minimum value INT_MIN (-2147483648)?**

- [ ] 2147483648 (positive, no problem)
- [ ] 0
- [x] -2147483648 (same value — overflow wraps back)
- [ ] 2147483647 (INT_MAX)

+2147483648 does not fit in 32 bits (max is 2147483647). The two's complement negation overflows and wraps back to the same bit pattern: `0x80000000` = -2147483648. In C this is undefined behavior for signed types.
