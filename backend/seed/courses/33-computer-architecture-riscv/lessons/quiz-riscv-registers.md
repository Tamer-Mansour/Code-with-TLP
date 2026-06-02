# Quiz: RISC-V Registers and Programming Model

**Q1. How many general-purpose integer registers does the base RISC-V ISA provide?**

- [ ] 8
- [ ] 16
- [x] 32
- [ ] 64

The base RV32I/RV64I ISA defines exactly 32 integer registers (x0–x31), each encoded in a 5-bit field inside every instruction word (2^5 = 32).

---

**Q2. What happens when an instruction writes a result to register x0?**

- [ ] The result is stored temporarily and discarded on the next write
- [ ] A hardware exception is raised
- [x] The write is silently discarded; x0 always reads as zero
- [ ] The result is written to x1 instead

x0 is hardwired to zero. Its write port is not connected to any storage cell, so writes have no effect and reads always return 0.

---

**Q3. Which instruction is the standard way to materialise a PC-relative address into an integer register?**

- [ ] `jal x0, offset`
- [x] `auipc rd, imm`
- [ ] `lui rd, imm`
- [ ] `lw rd, offset(pc)`

`AUIPC` (Add Upper Immediate to PC) computes `rd = PC + (imm << 12)`, enabling a two-instruction sequence to reach any 32-bit address relative to the current PC. `LUI` adds to zero, not to PC.

---

**Q4. A function uses register `s3` (x19) internally. According to the RISC-V ABI, what must it do?**

- [ ] Nothing — s3 is caller-saved
- [x] Save s3 on the stack at entry and restore it before returning
- [ ] Move s3's value to a temporary register for the duration
- [ ] Declare s3 as volatile in the calling code

`s2`–`s11` are callee-saved registers. Any function that modifies them must save the original value (typically on the stack) and restore it before returning.

---

**Q5. Which register holds the return address after a `jal ra, foo` instruction?**

- [ ] x0 (zero)
- [x] x1 (ra)
- [ ] x2 (sp)
- [ ] x10 (a0)

`jal rd, offset` stores `PC + 4` (the address of the next instruction) into `rd`. The ABI convention is to use `ra` (x1) as the link register for normal function calls.

---

**Q6. The RISC-V F extension adds floating-point support. How many floating-point registers does it provide, and how are they separate from integer registers?**

- [ ] 16 FP registers, aliased to x0–x15
- [ ] 32 FP registers, sharing the integer register file
- [x] 32 FP registers (f0–f31) in a completely separate register file
- [ ] 64 FP registers split between F and D extensions

The F/D extensions add a dedicated 32-entry floating-point register file (f0–f31). It is physically and architecturally distinct from the integer register file; FP loads (`flw`/`fld`) and stores (`fsw`/`fsd`) are required to move data between memory and FP registers.
