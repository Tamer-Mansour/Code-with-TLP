# Cross-Compilation for Embedded Targets

In virtual prototyping, you work with two distinct machines. The **host** is the powerful workstation where you develop — typically x86-64 Linux. The **target** is the embedded system being modelled — perhaps an ARM Cortex-A or RISC-V core. Cross-compilation means running the compiler on the host to produce binaries that execute on the target.

## Why Cross-Compile?

Embedded targets often have:

- Limited RAM and CPU — compiling natively is impractically slow.
- No operating system or disk — cannot host a compiler at all.
- A different instruction set architecture (ISA) — the host's native compiler produces the wrong machine code.

## Toolchain Naming Convention

A cross-compiler is identified by a **target triplet**: `arch-vendor-os-abi`.

| Example triplet | Meaning |
|-----------------|---------|
| `arm-none-eabi` | ARM, bare metal (no OS), EABI calling convention |
| `aarch64-linux-gnu` | 64-bit ARM, Linux with glibc |
| `riscv32-unknown-elf` | RISC-V 32-bit, unknown vendor, bare-metal ELF |
| `x86_64-linux-gnu` | Native x86-64 Linux (the host itself) |

The compiler binary is prefixed with the triplet:

```bash
arm-none-eabi-gcc   --version
arm-none-eabi-g++   --version
arm-none-eabi-objcopy
arm-none-eabi-nm
```

## A Cross-Compilation Workflow

```bash
# 1. Install the cross-toolchain
sudo apt install gcc-arm-none-eabi g++-arm-none-eabi

# 2. Compile firmware for ARM Cortex-M4
arm-none-eabi-g++ \
    -mcpu=cortex-m4 \
    -mthumb \
    -mfpu=fpv4-sp-d16 \
    -mfloat-abi=hard \
    -O2 -std=c++17 \
    -c firmware.cpp -o firmware.o

# 3. Link
arm-none-eabi-g++ \
    -mcpu=cortex-m4 -mthumb \
    -T linker_script.ld \
    firmware.o startup.o \
    -o firmware.elf

# 4. Convert to raw binary or Intel HEX for flashing
arm-none-eabi-objcopy -O binary firmware.elf firmware.bin
arm-none-eabi-objcopy -O ihex  firmware.elf firmware.hex
```

## Makefile for Cross-Compilation

```makefile
CROSS   := arm-none-eabi-
CC      := $(CROSS)gcc
CXX     := $(CROSS)g++
OBJCOPY := $(CROSS)objcopy

ARCH_FLAGS := -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard
CXXFLAGS   := $(ARCH_FLAGS) -O2 -std=c++17 -Wall

all: firmware.bin

firmware.elf: main.o hal.o
	$(CXX) $(ARCH_FLAGS) -T link.ld $^ -o $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

.PHONY: clean
clean:
	rm -f *.o *.elf *.bin
```

The `CROSS` prefix variable makes it trivial to switch between native and cross builds: override it at the command line with `make CROSS=riscv32-unknown-elf-`.

## Sysroot and Standard Library

For Linux-target cross-compilation, the compiler needs the target's system headers and C library. The `--sysroot` flag points to a staging area containing them:

```bash
aarch64-linux-gnu-g++ \
    --sysroot=/opt/arm64-sysroot \
    -I/opt/arm64-sysroot/usr/include \
    main.cpp -o main.elf
```

Bare-metal targets use a reduced library (`newlib` or `picolibc`) or no standard library at all (`-nostdlib`).

## Inspecting the Output

Always verify the target architecture of the compiled binary:

```bash
file firmware.elf
# firmware.elf: ELF 32-bit LSB executable, ARM, EABI5 version 1 ...

arm-none-eabi-readelf -h firmware.elf | grep Machine
# Machine: ARM
```

## Running on a Virtual Platform

A SystemC VP running on the x86 host can load and execute the cross-compiled binary through an **instruction set simulator (ISS)** model. The host compiles the VP with the host toolchain; the firmware binary is a data file loaded at runtime by the ISS model.

## Common Pitfalls

- **Mixing host and target object files** — produces linker errors about incompatible architectures.
- **Forgetting `-mthumb`** — Cortex-M cores only support Thumb instructions; omitting this flag generates incompatible ARM instructions.
- **Using host's `ar` / `nm`** — always prefix utility tools with the cross-triplet.

## Interview Answer

> "Cross-compilation means using a toolchain on the host machine that targets a different ISA. You prefix all tools with the target triplet (e.g., `arm-none-eabi-g++`) and pass architecture flags like `-mcpu=cortex-m4`. The resulting ELF runs on the target, not the host."
