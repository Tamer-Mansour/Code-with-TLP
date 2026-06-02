# Quiz: Bit Manipulation

**Q1. Which expression correctly clears bit 4 of the variable `reg` (a `uint32_t`) without affecting any other bits?**

- [ ] `reg ^= (1u << 4);`
- [x] `reg &= ~(1u << 4);`
- [ ] `reg |= (1u << 4);`
- [ ] `reg -= (1u << 4);`

Explanation: AND with the complement of the mask (`~(1u << 4)`) sets bit 4 to 0 and leaves all other bits unchanged. XOR would toggle, OR would set, and subtraction is not a safe bitwise operation.

---

**Q2. What does the expression `x & (x - 1)` compute?**

- [ ] Isolates the lowest set bit of `x`
- [ ] Tests whether `x` is even
- [x] Clears the lowest set bit of `x`
- [ ] Returns the bitwise complement of `x`

Explanation: Subtracting 1 flips the lowest set bit to 0 and flips all trailing zeros to 1. ANDing with the original value masks those trailing ones away, leaving the lowest set bit cleared. This is used in Kernighan's popcount loop.

---

**Q3. Given `uint32_t x = 0b10110100;`, what is the value of `x & (-x)`?**

- [ ] `0b10000000`
- [ ] `0b00010000`
- [x] `0b00000100`
- [ ] `0b01001100`

Explanation: `-x` in two's complement flips all bits then adds 1, generating a carry that sets exactly the position of the lowest set bit. `x & (-x)` isolates that bit. The lowest set bit of `0b10110100` is bit 2 (`0b00000100`).

---

**Q4. Which of the following is undefined behavior in C++ (pre-C++20)?**

- [ ] `uint32_t x = 1u << 31;`
- [x] `int x = 1 << 31;`
- [ ] `uint32_t x = 0xFFFFFFFFu >> 1;`
- [ ] `uint8_t x = static_cast<uint8_t>(0xFF << 0);`

Explanation: Left-shifting `1` (a signed `int`) into the sign bit is undefined behavior before C++20. Using `1u` (unsigned) is safe because unsigned overflow wraps modulo 2^n.

---

**Q5. What does `(status >> 4) & 0x07` compute when `status` is an 8-bit register?**

- [ ] Sets bits 4-6 of `status`
- [ ] Returns the upper nibble of `status` as an 8-bit value
- [x] Extracts the 3-bit field at bits [6:4] of `status`
- [ ] Clears bits 4-6 of `status`

Explanation: Shifting right by 4 moves bits [6:4] into positions [2:0]. ANDing with `0x07` (0b111) then masks off any higher bits, leaving just those three bits as a value in the range [0, 7].

---

**Q6. To set bits 1, 3, and 5 of `flags` simultaneously in a single statement, the correct expression is:**

- [ ] `flags |= (1u << 1) & (1u << 3) & (1u << 5);`
- [ ] `flags &= (1u << 1) | (1u << 3) | (1u << 5);`
- [x] `flags |= (1u << 1) | (1u << 3) | (1u << 5);`
- [ ] `flags ^= (1u << 1) | (1u << 3) | (1u << 5);`

Explanation: OR (`|`) combines the individual single-bit masks into a multi-bit mask. Applying that mask with `|=` sets all three bits in one operation without disturbing the others. AND would clear bits, and XOR would toggle them.
