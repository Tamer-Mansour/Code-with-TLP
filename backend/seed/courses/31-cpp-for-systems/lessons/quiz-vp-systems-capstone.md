# Quiz: Virtual Prototyping and the Systems Interview Capstone

Test your understanding of virtual prototypes, RISC-V encoding, interpreter loops, memory-mapped I/O, and simulation performance.

---

**Q1. In a RISC-V R-type instruction, which bits hold the `funct7` field?**

- [ ] Bits [6:0]
- [ ] Bits [14:12]
- [ ] Bits [19:15]
- [x] Bits [31:25]

*`funct7` occupies the seven most-significant bits of a 32-bit R-type word. It distinguishes ADD from SUB and SRL from SRA.*

---

**Q2. Why must writes to register `x0` in a RISC-V simulator be silently discarded?**

- [ ] x0 is a read-only alias for the stack pointer.
- [x] x0 is hardwired to zero by the RISC-V specification; software relies on it always reading as 0.
- [ ] x0 is reserved for the operating system privilege level.
- [ ] x0 stores the program counter value.

*The RISC-V specification defines x0 as the zero register. Any ISS that allows x0 to be overwritten will produce incorrect results for instructions that use x0 as an implicit operand.*

---

**Q3. Which C++ technique correctly sign-extends a 12-bit I-type immediate to 32 bits?**

- [ ] `uint32_t imm = (instr >> 20) & 0xFFF;`
- [ ] `int32_t imm = (instr >> 20) & 0xFFF;`
- [x] `int32_t imm = static_cast<int32_t>(instr) >> 20;`
- [ ] `int32_t imm = (instr >> 20) | 0xFFFFF000;`

*Casting the full instruction word to `int32_t` before an arithmetic right shift by 20 propagates the sign bit correctly into the lower 12 positions. The other options either truncate the sign bit or unconditionally set the upper bits.*

---

**Q4. What is the primary purpose of a software TLB in an instruction-set simulator?**

- [ ] To validate virtual memory page permissions for guest firmware.
- [ ] To translate RISC-V instructions into x86 host instructions at compile time.
- [x] To cache host pointer lookups for guest RAM pages so that most memory accesses avoid the full bus dispatch.
- [ ] To model cache associativity and hit/miss rates.

*A software TLB stores host pointers indexed by guest page number. RAM hits are resolved in O(1) with a pointer dereference; only MMIO or unmapped addresses fall through to the slower bus dispatch path.*

---

**Q5. A peripheral register clears its interrupt-pending flag when read. How should this be modelled in a C++ VP?**

- [ ] The `Memory` class should zero the byte at the register's offset after every read.
- [ ] The bus should track all reads and automatically reset any address that was flagged as volatile.
- [x] The `Device::read()` override for that register should capture the flag value, clear the internal flag, then return the captured value.
- [ ] The CPU should write zero to the register address immediately after every load instruction targeting MMIO.

*Side-effect registers must be handled in the device's `read()` implementation. Delegating this to the bus or CPU breaks encapsulation and makes the model impossible to test in isolation.*

---

**Q6. Which simulation technique offers the largest potential speedup for an instruction-set simulator but also requires the most implementation effort?**

- [ ] Decode caching (memoising field extraction results)
- [ ] Computed-goto threaded dispatch
- [ ] Sparse memory pages using `std::unordered_map`
- [x] JIT (Just-In-Time) compilation of guest basic blocks to host machine code

*JIT compilation can achieve 10–50x speedup over a pure interpreter by executing guest instructions as native host code, eliminating the fetch-decode-dispatch overhead entirely. The cost is significant complexity: block management, invalidation for self-modifying code, and register allocation.*
