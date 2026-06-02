# Designing a Minimal RV32I Simulator

Building even a small RISC-V simulator from scratch is the single best exercise for cementing your understanding of ISA design, instruction encoding, and processor internals. This lesson walks through the architecture of a minimal **RV32I** simulator — one that can fetch, decode, and execute the 40 base integer instructions.

## Design Goals

A minimal simulator needs to handle:

1. **Architectural state** — 32 general-purpose registers + PC.
2. **Memory** — a flat byte-addressable array.
3. **Fetch** — read a 32-bit word at the PC address.
4. **Decode** — extract opcode, rs1, rs2, rd, and immediate fields.
5. **Execute** — update registers and memory; advance the PC.
6. **Termination** — EBREAK or a designated halt address.

## Data Structures

```c
#define MEM_SIZE (1 << 20)   /* 1 MiB */
#define NUM_REGS 32

typedef struct {
    uint32_t regs[NUM_REGS]; /* x0-x31 */
    uint32_t pc;
    uint8_t  mem[MEM_SIZE];
} RV32I_State;
```

`x0` (zero register) must always read as 0. Enforce this by writing `state->regs[0] = 0` after every instruction, or by guarding writes: `if (rd != 0) regs[rd] = result;`.

## Instruction Encoding Recap

RV32I uses six instruction formats. Every format places the opcode in bits [6:0]:

```
R-type:  [31:25 funct7] [24:20 rs2] [19:15 rs1] [14:12 funct3] [11:7 rd] [6:0 opcode]
I-type:  [31:20 imm12]              [19:15 rs1] [14:12 funct3] [11:7 rd] [6:0 opcode]
S-type:  [31:25 imm[11:5]] [24:20 rs2] [19:15 rs1] [14:12 funct3] [11:7 imm[4:0]] [6:0 opcode]
B-type:  [31 imm12][30:25 imm[10:5]][24:20 rs2][19:15 rs1][14:12 funct3][11:8 imm[4:1]][7 imm11][6:0 opcode]
U-type:  [31:12 imm20]                                              [11:7 rd] [6:0 opcode]
J-type:  [31 imm20][30:21 imm[10:1]][20 imm11][19:12 imm[19:12]]   [11:7 rd] [6:0 opcode]
```

## Decode Helpers in C

```c
static inline uint32_t get_opcode(uint32_t instr) { return instr & 0x7F; }
static inline uint32_t get_rd    (uint32_t instr) { return (instr >> 7)  & 0x1F; }
static inline uint32_t get_funct3(uint32_t instr) { return (instr >> 12) & 0x07; }
static inline uint32_t get_rs1   (uint32_t instr) { return (instr >> 15) & 0x1F; }
static inline uint32_t get_rs2   (uint32_t instr) { return (instr >> 20) & 0x1F; }

/* Sign-extend an n-bit value */
static inline int32_t sext(uint32_t val, int bits) {
    int shift = 32 - bits;
    return (int32_t)(val << shift) >> shift;
}

/* I-type immediate */
static inline int32_t imm_I(uint32_t instr) {
    return sext(instr >> 20, 12);
}

/* S-type immediate */
static inline int32_t imm_S(uint32_t instr) {
    uint32_t hi = (instr >> 25) & 0x7F;
    uint32_t lo = (instr >>  7) & 0x1F;
    return sext((hi << 5) | lo, 12);
}

/* B-type immediate */
static inline int32_t imm_B(uint32_t instr) {
    uint32_t b12  = (instr >> 31) & 1;
    uint32_t b11  = (instr >>  7) & 1;
    uint32_t b10_5 = (instr >> 25) & 0x3F;
    uint32_t b4_1  = (instr >>  8) & 0xF;
    return sext((b12 << 12) | (b11 << 11) | (b10_5 << 5) | (b4_1 << 1), 13);
}
```

## The Execute Dispatch

```c
void execute(RV32I_State *s) {
    uint32_t instr  = mem_read32(s, s->pc);
    uint32_t opcode = get_opcode(instr);
    uint32_t rd     = get_rd(instr);
    uint32_t rs1    = get_rs1(instr);
    uint32_t rs2    = get_rs2(instr);
    uint32_t funct3 = get_funct3(instr);
    uint32_t funct7 = (instr >> 25) & 0x7F;

    switch (opcode) {
        case 0x33: /* R-type ALU */
            if (funct3 == 0x0 && funct7 == 0x00) /* ADD */
                s->regs[rd] = s->regs[rs1] + s->regs[rs2];
            else if (funct3 == 0x0 && funct7 == 0x20) /* SUB */
                s->regs[rd] = s->regs[rs1] - s->regs[rs2];
            /* ... more funct3/funct7 cases ... */
            s->pc += 4; break;

        case 0x13: /* I-type ALU (ADDI, SLTI, ...) */
            if (funct3 == 0x0) /* ADDI */
                s->regs[rd] = s->regs[rs1] + imm_I(instr);
            s->pc += 4; break;

        case 0x03: /* Loads */
            { uint32_t addr = s->regs[rs1] + imm_I(instr);
              if (funct3 == 0x2) /* LW */
                  s->regs[rd] = mem_read32(s, addr);
              s->pc += 4; } break;

        case 0x23: /* Stores */
            { uint32_t addr = s->regs[rs1] + imm_S(instr);
              if (funct3 == 0x2) /* SW */
                  mem_write32(s, addr, s->regs[rs2]);
              s->pc += 4; } break;

        case 0x63: /* Branches */
            { int32_t offset = imm_B(instr);
              int taken = 0;
              if (funct3 == 0x0) taken = (s->regs[rs1] == s->regs[rs2]); /* BEQ */
              if (funct3 == 0x1) taken = (s->regs[rs1] != s->regs[rs2]); /* BNE */
              s->pc += taken ? offset : 4; } break;

        case 0x6F: /* JAL */
            { int32_t offset = imm_J(instr);
              s->regs[rd] = s->pc + 4;
              s->pc += offset; } break;

        default:
            fprintf(stderr, "Unknown opcode 0x%02x at PC 0x%08x\n", opcode, s->pc);
            exit(1);
    }
    s->regs[0] = 0; /* x0 always zero */
}
```

## Testing the Simulator

Write a small assembly test that loads two values, adds them, and stores the result:

```asm
# test.s
    li   a0, 10        # addi a0, zero, 10
    li   a1, 20        # addi a1, zero, 20
    add  a2, a0, a1    # a2 = 30
    sw   a2, 0(sp)     # store result
    ebreak             # halt
```

Assemble with the RISC-V toolchain:

```bash
riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -nostdlib -o test.elf test.s
riscv64-unknown-elf-objcopy -O binary test.elf test.bin
```

Load `test.bin` into `s.mem` at the reset address, set `s.pc = 0x0`, and step through the simulator.

## Common Pitfalls

- **Sign extension errors** on immediate fields are the #1 bug. Always sign-extend before adding to a base address.
- **Endianness**: RISC-V is little-endian. Ensure `mem_read32` assembles bytes in the correct order.
- **x0 write protection**: forgetting to zero `regs[0]` after writes produces subtle bugs in branches that compare against x0.

## Interview Answer

> "A minimal RV32I simulator needs architectural state (32 registers + PC + memory), a decode step that extracts fields using bitmask shifts, and an execute switch on opcode/funct3/funct7. The trickiest part is correctly sign-extending the six different immediate encodings."
