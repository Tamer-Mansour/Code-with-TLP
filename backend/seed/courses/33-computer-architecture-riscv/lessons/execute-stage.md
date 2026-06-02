# The Execute Stage in Detail

The **Execute** stage is where the actual computation happens. After fetch has retrieved the instruction and decode has figured out what it means, the execute stage performs the operation — whether that is an arithmetic calculation, a logical operation, an address computation, or a branch comparison. It is the heart of the CPU's function.

## The Arithmetic Logic Unit (ALU)

The central component of the execute stage is the **ALU** (Arithmetic Logic Unit). It is a combinational circuit that takes two operands and a function code, and produces a result in a single combinational delay (nanoseconds, not clock cycles).

In RISC-V, the ALU handles:

| Operation | RISC-V Instructions |
|---|---|
| Addition | `ADD`, `ADDI`, `LW`/`SW` address calculation |
| Subtraction | `SUB` |
| Bitwise AND/OR/XOR | `AND`, `OR`, `XOR` and I-variants |
| Shift left/right logical | `SLL`, `SRL`, `SLLI`, `SRLI` |
| Shift right arithmetic | `SRA`, `SRAI` |
| Signed/unsigned compare | `SLT`, `SLTU`, `SLTI`, `SLTIU` |
| Branch comparison | `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU` |

The ALU always computes a result. If the instruction does not need it (e.g., a store computes the address using the ALU but does not write a register), downstream stages simply ignore the value.

## ALU Input Selection (The Mux Problem)

The execute stage must decide which values to feed into the ALU. The first operand is almost always the value of register `rs1`. The second operand is either:

- The value of register `rs2` (R-type instructions), or
- The sign-extended immediate from the decode stage (I-type, S-type, etc.)

The `ALUSrc` control signal from the decoder drives a multiplexer that selects between these two options.

```
rs1 value ──────────────────────────────► A input
                                              │
rs2 value ──► MUX ──────────────────────► B input
              │ 0                         │
Immediate ──► │ 1          ALU ◄──────────┘
       ALUSrc─┘
```

In a forwarding-enabled pipeline, the execute stage receives additional mux inputs from the memory and write-back stages to bypass stale register values — this is called **operand forwarding** or **data forwarding**.

## Branch Resolution

For branch instructions, the execute stage serves double duty:

1. **Compute the branch condition** — subtract `rs1 - rs2` and inspect the result (or use a dedicated comparator) to determine if the branch is taken.
2. **Compute the branch target address** — add the PC from the fetch stage to the sign-extended immediate offset.

```asm
# BEQ rs1, rs2, offset
# Execute stage computes:
zero_flag = (rs1 == rs2)          ; comparison
branch_target = PC + (offset << 1) ; target address (B-type immediate already << 1)
```

If `zero_flag` is true, the next PC is set to `branch_target`; otherwise it remains PC + 4. In a pipelined processor, this determination happens in the execute stage, but the fetch stage has already fetched the next sequential instruction speculatively — if the branch is taken, those fetched instructions must be flushed.

## The ALU Control Unit

The ALU needs a precise operation code, but the decoder only produces a coarse `ALUOp` signal. The **ALU control unit** in the execute stage refines this using both `ALUOp` and the `funct3`/`funct7` fields passed through the pipeline:

```
ALUOp (from decoder) ──►
                         ALU Control ──► 4-bit ALU operation
funct3 (from IR) ──────►
funct7[5] (from IR) ───►
```

For example, `ALUOp=10` (R-type) combined with `funct3=000` and `funct7[5]=0` means ADD; combined with `funct7[5]=1` it means SUB.

## Worked Example: Execute Stage for `ADDI x5, x1, 10`

Given:
- `rs1` = x1, value = 7
- Immediate = 10 (sign-extended to 32 bits: `0x0000000A`)
- `ALUSrc` = 1 (use immediate as second operand)
- ALU operation = ADD

```
A = reg[x1] = 7
B = immediate = 10      (ALUSrc = 1 selects immediate)
result = A + B = 17     (binary: 0x00000011)
zero_flag = (result == 0)? → False
```

The value 17 is forwarded to the write-back stage to be stored in x5. The zero flag is relevant for branches, not for `ADDI`, so it is ignored by later control logic.

## Performance Considerations

- **Critical path:** The ALU is usually on the critical timing path. Making it faster (fewer gate delays) allows a higher clock frequency.
- **Multi-cycle operations:** Division and floating-point operations typically take many cycles. Rather than stall the entire pipeline, processors use separate **functional units** (divider, FPU) and stall only when their result is needed.
- **Forwarding paths add muxes.** Every forwarding path adds multiplexers on the ALU inputs, which increase combinational delay slightly.

## Common Pitfalls

- **Forgetting that load/store still use the ALU.** `LW` and `SW` compute the effective address (base register + offset) in the execute stage — the ALU is not idle.
- **Confusing branch comparison with subtraction.** For unsigned comparisons (`BLTU`, `BGEU`), the comparison logic must treat operands as unsigned. Reusing a signed subtraction for unsigned comparisons produces wrong results.
- **Missing the forwarding mux.** A naive implementation that only reads the register file in decode will produce stale values for back-to-back dependent instructions.

> **Interview answer:** The execute stage feeds the two operands (a register value and either another register or a sign-extended immediate) into the ALU, which performs the specified arithmetic, logical, or comparison operation and computes the effective address for memory instructions or the target for branches.
