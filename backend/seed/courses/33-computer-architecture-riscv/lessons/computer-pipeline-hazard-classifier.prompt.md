# Pipeline Hazard Classifier

## Problem Description

Given a sequence of RISC-V assembly instructions, classify data hazards between consecutive instructions in a 5-stage in-order pipeline (IF → ID → EX → MEM → WB) with **full forwarding** hardware.

For each instruction starting from the **second** instruction (index 2 onward), analyze whether it has a RAW hazard with any of the **previous 2 instructions**, and classify the result as one of:

- `NO_HAZARD` — no RAW dependency within 2 instructions.
- `FORWARDING (from instr<M>)` — RAW hazard exists but forwarding resolves it (no stall).
- `STALL_REQUIRED (load-use from instr<M>)` — load-use hazard that requires 1 stall cycle.

## Hazard Classification Rules

1. A **RAW hazard** occurs when instruction N reads a register that a preceding instruction M (within 2 positions back) writes to.
2. A **load-use hazard** occurs when M is a load instruction (`lw`, `lh`, `lb`, `ld`, `lhu`, `lbu`, `lwu`) AND M is **immediately before** N (distance = 1). This **cannot** be resolved by forwarding → `STALL_REQUIRED`.
3. All **other RAW hazards** within 2 instructions (distance 1 from a non-load, or distance 2 from any instruction) **CAN** be resolved by forwarding → `FORWARDING`.
4. Register `x0` is hardwired to zero — writes to `x0` **never** create hazards.
5. If multiple hazards exist (from both i−1 and i−2), report the **most severe** one first (STALL_REQUIRED takes priority over FORWARDING). If equal severity, report the closer instruction (i−1 before i−2).

## Instruction Format

Instructions use these simplified forms:

```
add   rd, rs1, rs2
sub   rd, rs1, rs2
and   rd, rs1, rs2
or    rd, rs1, rs2
xor   rd, rs1, rs2
sll   rd, rs1, rs2
srl   rd, rs1, rs2
addi  rd, rs1, imm
slti  rd, rs1, imm
lw    rd, offset(rs1)
lh    rd, offset(rs1)
lb    rd, offset(rs1)
ld    rd, offset(rs1)
lhu   rd, offset(rs1)
lbu   rd, offset(rs1)
lwu   rd, offset(rs1)
sw    rs2, offset(rs1)
sh    rs2, offset(rs1)
sb    rs2, offset(rs1)
sd    rs2, offset(rs1)
beq   rs1, rs2, label
bne   rs1, rs2, label
blt   rs1, rs2, label
bge   rs1, rs2, label
```

- Stores (`sw`, `sh`, `sb`, `sd`) and branches (`beq`, `bne`, `blt`, `bge`) have **no destination register** and cannot be producers.
- Loads write to `rd` and are the only instructions that cause load-use hazards.
- All other instructions with `rd` are ALU-type producers.

## Input Format

```
N
instr_1
instr_2
...
instr_N
```

- First line: integer N (2 ≤ N ≤ 50), the number of instructions.
- Next N lines: one instruction per line.

## Output Format

Print N−1 lines, one for each instruction starting at instruction 2:

```
instr<K>: NO_HAZARD
instr<K>: FORWARDING (from instr<M>)
instr<K>: STALL_REQUIRED (load-use from instr<M>)
```

Where `<K>` is the 1-based index of the current instruction and `<M>` is the 1-based index of the producer.

## Sample Input

```
6
lw x1, 0(x2)
add x3, x1, x4
sub x5, x3, x6
lw x7, 4(x5)
sw x7, 8(x5)
add x0, x1, x2
```

## Sample Output

```
instr2: STALL_REQUIRED (load-use from instr1)
instr3: FORWARDING (from instr2)
instr4: FORWARDING (from instr3)
instr5: STALL_REQUIRED (load-use from instr4)
instr6: NO_HAZARD
```

## Explanation

- **instr2** (`add x3, x1, x4`): reads `x1`; instr1 is `lw x1` (load, distance=1) → load-use STALL.
- **instr3** (`sub x5, x3, x6`): reads `x3`; instr2 writes `x3` (ALU, distance=1) → forwarding resolves it.
- **instr4** (`lw x7, 4(x5)`): reads `x5`; instr3 writes `x5` (ALU, distance=1) → forwarding resolves it.
- **instr5** (`sw x7, 8(x5)`): reads `x7`; instr4 is `lw x7` (load, distance=1) → load-use STALL.
- **instr6** (`add x0, x1, x2`): destination is `x0` (hardwired zero, never a producer). Reads `x1` and `x2`; instr1 writes `x1` but is 5 instructions back (distance > 2) → no hazard.

## Additional Sample Input

```
4
add x1, x2, x3
add x4, x1, x5
lw x6, 0(x4)
add x7, x6, x1
```

## Additional Sample Output

```
instr2: FORWARDING (from instr1)
instr3: FORWARDING (from instr2)
instr4: STALL_REQUIRED (load-use from instr3)
```

## Constraints

- 2 ≤ N ≤ 50
- All register names are valid RISC-V names (`x0`–`x31`).
- Input is well-formed; no need to validate syntax.
- Immediates and labels may be any string token; you do not need to parse their values.
- Use only the Python standard library.
- Time limit: 3000 ms
- Memory limit: 256 MB
