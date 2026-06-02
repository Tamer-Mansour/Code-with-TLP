# From Decode to a Tiny Instruction-Set Simulator

An Instruction-Set Simulator (ISS) is the software equivalent of a CPU. It fetches instructions from a memory model, decodes each 32-bit word, updates a register file, and advances the program counter. This lesson assembles the decode knowledge from this module into a minimal but complete RV32I ISS skeleton.

## The Fetch-Decode-Execute Loop

Every ISS, from a 50-line script to a cycle-accurate pipeline model, is a variation of:

```python
while True:
    instr = memory.read32(pc)   # 1. Fetch
    decoded = decode(instr)     # 2. Decode
    pc = execute(decoded, pc)   # 3. Execute (returns next PC)
```

In a virtual prototype this loop is a SystemC thread or a simple C++ `while` loop. For an RV32I functional model, millions of iterations per second are achievable.

## Minimal C++ ISS Structure

```cpp
#include <cstdint>
#include <array>
#include <stdexcept>

struct RV32ISS {
    std::array<uint32_t, 32> x{};  // register file, x[0] always 0
    uint32_t pc = 0;
    uint8_t  mem[1 << 20]{};       // 1 MB flat memory

    // Helper: read 32-bit little-endian word
    uint32_t fetch() {
        uint32_t w = mem[pc] | (mem[pc+1]<<8) | (mem[pc+2]<<16) | (mem[pc+3]<<24);
        return w;
    }

    void write_rd(int rd, uint32_t v) { if (rd) x[rd] = v; }

    // Sign-extend a value from 'bits' width to 32 bits
    static int32_t sext(uint32_t v, int bits) {
        uint32_t sign = 1u << (bits - 1);
        return (v & sign) ? (int32_t)(v | (~0u << bits)) : (int32_t)v;
    }

    void step() {
        uint32_t ir     = fetch();
        uint32_t opcode = ir & 0x7F;
        int      rd     = (ir >>  7) & 0x1F;
        int      funct3 = (ir >> 12) & 0x07;
        int      rs1    = (ir >> 15) & 0x1F;
        int      rs2    = (ir >> 20) & 0x1F;
        int32_t  imm_i  = sext(ir >> 20, 12);
        int32_t  imm_s  = sext(((ir>>25)<<5)|(ir>>7&0x1F), 12);
        int32_t  imm_b  = sext(((ir>>31)<<12)|((ir>>7&1)<<11)|
                               ((ir>>25&0x3F)<<5)|((ir>>8&0xF)<<1), 13);
        int32_t  imm_u  = (int32_t)(ir & 0xFFFFF000u);
        int32_t  imm_j  = sext(((ir>>31)<<20)|((ir>>12&0xFF)<<12)|
                               ((ir>>20&1)<<11)|((ir>>21&0x3FF)<<1), 21);

        switch (opcode) {
          case 0x33: { // R-type ALU
            uint32_t f7 = ir >> 25;
            uint32_t a = x[rs1], b = x[rs2];
            uint32_t res = 0;
            if      (funct3==0 && f7==0)  res = a + b;         // ADD
            else if (funct3==0 && f7==32) res = a - b;         // SUB
            else if (funct3==7 && f7==0)  res = a & b;         // AND
            else if (funct3==6 && f7==0)  res = a | b;         // OR
            else if (funct3==4 && f7==0)  res = a ^ b;         // XOR
            else if (funct3==1 && f7==0)  res = a << (b&31);   // SLL
            else if (funct3==5 && f7==0)  res = a >> (b&31);   // SRL
            else if (funct3==5 && f7==32) res = (int32_t)a >> (b&31); // SRA
            write_rd(rd, res);
            pc += 4; break;
          }
          case 0x13: { // I-type ALU
            uint32_t a = x[rs1];
            uint32_t res = 0;
            if      (funct3==0) res = a + imm_i;           // ADDI
            else if (funct3==4) res = a ^ imm_i;           // XORI
            else if (funct3==6) res = a | imm_i;           // ORI
            else if (funct3==7) res = a & imm_i;           // ANDI
            write_rd(rd, res);
            pc += 4; break;
          }
          case 0x03: { // Load
            uint32_t addr = x[rs1] + imm_i;
            // (simplified: real code reads mem[addr] safely)
            pc += 4; break;
          }
          case 0x23: { // Store
            uint32_t addr = x[rs1] + imm_s;
            // mem write omitted for brevity
            pc += 4; break;
          }
          case 0x63: { // Branch
            bool taken = false;
            if      (funct3==0) taken = x[rs1] == x[rs2];                          // BEQ
            else if (funct3==1) taken = x[rs1] != x[rs2];                          // BNE
            else if (funct3==4) taken = (int32_t)x[rs1] <  (int32_t)x[rs2];       // BLT
            else if (funct3==5) taken = (int32_t)x[rs1] >= (int32_t)x[rs2];       // BGE
            pc = taken ? (pc + imm_b) : (pc + 4); break;
          }
          case 0x37: write_rd(rd, imm_u); pc+=4; break;           // LUI
          case 0x17: write_rd(rd, pc+imm_u); pc+=4; break;        // AUIPC
          case 0x6F: write_rd(rd, pc+4); pc+=imm_j; break;        // JAL
          case 0x67: write_rd(rd, pc+4); pc=(x[rs1]+imm_i)&~1u; break; // JALR
          default:
            throw std::runtime_error("Illegal instruction");
        }
    }
};
```

## Integrating with SystemC/TLM

In a VP context, the `fetch()` call becomes a TLM `b_transport` call through an initiator socket to a memory model. The rest of the loop is identical.

```cpp
// In a SystemC module:
void cpu_thread() {
    while (true) {
        tlm::tlm_generic_payload trans;
        sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
        uint32_t data;
        trans.set_command(tlm::TLM_READ_COMMAND);
        trans.set_address(pc);
        trans.set_data_ptr((unsigned char*)&data);
        trans.set_data_length(4);
        initiator_socket->b_transport(trans, delay);
        // decode and execute data...
    }
}
```

## Testing Your ISS

1. **Assemble a small program** with `riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -nostdlib`.
2. **Load the ELF** into your memory model.
3. **Run** and compare register values against Spike (`spike --isa=rv32i`), the official RISC-V ISA simulator.
4. **Add a trap handler** for illegal instructions to catch missing extension support early.

> **Interview answer:** "A RISC-V ISS is a fetch-decode-execute loop. Decode extracts opcode, register indices, and a sign-extended immediate using bit masks. Execute dispatches on opcode+funct3+funct7, updates the register file, and computes the next PC. Integrating with SystemC/TLM replaces the raw memory reads with b_transport calls."

## Key Takeaways

- The decode step is a set of cheap bit-mask operations — this is intentional in RISC-V's design.
- Always zero writes to x0 after execution.
- For branches, the condition check uses signed or unsigned comparison as specified by funct3.
- A working ISS for RV32I base integer can be under 200 lines of C++.
