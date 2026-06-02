# Quiz: Endianness and Data Layout

**Q1. A 32-bit integer with the value `0xABCD1234` is stored at address `0x100` on a little-endian machine. What byte appears at address `0x100`?**

- [ ] 0xAB
- [ ] 0xCD
- [x] 0x34
- [ ] 0x12

_Little-endian stores the least-significant byte (LSB) at the lowest address. The LSB of `0xABCD1234` is `0x34`._

---

**Q2. Which of the following correctly converts a 32-bit integer from host byte order to network byte order in C?**

- [ ] `bswap32(x)`
- [x] `htonl(x)`
- [ ] `ntohl(x)`
- [ ] `__builtin_bswap32(x)`

_`htonl` (host-to-network long) converts a 32-bit value to big-endian network byte order. `bswap32` and `__builtin_bswap32` unconditionally swap bytes regardless of host order. `ntohl` converts the opposite direction (network to host)._

---

**Q3. What is the `sizeof` the following struct on a typical 64-bit platform with default alignment?**

```c
struct S {
    uint8_t  a;
    uint32_t b;
    uint8_t  c;
};
```

- [ ] 6
- [ ] 7
- [x] 12
- [ ] 8

_`a` (1 byte) is followed by 3 bytes of padding so `b` is 4-byte aligned. After `c` (1 byte) the compiler adds 3 bytes of tail padding so that an array of `S` keeps each `b` field aligned. Total = 1 + 3 + 4 + 1 + 3 = 12._

---

**Q4. You call `is_little_endian()` using the union trick. The probe word is set to `1` and `probe.bytes[0]` is `0`. What does this indicate?**

- [ ] The machine is little-endian
- [x] The machine is big-endian
- [ ] The machine is bi-endian
- [ ] The result is undefined behavior

_If `bytes[0]` is `0`, the least-significant byte (`0x01`) is at the highest address — the most-significant byte is at the lowest address. That is the definition of big-endian._

---

**Q5. Which Python `struct` format character correctly unpacks a 16-bit big-endian unsigned integer from a byte buffer?**

- [ ] `"<H"`
- [x] `">H"`
- [ ] `"=H"`
- [ ] `"@H"`

_`>` means big-endian (network byte order). `<` is little-endian. `=` and `@` use the native host byte order._

---

**Q6. On RISC-V, what happens when software executes a naturally-aligned `lw` instruction on a base ISA core?**

- [ ] It raises an alignment exception because RISC-V is big-endian only
- [ ] It performs a big-endian 32-bit load
- [x] It performs a little-endian 32-bit load and requires the address to be 4-byte aligned
- [ ] It is an optional instruction only present on RV64

_The base RISC-V ISA uses little-endian byte ordering and requires natural alignment for `lw` (4-byte aligned address). Misaligned accesses raise an address-misaligned exception unless hardware or firmware handles them. `lw` is present in both RV32 and RV64._
