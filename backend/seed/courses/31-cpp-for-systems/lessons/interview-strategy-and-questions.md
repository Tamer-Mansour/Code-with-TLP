# Interview Strategy: Whiteboarding Systems Questions

Systems interviews at hardware-software boundary companies (Arm, Apple, Qualcomm, NVIDIA, Intel, SiFive) are different from typical LeetCode sessions. The interviewer wants to see how you *think* about hardware — not just whether you can sort a list. This lesson gives you a repeatable strategy.

## The Four-Phase Framework

### Phase 1 — Clarify the Hardware Context (2–3 minutes)

Before writing a single line, ask:

- "Is this a 32-bit or 64-bit architecture?"
- "Are we targeting a specific ISA, or is this generic?"
- "Do we need to model timing, or is functional correctness sufficient?"
- "Is memory coherence or multi-core a concern?"

This signals that you know hardware has dimensions that pure software problems do not.

### Phase 2 — Sketch the Data Structures

Draw the three boxes: CPU, Bus, Memory/Peripheral. Define the C++ types before writing methods:

```
CPU
 ├── uint32_t pc
 ├── uint32_t regs[32]
 └── step() -> void

Bus
 ├── map(base, size, device*)
 └── read32/write32

Device (interface)
 ├── read(offset, size)
 └── write(offset, val, size)
```

Interviewers reward candidates who separate concerns clearly.

### Phase 3 — Code the Critical Path

Code the thing they asked for — usually one of:

- A register-file class with x0 guard.
- A field extractor for a given instruction format.
- An address decoder.
- A FIFO or ring-buffer for a peripheral.

Write clean, commented code. Name variables after the hardware concept (`funct3`, not `f`).

### Phase 4 — Discuss Edge Cases Proactively

Do not wait to be asked. Volunteer:

- "x0 must be hardwired to zero."
- "Immediates need sign extension — I'll use arithmetic right shift."
- "Misaligned accesses should throw or raise an exception."
- "Self-modifying code invalidates any decode cache."

This is what separates a passing from an exceptional score.

## Common Whiteboard Questions and Crisp Answers

**Q: "How does a CPU communicate with a UART?"**

> "Through memory-mapped I/O. The UART is assigned a base address in the physical address space. Firmware writes to that address; the bus routes the transaction to the UART peripheral model instead of RAM. The UART's TX register causes a character to be transmitted; the RX register holds the next received byte."

**Q: "What is a TLB and why does a VP care?"**

> "A Translation Lookaside Buffer caches virtual-to-physical address mappings to avoid walking the page table on every access. In a VP, we model a software TLB — an array of host pointers indexed by guest page number — so that most memory accesses become a single pointer dereference, with the MMIO slow path only triggered on misses."

**Q: "What is the difference between functional and cycle-accurate simulation?"**

> "Functional simulation models correctness: given the same inputs, the output matches real hardware. Cycle-accurate simulation additionally models timing: stalls, pipeline stages, cache miss penalties. Functional simulation is 10–100x faster; cycle-accurate is required when validating performance or microarchitecture decisions."

**Q: "How would you handle an interrupt in a VP?"**

> "Each device exposes a `has_pending_irq()` method. After every instruction step, the CPU checks all wired interrupt lines. If one is asserted and the matching enable bit is set in the interrupt controller, the CPU saves PC, switches to the handler address (from the interrupt vector), and clears the pending flag."

## Body Language and Whiteboard Hygiene

- Write large enough for the interviewer to read from two metres away.
- Label every box and arrow.
- Say what you are typing as you type it — interviewers follow your reasoning, not just the result.
- If you get stuck, describe the ideal approach even if you cannot implement it in the remaining time.

## Preparation Checklist

- [ ] Can you extract all six R-type fields from a 32-bit word in under 30 seconds?
- [ ] Can you describe memory-mapped I/O without the interviewer prompting?
- [ ] Can you explain sign extension and why it matters?
- [ ] Can you sketch a bus decoder class from scratch?
- [ ] Can you discuss one performance technique (decode cache, software TLB, JIT)?
- [ ] Can you name three edge cases in an ISS (x0, sign extension, misalignment)?

If you can check every box, you are ready for a VP/OS systems interview.

## Interview Answer

> **Interview answer:** "I start by clarifying the hardware context, then sketch the three core abstractions (CPU, bus, device), implement the critical path with hardware-accurate naming conventions, and proactively enumerate edge cases — x0 guard, sign extension, unmapped address handling — before the interviewer asks."
