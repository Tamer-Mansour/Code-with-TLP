# Load-Store Architecture as a RISC Hallmark

The load-store architecture is perhaps the single most defining characteristic of RISC designs. It establishes a strict separation between memory operations and computation, and that separation has profound consequences for pipeline design, performance predictability, and compiler strategy.

## The Core Rule

In a load-store architecture, there are exactly two ways to interact with memory:

1. **Load** — copy a value from memory into a register.
2. **Store** — copy a value from a register into memory.

All arithmetic, logic, and control instructions operate exclusively on registers. There is no "add from memory" or "multiply into memory" instruction. If you need to compute with a memory value, you must load it first.

```asm
# RISC-V: strict load-store model
lw   t0, 0(a0)       # LOAD: memory[a0+0] -> t0
lw   t1, 4(a0)       # LOAD: memory[a0+4] -> t1
add  t2, t0, t1      # COMPUTE: t0 + t1 -> t2 (no memory involved)
sw   t2, 8(a0)       # STORE: t2 -> memory[a0+8]
```

## Why This Rule Exists

Memory access has unpredictable latency. A cache miss can stall execution for 100-300 cycles. If an arithmetic instruction can also be a memory instruction, the pipeline cannot know in advance how long the instruction will take. It must either:

- Stall the pipeline until memory responds (hurts throughput), or
- Speculatively execute around the stall (requires complex out-of-order logic).

By making memory access explicit and separate, the load-store model gives the pipeline — and the compiler — complete visibility into when and where memory latency can occur.

## Contrast with CISC Memory Operations

In x86, arithmetic instructions can reference memory directly:

```asm
; x86: ADD reads one operand from memory
addl  4(%rdi), %eax        # eax = eax + memory[rdi+4]

; x86: XADD — exchange and add, atomically, in memory
xaddl %eax, (%rdi)         # memory[rdi] += eax; eax = old value
```

These instructions are powerful but opaque: the hardware must handle the memory access internally, complicating the pipeline. A cache miss inside an arithmetic instruction means the instruction cannot retire until the load completes — there is no way for the out-of-order engine to "look inside" a single instruction and split the load from the addition.

## Pipeline Benefits

The load-store model enables a clean five-stage pipeline:

| Stage | Action |
|---|---|
| IF | Instruction Fetch |
| ID | Decode, register read |
| EX | ALU operation (or address calculation for load/store) |
| MEM | Memory read or write (only loads/stores enter this stage) |
| WB | Write result to register |

For arithmetic instructions, the MEM stage is a no-op. For load/store instructions, the EX stage computes the address. The pipeline stages are regular and balanced. A load-use hazard (using a loaded value immediately) requires only a single stall cycle, which the compiler can often fill with an unrelated instruction.

## Compiler Strategy for Load-Store ISAs

Because loads are explicit, the compiler can:

- **Hoist loads early** — schedule a load several instructions before its result is needed, hiding memory latency.
- **Sink stores late** — delay stores until registers holding the values are no longer needed elsewhere.
- **Track register liveness precisely** — every register that holds a memory value has a defined load point.

```c
// C source
int sum(int *a, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}
```

```asm
# RISC-V compiler output (simplified)
loop:
    lw   t0, 0(a0)       # load a[i] early
    addi a0, a0, 4       # advance pointer (fills load latency slot)
    add  a1, a1, t0      # use t0 — 1 instruction after load, often safe
    addi a2, a2, -1      # decrement counter
    bnez a2, loop        # branch
```

## Common Pitfalls

- **Register pressure:** More explicit loads mean more live values in registers simultaneously. With 32 registers this is manageable; compilers must spill when pressure exceeds the register file size.
- **Atomic operations:** Strict load-store models need special primitives for atomics. RISC-V uses Load-Reserved / Store-Conditional (`lr.w` / `sc.w`) pairs — an elegant extension of the load-store model.

```asm
# RISC-V atomic increment using LR/SC
retry:
    lr.w  t0, (a0)       # load-reserved
    addi  t0, t0, 1      # increment
    sc.w  t1, t0, (a0)   # store-conditional (fails if reservation broken)
    bnez  t1, retry      # retry if another core wrote to a0
```

**Interview answer:** A load-store architecture restricts memory access to dedicated load and store instructions, forcing all arithmetic to operate on registers. This makes memory latency explicit and predictable, enabling clean pipelining and effective compiler scheduling.
