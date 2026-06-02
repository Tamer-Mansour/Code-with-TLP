# Prompt: Detect Data Hazards in an Instruction Stream

## Problem Description

You are given a sequence of simplified RISC-V instructions for a five-stage in-order pipeline (IF → ID → EX → MEM → WB) with **full forwarding** hardware. Your task is to:

1. Identify every RAW (Read After Write) data hazard in the instruction stream.
2. Determine which hazards are resolved by forwarding (0 stall cycles) and which require a stall (1 stall cycle).
3. Report each hazard and the total stall cycle count.

## Rules

- Only RAW hazards within a gap of 0 or 1 instruction matter (gap >= 2 means the result is always available in time).
- **Gap = 0** (consumer is the immediately next instruction after producer):
  - If the producer is a **LOAD** instruction: 1 stall cycle (load-use hazard, forwarding cannot help).
  - If the producer is an **ALU** instruction: 0 stall cycles (forwarding resolves it via EX/MEM path).
- **Gap = 1** (consumer is 2 instructions after producer):
  - If the producer is a **LOAD** instruction: 0 stall cycles (MEM/WB forwarding resolves it).
  - If the producer is an **ALU** instruction: 0 stall cycles (MEM/WB forwarding resolves it).
- Stall penalties do not shift instruction positions for the purpose of hazard analysis in this simplified model (analyze the static instruction order as given).
- `x0` is hardwired to zero — writes to `x0` never create hazards.

## Instruction Format

Each instruction is one of these simplified forms (space-separated tokens):

```
add  rd, rs1, rs2      # ALU: destination = rd, sources = rs1, rs2
sub  rd, rs1, rs2      # ALU
and  rd, rs1, rs2      # ALU
or   rd, rs1, rs2      # ALU
addi rd, rs1, imm      # ALU (immediate): destination = rd, source = rs1
lw   rd, imm(rs1)      # LOAD: destination = rd, source = rs1 (base address)
sw   rs2, imm(rs1)     # STORE: no destination register; sources = rs1, rs2
beq  rs1, rs2, label   # BRANCH: no destination; sources = rs1, rs2
```

- Register names are `x0` through `x31`.
- Commas and parentheses are part of the token (e.g., `0(x2)` is one token, `x1,` is one token — strip them when parsing).
- Labels are strings (for `beq`) — ignore them.
- Instructions that have no destination (`sw`, `beq`) cannot be producers.

## Input Format

```
N
instr_1
instr_2
...
instr_N
```

- First line: integer N (1 ≤ N ≤ 100), the number of instructions.
- Next N lines: one instruction per line, exactly as described above.

## Output Format

For each RAW hazard detected (in order of the consumer instruction index, then producer index):

```
HAZARD: instr_I -> instr_J gap=G reg=xR [STALL|FORWARD]
```

Where:
- `instr_I` is the zero-indexed position of the producer (0-based).
- `instr_J` is the zero-indexed position of the consumer.
- `G` is the gap (0 or 1).
- `xR` is the register involved (e.g., `x1`).
- `STALL` if this hazard requires 1 stall cycle; `FORWARD` if forwarding resolves it.

After all hazard lines:

```
Total stalls: S
```

Where S is the total number of stall cycles.

If no hazards are found, print only:

```
Total stalls: 0
```

## Sample Input 1

```
4
lw x1, 0(x2)
add x3, x1, x4
sub x5, x3, x6
addi x7, x3, 1
```

## Sample Output 1

```
HAZARD: 0 -> 1 gap=0 reg=x1 STALL
HAZARD: 1 -> 2 gap=0 reg=x3 FORWARD
HAZARD: 1 -> 3 gap=1 reg=x3 FORWARD
Total stalls: 1
```

## Sample Input 2

```
3
add x1, x2, x3
add x4, x1, x5
add x6, x4, x7
```

## Sample Output 2

```
HAZARD: 0 -> 1 gap=0 reg=x1 FORWARD
HAZARD: 1 -> 2 gap=0 reg=x4 FORWARD
Total stalls: 0
```

## Constraints

- 1 ≤ N ≤ 100
- All register names are valid RISC-V register names (`x0`–`x31`).
- Input is well-formed; no need to validate syntax.
- Time limit: 3000 ms
- Memory limit: 256 MB
