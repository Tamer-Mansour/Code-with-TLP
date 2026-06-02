# Multiplexers, Decoders, and Encoders

Three combinational building blocks appear constantly in CPU design: **multiplexers** route data, **decoders** expand a compact code into individual signals, and **encoders** do the reverse. Every instruction-fetch, register-select, and ALU-opcode path relies on at least one of them.

## Multiplexer (MUX)

A **multiplexer** (data selector) selects one of `2^n` data inputs and forwards it to a single output, based on `n` select lines.

### 2-to-1 MUX

```
Inputs:  D0, D1
Select:  S
Output:  Y = S ? D1 : D0
```

Boolean expression: `Y = S̄·D0 + S·D1`

```
D0 ──┐
     ├──[ MUX ]──► Y
D1 ──┘     ▲
           S
```

### 4-to-1 MUX

```
Y = S1̄·S0̄·D0 + S1̄·S0·D1 + S1·S0̄·D2 + S1·S0·D3
```

| S1 | S0 | Y |
|----|----|----|
| 0  | 0  | D0 |
| 0  | 1  | D1 |
| 1  | 0  | D2 |
| 1  | 1  | D3 |

**CPU context**: The ALU source multiplexer selects whether an operand comes from a register, an immediate value, or memory — controlled by bits in the decoded instruction.

### MUX as a Universal Logic Element

A 4-to-1 MUX can implement **any** 2-variable Boolean function by hardwiring the data inputs to 0 or 1:

```python
# F = A XOR B using a 4-to-1 MUX (S1=A, S0=B)
# D0=0 (A=0,B=0 → 0), D1=1 (A=0,B=1 → 1),
# D2=1 (A=1,B=0 → 1), D3=0 (A=1,B=1 → 0)
```

## Decoder

A **decoder** takes an `n`-bit binary input and asserts exactly **one** of `2^n` output lines high — one-hot encoding.

### 2-to-4 Decoder

```
Inputs:  A1, A0  (2 bits)
Outputs: Y0–Y3   (one-hot)
Enable:  EN      (optional)
```

| A1 | A0 | Active Output |
|----|----|---------------|
| 0  | 0  | Y0 |
| 0  | 1  | Y1 |
| 1  | 0  | Y2 |
| 1  | 1  | Y3 |

Boolean expressions:
```
Y0 = Ā1·Ā0·EN
Y1 = Ā1·A0·EN
Y2 = A1·Ā0·EN
Y3 = A1·A0·EN
```

**CPU context**: The instruction decoder takes opcode bits and asserts one control signal per instruction type (ADD, SUB, LW, SW, …). In RISC-V, the 7-bit `opcode` field is first decoded to determine instruction class.

### Building a Larger Decoder

A 3-to-8 decoder can be built from two 2-to-4 decoders plus an inverter: use the MSB to enable one decoder or the other.

## Encoder

An **encoder** does the opposite of a decoder: it takes `2^n` inputs (one-hot) and outputs the `n`-bit binary address of the asserted input.

### 4-to-2 Encoder

| D3 | D2 | D1 | D0 | A1 | A0 |
|----|----|----|----|----|-----|
| 0  | 0  | 0  | 1  | 0  | 0  |
| 0  | 0  | 1  | 0  | 0  | 1  |
| 0  | 1  | 0  | 0  | 1  | 0  |
| 1  | 0  | 0  | 0  | 1  | 1  |

```
A0 = D1 + D3
A1 = D2 + D3
```

### Priority Encoder

A plain encoder breaks if two inputs are asserted simultaneously. A **priority encoder** resolves conflicts by selecting the highest-priority (usually highest-numbered) active input. Used in interrupt controllers to select which pending interrupt to service.

## Worked Example: Register File Read Port

A 32-register file needs a 5-bit address to select one of 32 registers:

```
5-bit rs1 address → 5-to-32 decoder → 32 "word-line" enables
                                          ↓
                                    32 tri-state buffers
                                          ↓
                                    32-bit data bus → ALU input A
```

The decoder fires exactly one word-line per read, which gates that register's contents onto the shared bus.

## Common Pitfalls

- **MUX vs decoder confusion**: a MUX routes data; a decoder activates control lines. Both use a binary select, but the outputs mean different things.
- **Undefined encoder output**: if zero inputs are asserted, the encoder output is meaningless — always add a "valid" output bit.
- **Fan-out limits**: in physical design, a single driver cannot connect to unlimited loads. Large decoders are often pipelined or buffered.

## Interview Answer

> "A MUX selects one data input based on select bits. A decoder converts a binary address to a one-hot signal — it is the gate-level equivalent of a `switch` statement. An encoder converts one-hot back to binary. Together they form the backbone of instruction decode and register-file addressing in every CPU."
