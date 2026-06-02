# Quiz: RISC-V Instruction Formats

**Q1. Which RISC-V instruction format contains NO immediate field?**

- [ ] I-type
- [x] R-type
- [ ] S-type
- [ ] B-type

R-type uses all 32 bits for opcode, rd, funct3, rs1, rs2, and funct7 — there is no room for an immediate. Immediates first appear in I-type.

---

**Q2. In B-type instructions, where is the most-significant bit (sign bit) of the branch offset stored?**

- [ ] Bit 11 of the instruction word
- [ ] Bit 7 of the instruction word
- [x] Bit 31 of the instruction word
- [ ] Bit 12 of the instruction word

All RISC-V immediate formats place the sign bit at instruction bit 31. This avoids a multiplexer in the sign-extension path and is one of the key hardware-driven design choices.

---

**Q3. An `sw x5, 20(x2)` instruction is which format, and how are the bits of the offset 20 distributed?**

- [ ] I-type; contiguous in bits [31:20]
- [x] S-type; upper 7 bits in [31:25], lower 5 bits in [11:7]
- [ ] R-type; offset encoded in funct7 and rs2
- [ ] B-type; split across bits [31], [30:25], [11:8], [7]

Stores use S-type so that rs1 and rs2 occupy their standard bit positions. The 12-bit offset is split between the vacated funct7 slot (high bits) and the vacated rd slot (low bits).

---

**Q4. What is the maximum positive PC-relative offset encodable by a `jal` instruction?**

- [ ] 2047 bytes
- [ ] 4094 bytes
- [x] 1,048,574 bytes (~1 MB)
- [ ] 268,435,454 bytes (~256 MB)

J-type carries a 21-bit signed offset (20 bits stored, LSB always 0). Maximum positive value: 2^20 - 2 = 1,048,574 bytes. B-type branches are limited to ±4094 bytes (13-bit offset).

---

**Q5. Which pair of instructions is typically combined to load an arbitrary 32-bit constant into a register?**

- [ ] `jal` + `jalr`
- [ ] `auipc` + `jalr`
- [x] `lui` + `addi`
- [ ] `lw` + `addi`

`lui` loads the upper 20 bits of the constant (U-type), and `addi` adds the lower 12 bits (I-type, sign-extended). If the lower 12 bits are >= 0x800, the `lui` immediate must be incremented by 1 to compensate for the negative sign extension of `addi`.

---

**Q6. Which field distinguishes `add` from `sub` in RISC-V?**

- [ ] The opcode field (bits [6:0])
- [ ] The funct3 field (bits [14:12])
- [x] Bit 30 of the funct7 field
- [ ] The rd field (bits [11:7])

Both `add` and `sub` have opcode `0110011` and funct3 `000`. The only difference is bit 30 of funct7: 0 for `add` (funct7 = `0000000`) and 1 for `sub` (funct7 = `0100000`). Hardware checks exactly this one bit.
