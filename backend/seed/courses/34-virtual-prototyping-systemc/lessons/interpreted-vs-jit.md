# Interpreted vs JIT-Based ISS

Once you decide to build or select an Instruction-Set Simulator, you face a second design choice: how does the ISS actually execute each instruction? The two mainstream approaches — interpretation and Just-In-Time (JIT) compilation — trade off simplicity for raw speed. Understanding both is essential for evaluating tools like QEMU, Spike, or a home-grown ISS.

## Interpretation: The Simple Approach

An interpreted ISS processes the guest instruction stream one instruction at a time. The main loop:

1. Fetches the next instruction word from the memory model.
2. Decodes it (usually via a giant `switch` on the opcode).
3. Calls the handler function for that opcode.
4. Advances the PC.

```cpp
// Simplified interpreted RISC-V ISS core loop
while (running) {
    uint32_t word = mem.read32(pc);
    Instruction instr = decode(word);

    switch (instr.opcode) {
        case ADD:  reg[instr.rd] = reg[instr.rs1] + reg[instr.rs2]; break;
        case ADDI: reg[instr.rd] = reg[instr.rs1] + instr.imm;      break;
        case LW:   reg[instr.rd] = mem.read32(reg[instr.rs1] + instr.imm); break;
        case SW:   mem.write32(reg[instr.rs1] + instr.imm, reg[instr.rs2]); break;
        case BEQ:  if (reg[instr.rs1] == reg[instr.rs2]) pc += instr.imm; continue;
        // ... dozens more
        default:   raise_illegal_instruction(); break;
    }
    pc += 4;
    reg[0] = 0; // x0 always 0
}
```

**Advantages of interpretation:**
- Simple to implement and debug — one handler per opcode.
- Easy to add instrumentation (tracing, coverage) at any instruction boundary.
- Correct behavior is straightforward to verify against the ISA spec.

**Disadvantages:**
- Every instruction requires a `fetch → decode → dispatch` round-trip through host C/C++ code.
- The host CPU branch predictor is under constant pressure from the opcode `switch`.
- Typical speed: **10–100 MIPS** for a careful C++ implementation.

## JIT Compilation: Trading Startup for Throughput

A JIT (Just-In-Time) ISS translates guest instructions into host machine code at runtime. Instead of interpreting each instruction individually, it:

1. Detects a new block of guest code (a **Translation Block**, TB) — usually a straight-line sequence ending at a branch.
2. Translates the entire block into host native code (x86-64, Arm64, etc.) and stores it in a **code cache**.
3. Jumps directly into the generated native code to execute the block.
4. On subsequent visits to the same guest PC, the JIT finds the existing TB in the cache and executes it immediately without re-translating.

```
Guest RISC-V code              Host x86-64 JIT output (conceptual)
─────────────────              ──────────────────────────────────
addi x1, x0, 5        →       mov dword [rbp + REG_OFFSET(1)], 5
add  x2, x1, x1       →       mov eax, dword [rbp + REG_OFFSET(1)]
                               add eax, eax
                               mov dword [rbp + REG_OFFSET(2)], eax
sw   x2, 0(x3)        →       mov edi, dword [rbp + REG_OFFSET(3)]
                               call mem_write32   ; ABI thunk
```

**Advantages of JIT:**
- Frequently executed blocks are native code — minimal per-instruction overhead.
- QEMU achieves **200–1000 MIPS** in TCG (Tiny Code Generator) JIT mode.
- Block chaining: consecutive blocks can be linked so the exit of one jumps directly to the entry of the next, eliminating dispatcher overhead.

**Disadvantages:**
- Significantly more complex to implement (you are writing a compiler back-end).
- Harder to instrument — inserting a trace point in the middle of a JIT block requires recompilation or patching.
- Cold-start penalty: the first execution of every block pays translation cost.
- Self-modifying code (SMC) must be detected and invalidated — a notoriously tricky corner case.

## Handling Self-Modifying Code

Self-modifying code is a significant challenge for JIT ISS implementations. When guest software writes to a page that already has a translated block, the ISS must:

1. Detect the write (via memory write hooks or page protection traps on the host).
2. Invalidate all TBs that overlap the written region.
3. Re-translate on the next execution.

QEMU handles this by write-protecting translated pages at the host OS level and handling the resulting `SIGSEGV` to trigger TB invalidation.

## Comparison Summary

| Property | Interpreted | JIT |
|---|---|---|
| Implementation complexity | Low | High |
| Warm-up time | None | Per new basic block |
| Peak throughput | 10–100 MIPS | 200–1000 MIPS |
| Instrumentation ease | Very easy | Harder (requires recompile or patching) |
| Self-modifying code | Trivial (no cache to invalidate) | Complex |
| Portability of ISS host | High (pure C++) | Depends on JIT back-end |

## Practical Recommendation

For most SystemC virtual prototypes, using **QEMU as an external ISS** (with its TCG JIT) gives near-maximum functional simulation speed with minimal custom development. A hand-written interpreted ISS is appropriate when you need deep instruction-level hooks (e.g., cycle-approximate annotations, custom memory models, or proprietary ISA extensions) and correctness is easier to audit than performance.

## Interview Answer

> "An interpreted ISS decodes and dispatches each instruction via a switch statement at runtime — simple but limited to roughly 10–100 MIPS. A JIT ISS translates basic blocks of guest instructions into host native code on first encounter, caching the result so subsequent executions are near-native speed, typically 200–1000 MIPS. The cost is a much more complex implementation and the need to handle self-modifying code by invalidating stale translation blocks."
