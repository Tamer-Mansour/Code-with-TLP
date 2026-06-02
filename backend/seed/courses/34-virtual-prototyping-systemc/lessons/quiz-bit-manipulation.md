# Quiz: Number Systems and Bit Manipulation

Test your understanding of binary, hex, two's complement, and bitwise operations.

---

**Q1. What is the decimal value of the 8-bit two's complement number `0b1111'1010`?**

- [ ] 250
- [ ] 246
- [x] -6
- [ ] -10

Two's complement: the MSB has weight -128. Sum: -128 + 64 + 32 + 16 + 8 + 2 = -6. Alternatively, invert to get `0b0000'0101` = 5, add 1 → 6, so the original is -6.

---

**Q2. Which expression correctly clears bit 4 of an 8-bit register `r` without affecting any other bits?**

- [ ] `r |= (1 << 4)`
- [x] `r &= ~(1 << 4)`
- [ ] `r ^= (1 << 4)`
- [ ] `r -= (1 << 4)`

OR sets bits; XOR toggles; subtraction is not a safe general-purpose bit operation. AND with the complement of the bit mask is the canonical clear-bit idiom.

---

**Q3. A 32-bit register holds `0xA0B0'C0D0`. What is the value of bits 15:8 (the third byte from the LSB)?**

- [ ] 0xA0
- [ ] 0xB0
- [x] 0xC0
- [ ] 0xD0

`0xA0B0'C0D0`: byte 0 (bits 7:0) = 0xD0, byte 1 (bits 15:8) = 0xC0, byte 2 (bits 23:16) = 0xB0, byte 3 (bits 31:24) = 0xA0. Bits 15:8 is byte 1 = 0xC0.

---

**Q4. `align_up(0x1001, 0x1000)` using the formula `(addr + align - 1) & ~(align - 1)` evaluates to:**

- [ ] 0x1000
- [x] 0x2000
- [ ] 0x1001
- [ ] 0x1FFF

`(0x1001 + 0xFFF) & ~0xFFF` = `0x2000 & 0xFFFF'F000` = `0x2000`. Since 0x1001 is not aligned to 4096, we round up to the next page boundary.

---

**Q5. What does the expression `n & (n - 1)` accomplish for a non-zero integer `n`?**

- [ ] Isolates the lowest set bit of `n`
- [ ] Returns `n` rounded down to the nearest power of 2
- [x] Clears the lowest set bit of `n`
- [ ] Returns the bitwise complement of `n`

Subtracting 1 from `n` flips the lowest set bit to 0 and all lower bits to 1. ANDing with the original `n` clears those flipped bits, effectively removing the lowest set bit.

---

**Q6. Given `uint8_t x = 0b1010'1010`, what is `x ^ 0b1111'0000`?**

- [ ] `0b1010'0000`
- [ ] `0b0000'1010`
- [x] `0b0101'1010`
- [ ] `0b1111'1010`

XOR compares each bit pair: 1^1=0, 0^1=1, 1^1=0, 0^1=1 for the high nibble → `0101`; 1^0=1, 0^0=0, 1^0=1, 0^0=0 for the low nibble → `1010`. Result: `0b0101'1010` = 0x5A.
