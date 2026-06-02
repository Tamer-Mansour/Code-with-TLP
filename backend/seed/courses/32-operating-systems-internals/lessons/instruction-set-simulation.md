# Instruction Set Simulation: Interpreted vs JIT

An Instruction Set Simulator (ISS) is the heart of any virtual prototype. It must faithfully reproduce what a target processor does — register state, memory effects, exception handling — while running as fast as possible on the host machine. Two fundamentally different strategies exist: **interpreted simulation** and **just-in-time (JIT) compilation**.

## Interpreted Simulation

In an interpreter, the host CPU executes a fetch-decode-execute loop written in C or C++. Each target instruction is decoded at runtime and dispatched to a handler function.

```c
// Simplified interpreted RISC-V loop
void interpret(CPUState *cpu) {
    while (!cpu->halted) {
        uint32_t instr = mem_read32(cpu->pc);
        uint32_t opcode = instr & 0x7F;          // RISC-V opcode field
        switch (opcode) {
            case 0x33: exec_r_type(cpu, instr); break;  // ADD, SUB, …
            case 0x03: exec_load(cpu, instr);   break;  // LB, LH, LW
            case 0x23: exec_store(cpu, instr);  break;  // SB, SH, SW
            case 0x63: exec_branch(cpu, instr); break;  // BEQ, BNE, …
            default:   raise_illegal(cpu, instr); break;
        }
        cpu->pc += 4;
    }
}
```

**Advantages**
- Simple to implement and debug.
- Easy to add per-instruction hooks (tracing, coverage, fault injection).
- Portable — the same C code runs on any host.

**Disadvantages**
- Every instruction costs several host instructions just for the decode overhead.
- Typical throughput: 50–200 MIPS on a modern host.
- Too slow for booting a full Linux distro in seconds.

> **Interview answer:** An interpreted ISS decodes each instruction at runtime inside a switch/dispatch loop; it is simple and easy to instrument but pays dispatch overhead on every instruction.

## JIT Compilation

A JIT ISS translates blocks of target instructions into host machine code at runtime. QEMU is the canonical example.

**Translation pipeline:**

```
Target binary
     │
     ▼  1. Lift to IR (TCG ops in QEMU)
Intermediate Representation (IR)
     │
     ▼  2. Optimize IR (dead-store elim, constant fold)
Optimized IR
     │
     ▼  3. Emit host machine code (x86-64, AArch64, …)
Host code buffer (Translation Block cache)
     │
     ▼  4. Execute natively; re-enter at block boundary
```

QEMU calls these translated units **Translation Blocks (TBs)**. Once a TB is compiled, it executes at near-native speed. A typical JIT ISS achieves **500 MIPS to 1 BIPS** — fast enough to boot Linux in a few seconds.

```c
// Conceptual QEMU TB execution loop (simplified)
for (;;) {
    tb = tb_lookup(cpu->pc);
    if (!tb) {
        tb = tb_gen_code(cpu);      // lift + compile
    }
    cpu_exec_tb(cpu, tb);           // run host code
    // tb_exit_reason: branch, interrupt, page fault…
    handle_exit_reason(cpu);
}
```

## Comparing the Two Approaches

| Property | Interpreted | JIT |
|---|---|---|
| Implementation complexity | Low | High |
| Instruction throughput | ~100 MIPS | ~1 BIPS |
| Hook/trace granularity | Per-instruction | Per-TB (coarser) |
| Boot time (full Linux) | Minutes | Seconds |
| Self-modifying code | Trivial | Requires TB invalidation |

## Self-Modifying Code — The JIT Hazard

When a target program writes to memory that has already been JIT-compiled, the cached TB is stale. The ISS must:

1. Mark every TB with the physical address range it covers.
2. When a store is executed, check if it hits any cached TB.
3. If yes, invalidate (flush) those TBs so they are recompiled on next execution.

This is called **SMC (Self-Modifying Code) detection** and is one of the trickiest correctness requirements in JIT-based simulators.

## Common Pitfalls

- **Incorrect flag semantics** — carry, overflow, and saturation flags are architecture-specific; an off-by-one in the carry condition breaks arithmetic-heavy code silently.
- **Unaligned accesses** — some targets support them, some trap. The ISS must match the target's behavior exactly.
- **Interrupt injection timing** — an interrupt must be checked between instructions (interpreter) or at TB boundaries (JIT). Missing an interrupt window can cause OS hangs.
- **Endianness** — the ISS must swap bytes on host/target endian mismatch for every memory transaction.

Understanding interpreted vs. JIT simulation helps you choose the right tool — Spike for accuracy, QEMU for speed — and diagnose subtle correctness bugs when firmware behaves differently on real silicon.
