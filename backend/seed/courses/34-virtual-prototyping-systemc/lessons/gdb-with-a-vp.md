# Attaching gdb to a Virtual Prototype

One of the biggest advantages of a virtual prototype over real hardware is that you can attach a full-featured debugger to the guest CPU without any JTAG probe, without halting production code, and without modifying the target binary. This lesson covers how the connection works and how to use it effectively.

## How the Connection Works

A virtual prototype exposes a **GDB Remote Serial Protocol (RSP)** server. The ISS (Instruction-Set Simulator) implements a tiny stub that listens on a TCP port. When gdb connects, it sends RSP packets to read/write registers and memory and to set breakpoints. The ISS translates those packets into internal simulator operations.

```
+----------+      TCP (default :1234)     +----------------------+
|   gdb    |  <-------------------------> | VP / ISS (RSP stub)  |
|  (host)  |      GDB Remote Protocol     | (simulated CPU)      |
+----------+                              +----------------------+
```

The guest binary runs inside the ISS; the host gdb is compiled for the **target architecture** (e.g., `arm-none-eabi-gdb`, `riscv64-unknown-elf-gdb`).

## Starting the VP and Attaching

**Step 1 — Launch the VP with RSP enabled** (exact flags depend on your platform, but the pattern is universal):

```bash
# QEMU-style VP
./my_vp --cpu cortex-a53 --rsp-port 1234 --freeze-on-start &

# gem5-style
./build/ARM/gem5.opt configs/example/se.py \
    --cpu-type=TimingSimpleCPU \
    --remote-gdb-port=7000 \
    -c ./hello.elf
```

The `--freeze-on-start` flag (or equivalent) halts the CPU immediately so gdb can set breakpoints before the first instruction executes.

**Step 2 — Launch the cross gdb:**

```bash
arm-none-eabi-gdb ./hello.elf
```

**Step 3 — Connect and start:**

```
(gdb) target remote localhost:1234
Remote debugging using localhost:1234
0x00000000 in ?? ()
(gdb) load          # optional: re-flash ELF into simulated RAM
(gdb) break main
Breakpoint 1 at 0x10054: file main.c, line 12.
(gdb) continue
```

## Useful gdb Commands in a VP Context

| Command | What it does |
|---|---|
| `info registers` | Dump all CPU registers |
| `x/10i $pc` | Disassemble 10 instructions at PC |
| `x/4wx 0x40010000` | Hex dump peripheral register block |
| `watch *0x40010000` | Watchpoint on peripheral register |
| `set scheduler-locking on` | Prevent other threads from running while stepping |
| `maintenance packet m40000000,4` | Raw RSP memory read |

## Setting Watchpoints on MMIO

MMIO watchpoints are especially useful in a VP because they catch the exact instruction that reads or writes a peripheral register — something impossible with JTAG on most hardware:

```
(gdb) watch *((volatile uint32_t *)0x40010004)
Hardware watchpoint 2: *((volatile uint32_t *)0x40010004)
(gdb) continue
Hardware watchpoint 2: *((volatile uint32_t *)0x40010004)
Old value = 0
New value = 1
uart_init () at uart.c:34
34    UART->CR1 |= UART_CR1_UE;
```

## Common Pitfalls

- **Architecture mismatch.** Using an x86 gdb to debug an ARM binary gives garbage output. Always use the cross-compiled gdb that matches the ISS target.
- **Missing debug symbols.** If the ELF was built with `-O2` and no `-g`, gdb can still set breakpoints by address, but source-level stepping is lost. Always keep a debug build handy.
- **Forgetting `load`** when the VP does not auto-load the ELF on attach. Registers will show correct addresses, but RAM will be zeroed.
- **Simulation running while exploring.** Use `monitor stop` or `Ctrl-C` in gdb to pause the VP before examining state.

> **Interview answer:** "I launch the virtual prototype with an RSP server on a TCP port, then attach the target-architecture gdb with `target remote`. This gives full source-level debugging — breakpoints, watchpoints, register inspection — without any physical hardware."
