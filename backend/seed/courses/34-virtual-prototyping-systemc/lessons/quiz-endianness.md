# Quiz: Endianness and Data Representation

Test your understanding of byte ordering, data widths, struct layout, and hexdump interpretation.

---

**Q1. A 32-bit value `0x0A0B0C0D` is stored at address `0x1000` on a little-endian system. What byte is at address `0x1001`?**

- [ ] `0x0A`
- [x] `0x0C`
- [ ] `0x0D`
- [ ] `0x0B`

_In little-endian, the least significant byte `0x0D` is at `0x1000`, `0x0C` at `0x1001`, `0x0B` at `0x1002`, and the most significant byte `0x0A` at `0x1003`._

---

**Q2. Which of the following correctly byte-swaps a `uint32_t` in C without invoking undefined behaviour?**

- [ ] `uint32_t r = (val << 24) | (val >> 24) | ((val & 0xFF00) << 8) | ((val & 0xFF0000) >> 8);`
- [x] `uint32_t r = ((val & 0xFF) << 24) | ((val & 0xFF00) << 8) | ((val >> 8) & 0xFF00) | (val >> 24);`
- [ ] `uint32_t r = *((uint32_t *)((char *)&val + 3));`
- [ ] `uint32_t r = __builtin_swap(val);`

_Option A shifts `val` (a `uint32_t`) left by 24, which is safe, but the mask-free `val << 24` can promote to `int` and overflow if `val >= 0x80000000` on a 32-bit `int` platform. Option B correctly masks each byte before shifting. Option C is a strict-aliasing violation. Option D is not a standard GCC built-in._

---

**Q3. What is `sizeof(struct S)` for the following struct on a typical 32-bit platform?**

```c
struct S {
    uint8_t  a;
    uint32_t b;
    uint8_t  c;
};
```

- [ ] 6
- [ ] 8
- [x] 12
- [ ] 9

_`a` occupies offset 0 (1 byte), then 3 bytes of padding are inserted so `b` starts at offset 4 (4-byte aligned). `c` occupies offset 8 (1 byte), then 3 bytes of tail padding bring the size to 12 — a multiple of the struct's alignment (4)._

---

**Q4. A hexdump line reads: `00000004  01 00 00 00`. On a big-endian system, what 32-bit value is stored at address `0x0004`?**

- [x] `0x01000000`
- [ ] `0x00000001`
- [ ] `0x10000000`
- [ ] `0x00000010`

_On a big-endian system, the byte at the lowest address is the most significant. Bytes are `01 00 00 00` from address `0x04` upward, so the value is `0x01000000`._

---

**Q5. Which C99/C11 type should you use to store a pointer as an integer safely on both 32-bit and 64-bit platforms?**

- [ ] `uint32_t`
- [ ] `unsigned long`
- [x] `uintptr_t`
- [ ] `size_t`

_`uintptr_t` from `<stdint.h>` is guaranteed to be wide enough to hold any pointer value on any platform. `uint32_t` truncates on 64-bit. `unsigned long` is 32 bits on 64-bit Windows (LLP64). `size_t` can hold an object size, but is not guaranteed to hold a pointer._

---

**Q6. In a TLM-2.0 generic payload, byte 0 of `data_ptr` always maps to which address?**

- [ ] The most significant address of the transfer
- [ ] The address of the initiator's local buffer
- [x] The lowest address of the transfer
- [ ] The bus base address

_The TLM-2.0 specification mandates that `data_ptr[0]` corresponds to the byte at the transfer's base address (the lowest address). The initiator places data in the buffer according to this convention regardless of the initiator's native endianness._
