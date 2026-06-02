# How Modern x86 Decodes CISC to Micro-Ops

Modern Intel and AMD processors execute x86 instructions, but internally they operate almost nothing like the CISC ISA suggests. Beneath the CISC surface lies a RISC-style execution engine. The translation layer between them is one of the most consequential engineering decisions in processor history.

## The Problem: CISC Meets Modern Pipelines

A deep, out-of-order pipeline needs:

- Instructions of predictable, bounded length so the scheduler can issue many simultaneously.
- Operations whose inputs and outputs are fully visible — no hidden implicit state.
- Operations that complete in a small, predictable number of cycles.

x86 instructions satisfy none of these requirements reliably. `REP MOVSB` can copy gigabytes of memory. `FNSAVE` saves 108 bytes of FPU state. Even `PUSH EAX` implicitly modifies two resources: the stack pointer (`RSP`) and memory. A modern out-of-order engine cannot schedule around these hidden dependencies without first breaking them apart.

## Micro-Operations (Micro-Ops / µops)

The solution is to translate each x86 instruction into one or more **micro-ops** (µops) — RISC-like internal operations with explicit operands and bounded latency.

```
x86 instruction:   PUSH  RAX
Decoded µops:
    SUB  RSP, 8            # adjust stack pointer
    STORE [RSP], RAX       # write value to new stack top
```

```
x86 instruction:   ADD  [RBX+8], RCX
Decoded µops:
    LOAD  tmp, [RBX+8]     # read memory operand
    ADD   tmp, tmp, RCX    # integer add
    STORE [RBX+8], tmp     # write result back
```

A single "simple" x86 instruction can decompose into 1-3 µops for common cases, or dozens of µops for complex instructions like `ENTER` or `CPUID`.

## The Front-End: Where CISC Lives

The processor front-end handles the x86 ISA:

```
Instruction Cache (I-cache)
        |
Fetch (16-32 bytes per cycle)
        |
Pre-decode (find instruction boundaries — the hard part)
        |
Instruction Queue
        |
Decode (up to 4-6 decoders in parallel on modern Intel)
        |
Micro-Op Queue / Loop Stream Detector
        |
  --> Back-End (execution engine)
```

The **pre-decode** step is where x86's variable-length encoding creates the most pain. Finding where instruction N+1 begins requires knowing the length of instruction N, which requires examining its prefix bytes, opcode byte(s), ModRM, SIB, and displacement fields. This is inherently serial and limits fetch throughput.

## The Decoded ICache (µop Cache)

Intel's Sandy Bridge (2011) introduced the **Decoded Instruction Cache** (also called the µop cache or "LSD" — Loop Stream Detector buffer). Instead of re-decoding hot x86 instructions on every fetch cycle, decoded µops are cached:

- Capacity: ~1,500 µops (Intel Skylake and later)
- Bandwidth: up to 6 µops/cycle from the µop cache vs. 4-5 µops/cycle from the legacy decoder
- Power savings: the complex x86 decoder is bypassed on cache hits

```
Hot loop execution path:
  µop Cache hit → Allocate → Execute
  (bypasses: fetch, pre-decode, x86 decode)
```

This is why modern x86 processors are so fast on loop-heavy code: the CISC decode overhead is paid only once.

## Register Renaming and the Back-End

Once in µop form, the back-end applies **register renaming** — replacing the x86's 16 visible general-purpose registers with a much larger physical register file (e.g., 180+ entries in Intel Skylake). This eliminates false dependencies (write-after-write, write-after-read hazards) and enables wide out-of-order execution.

| x86 Register | Physical Register File Entry |
|---|---|
| RAX (write) | Phys Reg 47 (renamed) |
| RAX (next write) | Phys Reg 83 (renamed again) |

The µop scheduler sees no false dependencies and can issue µops from different x86 instructions in parallel, even if they appear to write the same register.

## Cost of the Translation Layer

The CISC front-end imposes real costs:

- **Die area:** The x86 decoder and µop cache occupy significant chip area.
- **Power:** Pre-decode and decode consume power even when µops are cached.
- **Latency:** The decode pipeline adds several cycles between fetch and first execution.
- **Verification burden:** Correctness of the translator must be verified for every instruction in a 3,000+ instruction ISA.

Apple Silicon (M-series, ARM ISA) and AWS Graviton (ARM) avoid this cost entirely — their simpler front-ends leave more budget for execution units and cache.

## Why x86 Gets Away With It

At high clock frequencies and large out-of-order windows (e.g., 512-entry reorder buffer in Intel Raptor Lake), the back-end execution dominates total runtime. The front-end overhead becomes a second-order effect on most workloads. This is why Intel and AMD compete effectively against ARM on server benchmarks despite the translation overhead.

**Interview answer:** Modern x86 processors translate CISC instructions into RISC-like micro-ops in the front-end, enabling a simple, wide out-of-order execution back-end; a µop cache bypasses the expensive x86 decoder on hot loops, mitigating the performance cost of variable-length CISC decoding.
