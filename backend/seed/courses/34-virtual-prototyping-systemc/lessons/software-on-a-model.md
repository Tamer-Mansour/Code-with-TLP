# Running Real Software on a Hardware Model

"Real software" means an unmodified compiled binary — the same ELF file you would flash onto real silicon. No source changes, no stubs, no simulatable version of the driver. Getting that binary to execute correctly on a virtual platform requires solving a chain of problems that span ISA fidelity, memory mapping, and peripheral timing.

## Loading the Binary

The simulation host reads the ELF file, extracts loadable segments, and places them into the virtual memory model at the correct virtual addresses. A small loader function (often a SystemC `before_end_of_elaboration` hook) does this before `sc_start()`.

```cpp
void load_elf(const std::string& path, Memory& mem) {
    // Open ELF, iterate PT_LOAD segments
    for (auto& seg : elf.segments()) {
        mem.write(seg.vaddr(), seg.data(), seg.filesz());
        mem.zero(seg.vaddr() + seg.filesz(),
                 seg.memsz() - seg.filesz()); // BSS
    }
    cpu.set_pc(elf.entry());
}
```

## The Execution Loop

The ISS fetch-decode-execute loop is the heart of SW execution on the model:

```
while (running) {
    uint32_t insn = mem_fetch(pc);
    decode(insn, &op);
    execute(&op, &regs);
    pc = next_pc(op, regs);
    check_interrupts();
    advance_simulation_time(cycle_cost);
}
```

Each memory access — including instruction fetch — goes through the virtual memory map. Accesses to RAM return data. Accesses to MMIO ranges are forwarded to the corresponding SystemC peripheral module via a TLM `b_transport()` call.

## Memory Map Fidelity

The virtual platform must replicate the chip's memory map exactly. A typical ARM Cortex-M system:

| Region | Base address | Model backing |
|---|---|---|
| Flash (code) | `0x0000_0000` | Read-only memory model |
| SRAM | `0x2000_0000` | Read-write memory model |
| Peripheral A | `0x4000_0000` | SystemC peripheral |
| SysTick | `0xE000_E010` | Cortex-M internal timer |

Any address not backed by a model should return a bus error — exactly as real silicon would.

## Handling Peripherals from SW

When the firmware writes to a UART transmit register:

1. The ISS executes a `STR` instruction targeting `0x40013804`.
2. The router forwards the TLM transaction to the UART model.
3. The UART model extracts the byte, prints it to the host console, and schedules a TX-complete interrupt after a simulated baud-rate delay.
4. When the ISS next calls `check_interrupts()`, it vectors to the ISR.

This round-trip is invisible to the firmware — it is identical to what happens on real hardware.

## Worked Example: Bare-Metal "Hello World"

```c
// hello.c — compiled for target ARM, no OS
#define UART_DR  (*(volatile uint32_t*)0x40013800)
#define UART_SR  (*(volatile uint32_t*)0x40013804)

void uart_putc(char c) {
    while (!(UART_SR & 0x80)) {}  // wait TX ready
    UART_DR = c;
}

int main(void) {
    const char* s = "Hello, virtual world!\n";
    while (*s) uart_putc(*s++);
    return 0;
}
```

In the virtual platform the UART model's `b_transport` handles reads of `UART_SR` (always returns `0x80` — ready) and writes to `UART_DR` (prints the character). The firmware never knows it is not running on silicon.

## Common Pitfalls

- **Stack pointer initialisation** — Cortex-M cores load SP from the vector table at address `0x0000_0000`. If the loader misses this, the first stack operation corrupts memory.
- **Cache coherency** — If the model includes a cache, the ISS must flush it when DMA writes to DRAM; otherwise SW reads stale data.
- **Semihosting** — Some toolchains emit semihosting traps (`BKPT 0xAB`). The ISS must handle these or the binary halts silently.

## Interview Answer

> "You compile the target binary as normal, then a loader places its ELF segments into a virtual memory model. The ISS runs the binary's instructions natively; any MMIO access is intercepted and forwarded to the corresponding SystemC peripheral via TLM transactions, making the firmware experience identical to real hardware."
