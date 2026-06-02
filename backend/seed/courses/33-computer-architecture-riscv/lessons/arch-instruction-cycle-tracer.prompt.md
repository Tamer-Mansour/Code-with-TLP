# arch-instruction-cycle-tracer

## Problem Statement

Implement a RISC-V instruction-cycle stage tracer. Given a sequence of instruction type names, output which of the five classic pipeline stages — IF, ID, EX, MEM, WB — are **active** for each instruction.

Stage activity rules:
- **IF** (Instruction Fetch): always active — every instruction must be fetched from memory.
- **ID** (Instruction Decode): always active — every instruction must be decoded and source registers read.
- **EX** (Execute): always active — every instruction uses the ALU (at minimum for address or branch target computation).
- **MEM** (Memory Access): active **only** for `LOAD` and `STORE`.
- **WB** (Write-Back): active for all instructions **except** `STORE` and `BRANCH`.

Active stages are shown as `*`; idle stages as `-`.

## Input Format

- One or more lines, each containing a single instruction type (uppercase).
- Valid types: `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLT`, `ADDI`, `LOAD`, `STORE`, `BRANCH`, `JAL`
- Input ends at EOF.
- At most 100 instructions.

## Output Format

For each input line, output exactly one line:

```
<TYPE>: IF=* ID=* EX=* MEM=<*|-> WB=<*|->
```

- Fields are separated by single spaces.
- The colon and space after `<TYPE>` are required.
- No trailing spaces.

## Constraints

- 1 ≤ number of instructions ≤ 100
- All input types are guaranteed to be from the valid list above.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input 1

```
ADD
LOAD
STORE
BRANCH
JAL
```

## Sample Output 1

```
ADD: IF=* ID=* EX=* MEM=- WB=*
LOAD: IF=* ID=* EX=* MEM=* WB=*
STORE: IF=* ID=* EX=* MEM=* WB=-
BRANCH: IF=* ID=* EX=* MEM=- WB=-
JAL: IF=* ID=* EX=* MEM=- WB=*
```

## Sample Input 2

```
ADDI
SUB
XOR
```

## Sample Output 2

```
ADDI: IF=* ID=* EX=* MEM=- WB=*
SUB: IF=* ID=* EX=* MEM=- WB=*
XOR: IF=* ID=* EX=* MEM=- WB=*
```

## Explanation

- `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLT`, `ADDI`, `JAL`: no memory access, result written to register → MEM=-, WB=*
- `LOAD`: reads data memory and writes register → MEM=*, WB=*
- `STORE`: writes data memory but does not update any register → MEM=*, WB=-
- `BRANCH`: compares registers in EX, redirects PC — no memory access, no register write → MEM=-, WB=-
