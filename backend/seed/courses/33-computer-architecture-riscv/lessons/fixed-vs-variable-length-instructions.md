# Fixed- vs Variable-Length Instructions

Instruction encoding is one of the most consequential decisions in ISA design. Whether every instruction occupies the same number of bytes (fixed-length) or a variable number (variable-length) affects the decoder, the pipeline, code density, and even security properties of the processor.

## Fixed-Length Instructions

In a fixed-length ISA, every instruction is exactly N bits wide. RISC-V, MIPS, and classic ARM use 32 bits per instruction.

```asm
; RISC-V: every instruction is exactly 32 bits
; Bit fields are always at the same positions:
; [31:25] funct7 | [24:20] rs2 | [19:15] rs1 | [14:12] funct3 | [11:7] rd | [6:0] opcode

add  x3, x1, x2    # 32-bit encoding, fields aligned
lw   x5, 8(x6)     # 32-bit encoding, I-type format
beq  x1, x2, label # 32-bit encoding, B-type format
```

### Advantages of Fixed-Length

- **Parallel fetch:** The processor knows exactly where instruction N+1 begins — at address `PC + 4`. No scanning required.
- **Aligned access:** Instructions are always word-aligned; a single memory read retrieves one complete instruction.
- **Simple decode:** Opcode, register fields, and immediates are always at predictable bit positions. The decoder is a combinational logic block, not a state machine.
- **Pipeline regularity:** Fetch, decode, and issue stages can operate at the same rate with no stalls from length discovery.

### Disadvantages of Fixed-Length

- **Code size:** Encoding a small immediate (e.g., `add x1, x2, 1`) wastes bits — the 32-bit instruction carries many zeros.
- **Jump offsets:** With a fixed word size, the immediate field available for branch targets is limited. RISC-V branches use a 13-bit signed offset (12 bits + 1 implicit), reaching ±4 KB without additional instructions.

## Variable-Length Instructions

x86 is the canonical variable-length ISA. Instructions range from 1 byte (`NOP`, `RET`) to 15 bytes (with all prefixes, a SIB byte, displacement, and immediate).

```asm
; x86: instruction lengths vary wildly
NOP                     ; 1 byte:  0x90
MOV EAX, 1             ; 5 bytes: B8 01 00 00 00
MOV RAX, [RBX+RCX*4+8] ; 4 bytes: 48 8B 44 8B 08
; With all optional prefixes: can reach 15 bytes
```

The x86 instruction format has evolved since 1978 and includes:
- Optional legacy prefixes (up to 4 bytes)
- Optional REX prefix (64-bit operand size, extended registers)
- Optional VEX/EVEX prefix (AVX instructions)
- Opcode (1-3 bytes)
- Optional ModRM + SIB bytes
- Optional displacement (0, 1, 2, or 4 bytes)
- Optional immediate (0, 1, 2, or 4 bytes)

### Advantages of Variable-Length

- **Code density:** Common short instructions (`PUSH`, `POP`, single-register ops) use 1-2 bytes. Programs are smaller.
- **Rich immediate encoding:** A 32-bit immediate can be embedded directly in a 6-byte instruction.
- **Backward compatibility:** Adding new instructions via new prefix encodings preserves old binary compatibility.

### Disadvantages of Variable-Length

- **Serial decode:** To find instruction N+1, you must fully decode instruction N. This serializes the decode stage.
- **Fetch complexity:** A 16-byte fetch window may contain anywhere from 1 to 15 instructions. Logic must determine boundaries.
- **Branch prediction complexity:** Predicting target alignment requires knowing instruction lengths.
- **Security surface:** Misaligned execution (jumping into the middle of an instruction) can unintentionally create valid instruction sequences — a source of ROP gadgets.

## RISC-V's Compromise: The C Extension

RISC-V acknowledges the code density problem with its optional "C" (Compressed) extension. This defines 16-bit versions of the most common instructions:

```asm
; Standard RISC-V (32-bit)
addi  x2, x2, -4     # 4 bytes

; RVC compressed equivalent
c.addi sp, -4        # 2 bytes — same semantics, half the space
```

The processor fetches 32-bit aligned chunks and checks bits [1:0] to determine if the instruction is 16-bit (`00`, `01`, `10`) or 32-bit (`11`). This allows a clean mixed-width encoding without the full complexity of x86's variable-length scheme.

## Comparison Table

| Property | Fixed (RISC-V) | Variable (x86) | RVC Hybrid |
|---|---|---|---|
| Decode complexity | Low | High | Medium |
| Code density | Lower | Higher | Medium-High |
| Pipeline regularity | High | Low | Medium |
| Security (gadget surface) | Smaller | Larger | Small |

**Interview answer:** Fixed-length instructions simplify decode and enable parallel fetch at the cost of code density; variable-length instructions pack more meaning per byte at the cost of serial decoding and pipeline complexity. RISC-V's optional compressed extension offers a middle ground.
