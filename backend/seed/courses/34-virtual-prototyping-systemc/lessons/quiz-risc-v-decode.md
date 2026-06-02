# Quiz: RISC-V Instruction Decode

**Q1. Which field is at the same bit positions in ALL six RISC-V base instruction formats?**

- [ ] rd (destination register)
- [ ] rs1 (source register 1)
- [ ] funct3
- [x] opcode (bits [6:0])

The opcode always occupies bits [6:0]. rd, rs1, and funct3 share positions in most formats but not all (e.g., B-type and S-type use bits [11:7] for immediate, not rd).

---

**Q2. The instruction `0x00208033` decodes to which RISC-V assembly instruction?**

- [ ] SUB x0, x1, x2
- [x] ADD x0, x1, x2
- [ ] AND x0, x1, x2
- [ ] OR x1, x0, x2

`0x00208033`: opcode=0110011, funct7=0000000, rs2=2, rs1=1, funct3=000, rd=0 → ADD x0, x1, x2. funct7=0100000 would be SUB.

---

**Q3. An I-type instruction holds a 12-bit signed immediate. The value `0xFFF` in that 12-bit field represents which decimal number?**

- [ ] 4095
- [ ] 255
- [ ] 0
- [x] -1

`0xFFF` = 1111 1111 1111 in binary. The sign bit (bit 11) is set, so this is a negative number. In two's complement: 4095 − 4096 = −1.

---

**Q4. In a B-type branch instruction, why is the immediate split with bit[11] stored at bit[7] and bit[12] at bit[31]?**

- [ ] To allow 14-bit offsets instead of 13-bit
- [x] To keep rs1 and rs2 in their standard bit positions, shared with S-type decode
- [ ] To support unaligned branch targets
- [ ] To reduce the number of transistors in the ALU

The scrambled layout keeps rs1=[19:15] and rs2=[24:20] in exactly the same positions as R-type and S-type. A single decoder extracts these fields for all formats; only the immediate reconstruction differs.

---

**Q5. What is the correct way to extract and sign-extend a 12-bit I-type immediate from a 32-bit instruction in Python?**

- [ ] `imm = instr >> 20`
- [ ] `imm = (instr >> 20) & 0xFFF`
- [x] `imm12 = (instr >> 20) & 0xFFF; imm = imm12 - 0x1000 if imm12 & 0x800 else imm12`
- [ ] `imm = instr & 0xFFF`

The zero-masked form `& 0xFFF` leaves a positive 12-bit integer. You must then check bit 11 and subtract 4096 to get the signed value. `instr >> 20` alone can be positive or implementation-defined in other languages.

---

**Q6. Which statement about the U-type instruction format is TRUE?**

- [ ] The 20-bit immediate is sign-extended before being placed in rd
- [x] The 20-bit immediate is placed directly in bits [31:12] of rd; bits [11:0] are zeroed
- [ ] U-type instructions do not have a destination register
- [ ] U-type instructions use a 12-bit immediate like I-type

`LUI rd, imm` sets `rd = imm << 12`, making the upper 20 bits of rd equal to the encoded immediate. The lower 12 bits are set to zero. There is no sign extension — the immediate IS the upper portion of the result.
