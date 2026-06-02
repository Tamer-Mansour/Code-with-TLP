# Why Immediates Are Scrambled Across Fields

At first glance, the way RISC-V scatters immediate bits across non-contiguous instruction fields looks like an error. In reality, every scramble is a deliberate hardware optimization. This lesson explains the two core principles behind the scrambling and why they matter in silicon.

## Principle 1: The Sign Bit Is Always at Bit 31

Every RISC-V format that carries an immediate places the **sign bit at instruction bit 31**, regardless of how many total immediate bits the format contains.

| Format | Immediate width | Sign bit location in instruction |
|--------|----------------|----------------------------------|
| I      | 12 bits        | bit 31 |
| S      | 12 bits        | bit 31 |
| B      | 13 bits        | bit 31 |
| J      | 21 bits        | bit 31 |

Why does this matter? Sign extension is one of the most timing-critical paths in the decode stage. If the sign bit were in different positions per format, you would need a multiplexer to route the correct bit into the sign-extension chain. That mux adds gate delay. By anchoring the sign bit at bit 31 unconditionally, the hardware can begin sign-extension in parallel with format detection — shaving a critical path stage.

```
For all formats: sign_bit = instruction[31]
extended_imm = { sign_bit repeated, actual_imm_bits... }
```

No mux required on that path.

## Principle 2: Register Specifiers Stay in Fixed Positions

RISC-V keeps rs1, rs2, and rd in the same bit positions in every format that uses them:

| Field | Bits    | Present in |
|-------|---------|-----------|
| rs1   | [19:15] | R, I, S, B |
| rs2   | [24:20] | R, S, B |
| rd    | [11:7]  | R, I, U, J |

This means the register file can start reading rs1 and rs2 **the moment the instruction arrives**, before the opcode is fully decoded. Any immediate bit that would otherwise land in [24:20] or [19:15] would force the register file read to wait. By routing immediate bits away from those positions, RISC-V avoids adding a mux on the critical register-read path.

## How This Produces the Scramble

Consider S-type. You have a 12-bit immediate and two source registers. The natural layout would be:

```
[31:20] = imm[11:0]   (contiguous)
[19:15] = rs1
[14:12] = funct3
[11:7]  = rd  ← but stores have no rd
[6:0]   = opcode
```

Stores need rs2 where rd would be. Insert rs2 at [24:20], move imm[4:0] to [11:7] (the vacated rd slot), keep imm[11:5] at [31:25]:

```
[31:25] = imm[11:5]
[24:20] = rs2
[19:15] = rs1
[14:12] = funct3
[11:7]  = imm[4:0]
[6:0]   = opcode
```

rs1 and rs2 remain in standard positions. The only cost is one extra concatenation in the immediate reconstruction path.

## The B-Type Twist: Adjacent Bits Stay Adjacent

B-type goes further. Beyond the sign-bit rule and register-position rule, it also tries to keep bits that are **adjacent in the reconstructed immediate adjacent in the instruction word**.

In the final reconstructed B immediate:

```
bit position: 12 11 10  9  8  7  6  5  4  3  2  1  0(implicit)
```

Bits [12] and [11] appear together at the top. In the instruction word, bit 31 (imm[12]) and bit 7 (imm[11]) are placed such that a simple concatenation of two contiguous sub-fields reconstructs `imm[12:11]` with no gap. The hardware extracts `inst[31:25]` and `inst[11:7]` as two slices, then wires them directly — no individual-bit routing needed.

## Practical Impact for Software Writers

These optimizations are invisible when you use an assembler. They matter when you:

1. **Hand-encode instructions** — you must apply the scramble or your immediate is wrong.
2. **Write a disassembler or emulator** — you must un-scramble the fields to recover the original value.
3. **Answer interview questions** — examiners frequently ask candidates to explain *why* the B-type immediate is scrambled, not just *how* it is scrambled.

## Common Pitfall

Candidates who memorize the field positions without understanding the rationale often get confused when asked: "Why is bit 11 of the B-type immediate at instruction bit 7 and not at instruction bit 8?" The answer: because bit 7 is immediately below the sign bit in the reconstructed 13-bit value when the two slices are joined, minimizing wiring complexity in the concatenation MUX tree.

## Interview Answer

> "RISC-V immediates are scrambled for two hardware reasons: the sign bit is always at instruction bit 31 so sign-extension needs no mux, and register specifier fields stay at fixed positions so the register file can be read in parallel with decoding. The scramble is the minimum rearrangement needed to satisfy both constraints simultaneously."
