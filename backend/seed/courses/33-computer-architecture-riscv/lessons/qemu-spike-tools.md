# Tools of the Trade: QEMU, Spike, gem5

Three open-source simulators appear in virtually every RISC-V and computer architecture job description: **QEMU**, **Spike**, and **gem5**. Each serves a distinct role. Knowing when to reach for each one — and what its limitations are — is a reliable interview differentiator.

## QEMU

QEMU (Quick EMUlator) is a full-system emulator that translates guest instructions to host instructions using **just-in-time (JIT) binary translation** via its Tiny Code Generator (TCG).

- Supports dozens of architectures: x86, ARM, RISC-V, MIPS, PowerPC, and more.
- Can run a full Linux kernel with devices (virtio block, network, serial).
- Runs at 10-100 MIPS — fast enough to boot a desktop Linux in seconds.

```bash
# Boot a RISC-V Linux image with QEMU
qemu-system-riscv64 \
  -machine virt \
  -cpu rv64 \
  -m 512M \
  -kernel Image \
  -drive file=rootfs.img,format=raw,id=hd0 \
  -device virtio-blk-device,drive=hd0 \
  -append "root=/dev/vda rw console=ttyS0" \
  -nographic
```

### Key QEMU features for architects

- **GDB stub** (`-s -S` flags): attach GDB to the guest at any point.
- **Plugin API**: instrument every instruction without modifying QEMU source.
- **TCG IR**: trace the translation to understand what the JIT emits.
- No cycle accuracy — QEMU does not model pipeline timing.

## Spike

Spike is the official RISC-V ISA reference simulator maintained by the RISC-V Foundation (UC Berkeley). It is the gold-standard functional model: if Spike accepts a program, the behaviour is spec-compliant.

- Written in C++, clean and readable — good learning resource.
- Supports RV32I, RV64I, and all standard extensions (M, A, F, D, C, V, Zicsr, …).
- Ships with **pk** (proxy kernel): a thin layer that proxies syscalls to the host OS so bare-metal ELF binaries can run without a full OS.

```bash
# Run a RISC-V ELF with Spike + proxy kernel
spike pk hello.elf

# Interactive debug: step through instructions
spike -d pk hello.elf
# (gdb) until pc 0 0x80000100
# (gdb) reg 0 a0
```

### Spike interactive debugger commands

| Command | Effect |
|---|---|
| `r <n>` | Run n instructions |
| `pc 0` | Print current PC of hart 0 |
| `reg 0 <name>` | Print register value |
| `mem <addr>` | Print memory word |
| `until pc 0 <addr>` | Run until PC reaches address |

Spike is not cycle-accurate, but it supports a `--log-commits` flag that logs every register write — invaluable for generating golden reference traces.

## gem5

gem5 is the dominant open-source **cycle-accurate** simulator in academia and industry. It models the full micro-architecture: pipeline stages, caches, branch predictors, memory controllers, and DRAM.

- Supports x86, ARM, RISC-V (in-order and out-of-order CPU models).
- Written in C++ with a Python configuration layer.
- **SE mode** (syscall emulation): runs ELF binaries without a kernel.
- **FS mode** (full system): runs a real OS with device models.

```python
# gem5 config snippet — RISC-V O3 CPU with 32 KB L1 cache
from m5.objects import *

system = System()
system.cpu = DerivO3CPU()
system.cpu.icache = Cache(size='32kB', assoc=8)
system.cpu.dcache = Cache(size='32kB', assoc=8)
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_8x8()
```

### gem5 use cases

- Measuring IPC, CPI, cache miss rates for a workload.
- Comparing micro-architecture configurations (cache sizes, issue width, branch predictor).
- Checkpoint/restore: fast-forward with AtomicSimpleCPU, then switch to O3 for detailed simulation.

## Comparison Summary

| Tool | Type | Speed | Accuracy | Best use |
|---|---|---|---|---|
| QEMU | Functional (JIT) | 10-100 MIPS | ISA only | Full OS boot, driver dev |
| Spike | Functional (interpreter) | 1-10 MIPS | ISA (gold ref) | Compliance testing, traces |
| gem5 | Cycle-accurate | 0.1-5 MIPS | Micro-arch | Perf analysis, arch research |

## Common Pitfall

Do not use gem5 for initial software bringup — booting Linux in full O3 mode takes hours. The correct flow: boot with QEMU, develop software, run regression with Spike, analyse performance with gem5.

## Interview Answer

> "QEMU is a fast full-system emulator for OS and driver development. Spike is the official RISC-V ISA reference simulator used for compliance and golden traces. gem5 is a cycle-accurate simulator for micro-architecture exploration and performance analysis. All three are used together in a typical SoC development flow."
