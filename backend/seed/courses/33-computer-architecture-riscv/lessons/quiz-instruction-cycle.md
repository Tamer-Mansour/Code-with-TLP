# Quiz: The Instruction Cycle

**Q1. Which register drives the fetch stage by holding the address of the next instruction to execute?**

- [ ] Instruction Register (IR)
- [x] Program Counter (PC)
- [ ] Memory Data Register (MDR)
- [ ] Stack Pointer (SP)

The PC is incremented after each fetch (PC ← PC + 4 in RISC-V) and updated to a branch target when a branch is taken. The IR holds the fetched instruction word, not the address.

---

**Q2. In a 5-stage RISC-V pipeline, which stage is a no-op (idle) for a `STORE` instruction?**

- [ ] Fetch (IF)
- [ ] Execute (EX)
- [ ] Memory Access (MEM)
- [x] Write-Back (WB)

A `STORE` writes a register value to data memory in the MEM stage but does not write any architectural register, so the WB stage has nothing to do. All stages are active for a `LOAD`.

---

**Q3. A load-use hazard occurs when a `LOAD` is immediately followed by an instruction that reads the loaded value. Why can forwarding alone NOT eliminate the stall?**

- [ ] Forwarding only works for R-type instructions
- [ ] The register file has only one read port
- [x] The loaded value is not available until after the MEM stage, which is too late for the very next instruction's EX stage
- [ ] The branch predictor interferes with the forwarding path

The execute stage of the instruction immediately following the `LOAD` needs the value before the MEM stage of the `LOAD` has produced it — a one-cycle gap that forwarding cannot bridge. One pipeline stall (bubble) is always required.

---

**Q4. In RISC-V, where is the saved return address placed when a `JAL` instruction executes?**

- [ ] In the `mepc` CSR register
- [ ] On the stack at the address held by `sp`
- [x] In the destination register `rd` (commonly `x1`/`ra`)
- [ ] In a dedicated link register invisible to software

`JAL rd, offset` stores PC+4 (the return address) into `rd` and jumps to PC + sign_extended_offset. By convention `x1` (alias `ra`) is used as `rd` for call instructions, making it the RISC-V link register.

---

**Q5. At what point in the instruction cycle does a RISC-V processor check for pending interrupts?**

- [ ] During the fetch stage, before the instruction is read
- [ ] During the decode stage, after the opcode is identified
- [ ] During the execute stage, alongside the ALU computation
- [x] At the boundary between completed instructions, after write-back and before the next fetch

Interrupts are checked at instruction boundaries — the only moment when all architectural state is consistent. Taking an interrupt mid-instruction would leave registers and memory in a partially updated state.

---

**Q6. Which of the following correctly describes the difference between an exception and an interrupt in RISC-V terminology?**

- [ ] Exceptions are handled in user mode; interrupts are handled in machine mode
- [x] Exceptions are synchronous events caused by the currently executing instruction; interrupts are asynchronous events caused by external hardware
- [ ] Exceptions always abort the program; interrupts always resume it
- [ ] Interrupts are a subset of exceptions triggered only by CSR instructions

In RISC-V, both exceptions and interrupts are "traps," but exceptions (illegal instruction, misaligned access, ECALL) are synchronous — tied to the current instruction — while interrupts (timer, external, software) are asynchronous signals from outside the CPU core.
