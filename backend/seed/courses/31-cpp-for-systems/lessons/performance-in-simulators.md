# Performance Techniques in Instruction Simulators

A naive interpreter loop runs at roughly 100–200 MIPS on modern hardware. Real firmware boot flows can require simulating billions of instructions. This lesson covers the techniques that push VPs from "slow prototype" to "production tool."

## Baseline: The Interpreter Bottleneck

The bottleneck in a pure interpreter is the **dispatch overhead** — the switch, the field extractions, and the indirect function call per instruction. Profiling typically reveals 60–70 % of time spent in the fetch-decode-dispatch path, not in the actual computation.

Measure first:

```bash
perf stat -e instructions,cycles,cache-misses ./my_isss benchmark.elf
```

## Technique 1: Computed Goto (Threaded Dispatch)

Replace the central `switch` with GCC's `&&label` extension to jump directly from handler to handler:

```cpp
// Not standard C++, but supported by GCC and Clang
static void* dispatch_table[128] = {
    [0x33] = &&op_alu_r,
    [0x13] = &&op_alu_i,
    // ...
};

#define NEXT  goto *dispatch_table[mem_.load32(pc_) & 0x7F]

NEXT;   // start
op_alu_r: { exec_r(...); pc_ += 4; NEXT; }
op_alu_i: { exec_i(...); pc_ += 4; NEXT; }
```

This eliminates the branch prediction miss that plagues a central switch.

## Technique 2: Direct-Mapped Translation Cache (Basic Block Cache)

Pre-decode each instruction once and cache the decoded representation:

```cpp
struct DecodedInsn {
    uint8_t  opcode_class;   // enum
    uint8_t  rd, rs1, rs2, funct3, funct7;
    int32_t  imm;
};

std::unordered_map<uint32_t, DecodedInsn> decode_cache_;

const DecodedInsn& fetch_decoded(uint32_t pc) {
    auto it = decode_cache_.find(pc);
    if (it != decode_cache_.end()) return it->second;
    return decode_cache_[pc] = decode(mem_.load32(pc));
}
```

This cuts decode cost to near zero after the first pass through a loop.

## Technique 3: JIT Compilation (Just-in-Time)

The gold standard for performance: translate guest basic blocks into host machine code at runtime. Libraries like **AsmJit** or **LLVM MCJIT** provide the infrastructure:

```
Guest RISC-V block -> IR -> Host x86-64 machine code -> execute directly
```

A JIT can achieve 1–5 Giga-instructions per second (GIPS), roughly 10–50x faster than an interpreter. The cost is implementation complexity: you must handle self-modifying code by invalidating translated blocks.

## Technique 4: Memory Access Optimisation

Each `bus_.read32()` call traverses the region list. Replace it with a **Software TLB** (a flat array of host pointers indexed by page number):

```cpp
uint8_t* host_page_[4096] = {};   // guest 4K pages -> host pointer

uint32_t fast_load32(uint32_t addr) {
    uint8_t* page = host_page_[addr >> 12];
    if (page) {
        uint32_t v; std::memcpy(&v, page + (addr & 0xFFF), 4); return v;
    }
    return bus_.read32(addr);   // slow path for MMIO
}
```

RAM lookups become two loads + a `memcpy`; MMIO still goes through the device model.

## Technique 5: Reducing Host Memory Footprint

Simulating gigabytes of guest RAM is impractical. Use a **sparse memory map** — a hash map of page-sized chunks allocated on demand:

```cpp
std::unordered_map<uint32_t, std::array<uint8_t,4096>> pages_;

uint8_t* get_page(uint32_t addr) {
    return pages_[addr >> 12].data();
}
```

## Performance Summary

| Technique | Typical speedup | Complexity |
|---|---|---|
| Baseline switch interpreter | 1x (baseline) | Low |
| Computed goto | 1.5–2x | Low |
| Decode cache | 2–4x | Low |
| Software TLB | 2–3x (memory bound) | Medium |
| JIT compilation | 10–50x | High |

## Interview Answer

> **Interview answer:** "I start with a clean interpreter and profile first. Common wins are: a decode cache to avoid re-decoding hot loops, a software TLB for fast RAM access while keeping MMIO on the slow bus path, and computed-goto dispatch to reduce branch-prediction misses. JIT is the ceiling but adds significant complexity and is justified only when simulation speed is a hard product requirement."
