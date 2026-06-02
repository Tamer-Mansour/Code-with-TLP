# Quiz: RISC-V Load-Store Architecture

**Q1. Which of the following best describes a load-store architecture?**

- [ ] Any instruction can read from or write to memory directly.
- [x] Only dedicated load and store instructions access memory; all other instructions operate on registers.
- [ ] Loads are combined with arithmetic in a single instruction.
- [ ] Memory is accessed through a separate co-processor.

Only load (LW, LB, etc.) and store (SW, SB, etc.) instructions touch memory in a load-store ISA. Arithmetic instructions such as ADD and AND operate solely on register values.

---

**Q2. You execute `LB x2, 0(x1)` and the byte at the address in x1 is `0x90`. On a 64-bit RISC-V hart, what value is placed in x2?**

- [ ] `0x0000000000000090`
- [x] `0xFFFFFFFFFFFFFF90`
- [ ] `0x9000000000000000`
- [ ] `0x0000000000000009`

`0x90` has bit 7 set (it equals -112 as a signed byte). `LB` sign-extends this, filling all upper 56 bits with 1s, producing `0xFFFFFFFFFFFFFF90`. Use `LBU` to zero-extend instead.

---

**Q3. What is the effective address computed by the instruction `LW x3, -4(x10)` when `x10 = 0x2000`?**

- [ ] `0x2004`
- [x] `0x1FFC`
- [ ] `0x2000`
- [ ] `0xFFFFFFFFFFFFFFFC`

The offset `-4` is sign-extended to the full address width, then added to the base: `0x2000 + (-4) = 0x1FFC`. The result `0x1FFC` is the effective address from which 4 bytes are read.

---

**Q4. In the RISC-V S-type encoding used by store instructions, why is the 12-bit immediate split across two non-contiguous bit fields?**

- [ ] To encode a larger offset than 12 bits.
- [ ] To allow stores to have a destination register.
- [x] To keep rs1 and rs2 at the same bit positions as in other instruction types, simplifying the hardware decoder.
- [ ] To support both signed and unsigned stores in one encoding.

Placing rs1 and rs2 at fixed positions (bits [19:15] and [24:20]) means the register-file read ports can always be wired to the same instruction bits. The immediate is split as a consequence of fitting two source registers into the fixed-width 32-bit encoding.

---

**Q5. Which RISC-V instruction is specifically needed before executing JIT-compiled code that was just written into a memory buffer?**

- [ ] `FENCE RW, RW`
- [ ] `FENCE W, W`
- [x] `FENCE.I`
- [ ] `LR.W`

`FENCE.I` synchronizes the instruction-fetch stream with data memory writes. Without it, the instruction cache may serve stale bytes from before the JIT code was written. `FENCE RW, RW` only orders data memory accesses, not instruction fetches.

---

**Q6. A `SC.W` (store-conditional) instruction returns a non-zero value in its destination register. What does this indicate?**

- [ ] The store succeeded and the memory was updated.
- [ ] The address was misaligned.
- [x] The store failed because the reservation set by the paired `LR.W` was invalidated.
- [ ] The value stored exceeded the 32-bit range.

In the LR/SC pair, `SC.W` writes 0 to its destination register on success and a non-zero value on failure. Failure means another hart wrote to the reserved address (or a context switch occurred) after the `LR.W`, so the programmer must retry the entire read-modify-write loop.
