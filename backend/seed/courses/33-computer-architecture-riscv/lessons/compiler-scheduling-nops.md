# Compiler Scheduling and NOP Insertion

The pipeline hazard mitigation techniques discussed so far — forwarding, interlocks, branch prediction — are all hardware mechanisms. But software has an equally important role. The **compiler** can analyze instruction dependencies and reorder or insert instructions to prevent hazards from occurring in the first place, eliminating stall cycles without any hardware interlock firing.

## Two Compiler Strategies

### 1. Instruction Scheduling (Reordering)

The compiler identifies instructions with no data or control dependency on the hazard-causing instruction and moves them into the slot that would otherwise be a stall or bubble. The program semantics must be preserved — the compiler proves safety by checking that the moved instruction does not produce or consume the same registers as the instructions it jumps over.

```c
// C source
int x = a + b;
int y = c + d;
int z = x + 1;
```

Naive RISC-V:
```asm
add  x1, x2, x3   # x = a + b
addi x4, x1, 1    # z = x + 1  ← RAW hazard on x1 (2 stalls without forwarding / 0 with)
add  x5, x6, x7   # y = c + d
```

After compiler scheduling:
```asm
add  x1, x2, x3   # x = a + b
add  x5, x6, x7   # y = c + d  ← moved here: independent, fills the slot
addi x4, x1, 1    # z = x + 1  ← x1 now ready, no stall
```

The result is identical but the load-use (or post-ALU) dependency is satisfied without hardware stalling.

### 2. NOP Insertion

When no useful independent instruction exists to fill a hazard slot, the compiler inserts an explicit **NOP** (no-operation). This wastes a cycle but ensures correctness on hardware that does not have interlocks (some embedded DSPs and early RISC processors required software to manage all hazards).

```asm
lw   x1, 0(x2)
nop               # compiler-inserted — fills load-use slot
add  x3, x1, x4
```

NOP insertion is the fallback when scheduling fails. It is always correct but always wasteful. Modern compilers prefer scheduling and use NOPs only when the basic block has no independent instructions to move.

## The Dependency Graph

The compiler builds a **data dependence graph (DDG)** of the instructions in a basic block:

- Nodes = instructions
- Edges = dependencies (RAW, WAR, WAW) with weights = latency of the producing instruction

The scheduling problem is then: find a topological ordering of the DDG that satisfies all dependencies, minimizes the critical path length, and uses available hardware resources.

```
     [lw x1]  ← latency 2 (load-use penalty)
         |
     [add x3, x1, ...]
         |
     [sub x5, x3, ...]
```

An independent `addi x6, x7, 1` with no edges can be inserted after `lw x1` to hide the latency.

## Loop Unrolling and Scheduling

For loops, the compiler can **unroll** the loop body — replicate it N times before the branch — creating more independent instructions in the same basic block and giving the scheduler more freedom to fill hazard slots.

```c
// Original loop
for (int i = 0; i < 100; i++) a[i] = a[i] + 1;
```

Unrolled by 4:
```asm
# Processes 4 elements per iteration
lw   x1, 0(x2)
lw   x3, 4(x2)
lw   x5, 8(x2)
lw   x7, 12(x2)
addi x1, x1, 1   # no stall: lw for x1 was 3 cycles ago
addi x3, x3, 1
addi x5, x5, 1
addi x7, x7, 1
sw   x1, 0(x2)
...
```

The four load instructions execute back-to-back, and by the time the first `addi` executes, the load latency is already satisfied by the three intervening instructions.

## When the Compiler Cannot Help

Compiler scheduling works within a **basic block** — a straight-line sequence of instructions with no branches in or out. Across basic blocks (especially across function calls or through aliased pointers), the compiler may not be able to prove independence and must be conservative.

In these cases, the hardware interlocks are the safety net.

## Static vs Dynamic Scheduling

| Approach | Who Schedules | Visibility | Flexibility |
|---|---|---|---|
| Compiler scheduling | Compiler (static) | Full source-level info | Fixed at compile time |
| Hardware out-of-order | Processor (dynamic) | Runtime values, real latencies | Adapts to runtime behavior |
| VLIW | Compiler (static) | Explicit parallel slots | Very wide, compiler-heavy |

## Interview Answer

> "The compiler resolves pipeline hazards by reordering instructions — moving independent operations into the slots that would otherwise stall — and by inserting NOPs when no useful instruction can be moved. This reduces CPI without any hardware stall penalty. The compiler builds a dependency graph and schedules instructions to maximize distance between producers and consumers."
