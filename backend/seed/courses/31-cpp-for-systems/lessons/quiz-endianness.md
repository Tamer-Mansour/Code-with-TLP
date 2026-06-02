# Quiz: Endianness and Data Representation

Test your understanding of byte ordering, integer encoding, and binary data serialization.

---

**Q1. The 32-bit integer `0xAABBCCDD` is stored in memory on a little-endian machine. What is the byte at the lowest memory address?**

- [ ] `0xAA`
- [ ] `0xBB`
- [ ] `0xCC`
- [x] `0xDD`

Little-endian stores the least significant byte first (at the lowest address). `0xDD` is the least significant byte of `0xAABBCCDD`.

---

**Q2. What does `htonl(x)` return when called on a big-endian machine?**

- [ ] The byte-swapped value of `x`
- [x] `x` unchanged
- [ ] The one's complement of `x`
- [ ] `x` right-shifted by 16

`htonl` converts from host byte order to network (big-endian) byte order. On a big-endian machine, host order already is network order, so the function is a no-op and returns `x` unchanged.

---

**Q3. Which of the following is the correct two's complement representation of `-1` in an 8-bit signed integer?**

- [ ] `0x00`
- [ ] `0x01`
- [ ] `0x7F`
- [x] `0xFF`

Two's complement of 1: invert all bits of `0x01` → `0xFE`, then add 1 → `0xFF`. All 8 bits set to 1 represents -1 in two's complement.

---

**Q4. You receive a 4-byte buffer `{0x00, 0x00, 0x04, 0xD2}` from a network socket (network byte order). What is the corresponding host-side `uint32_t` value in decimal?**

- [ ] 3288334336
- [x] 1234
- [ ] 872415232
- [ ] 4294966062

Network byte order is big-endian: `(0x00 << 24) | (0x00 << 16) | (0x04 << 8) | 0xD2` = `0x000004D2` = 1234.

---

**Q5. Why should you avoid using `memcpy` on an entire `struct` to send it over a socket without additional processing?**

- [ ] `memcpy` is too slow for network operations
- [ ] Structs cannot be copied with `memcpy`
- [x] Compiler-inserted padding and host-endian byte order make the binary layout non-portable
- [ ] The struct members may be in the wrong type

The compiler adds padding for alignment, and multi-byte integers are in host byte order. Both factors make raw struct bytes incorrect on a different machine or a different compiler build.

---

**Q6. In C++, which pointer type is allowed by the strict aliasing rule to read the raw bytes of any other object?**

- [ ] `int*`
- [ ] `void*`
- [x] `unsigned char*`
- [ ] `uint32_t*`

The C++ standard grants `char*`, `signed char*`, and `unsigned char*` special permission to alias any object type. `void*` cannot be dereferenced. `int*` and `uint32_t*` aliasing another type is undefined behaviour.
