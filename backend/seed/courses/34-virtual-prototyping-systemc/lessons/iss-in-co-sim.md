# Instruction-Set Simulators in Co-Simulation

An Instruction-Set Simulator (ISS) is the component that executes target software within a co-simulation. It is the bridge between the software domain (compiled binary) and the hardware domain (SystemC/TLM peripheral models). Understanding how an ISS works — and how to connect it to the rest of the platform — is essential for virtual prototyping.

## What an ISS Does

An ISS replicates the observable behaviour of a target processor:

1. **Fetch** — Read bytes from the target's memory at the program counter (PC).
2. **Decode** — Interpret the bytes as an instruction according to the target ISA.
3. **Execute** — Update registers, memory, or flags according to the instruction semantics.
4. **Advance** — Move the PC to the next instruction and advance simulated time.

```cpp
// Simplified ISS loop (interpretive)
void Iss::run() {
    while (!halted) {
        uint32_t raw = mem->read32(pc);
        Instruction insn = decode(raw);
        execute(insn);
        pc = compute_next_pc(insn);
        sim_time += insn.cycle_cost();
        if (pending_irq()) handle_interrupt();
    }
}
```

## Anatomy of a TLM-Connected ISS

The ISS sits between the simulation kernel and the rest of the platform:

```
SystemC simulation kernel
         |
    +----+----+
    |   ISS   |  <-- SC_THREAD, runs target binary
    |  module |
    +----+----+
         | initiator TLM socket
    +----+----+
    | Router  |  address decoder
    +--+--+---+
       |  |
  RAM  | UART (peripheral model)
  model|
```

- The ISS is an `sc_module` with an `SC_THREAD` process.
- It holds an initiator `tlm_initiator_socket<>` for all memory and MMIO accesses.
- Every `LDR`/`STR` instruction becomes a `b_transport()` call on that socket.

## Connecting ISS to TLM Sockets

```cpp
// ISS SystemC module declaration
SC_MODULE(Cortex_M4_ISS) {
    tlm_utils::simple_initiator_socket<Cortex_M4_ISS> bus_socket;

    void mem_read(uint64_t addr, uint8_t* buf, unsigned size) {
        tlm::tlm_generic_payload t;
        sc_core::sc_time delay = SC_ZERO_TIME;
        t.set_command(tlm::TLM_READ_COMMAND);
        t.set_address(addr);
        t.set_data_ptr(buf);
        t.set_data_length(size);
        bus_socket->b_transport(t, delay);
        wait(delay);
    }
    // ... similarly for mem_write
};
```

## Types of ISSes Used in Practice

| ISS type | Examples | Simulation speed | Accuracy |
|---|---|---|---|
| Interpretive | gem5, custom | 50–200 MIPS | Very high |
| JIT (block-level) | QEMU, Fast Models | 500–2000 MIPS | High |
| Native / hypervisor | Imperas OVP, Virtualizer | Up to native speed | ISA-level |
| Cycle-accurate ISS | gem5 O3, MARSS | 1–10 MIPS | Micro-arch level |

## Interrupt Handling

Interrupt delivery from a peripheral to the ISS requires a SystemC signal:

```cpp
// Peripheral raises interrupt
irq_out.write(true);

// ISS checks the signal at quantum boundaries
void Iss::check_irq() {
    if (irq_in.read() && cpu_irq_enabled()) {
        push_context();
        pc = irq_vector_table[irq_number];
    }
}
```

The interrupt signal must be connected with `sc_signal<bool>` so the SystemC delta-cycle mechanism propagates the change correctly.

## ISS Debug Interface

Most ISSes expose a GDB Remote Serial Protocol (RSP) server. Connecting GDB to it gives full source-level debug of target firmware:

```bash
# Terminal 1: start simulation with GDB stub on port 1234
./virtual_platform --gdb-port 1234 --firmware app.elf

# Terminal 2: connect GDB (arm-none-eabi-gdb)
(gdb) target remote :1234
(gdb) break main
(gdb) continue
```

Breakpoints, watchpoints, and step-into all work across the virtual hardware — you see peripheral register values changing in real time as you step through firmware.

## Common Pitfalls

- **Missing wait() after b_transport** — If the ISS does not call `wait(delay)` after a blocking transport call, simulation time never advances, causing an infinite-loop hang.
- **Incorrect ISR vector table** — If the ISS reads the vector table from the wrong base address, interrupts jump to garbage — a common bring-up failure.
- **Quantum too large** — A 1 ms quantum means the ISS will not check for interrupts more than 1000 times per simulated second. For a 1 ms timer interrupt, this is borderline; for a 10 µs interrupt, it fails.

## Interview Answer

> "An ISS is a SystemC module with an initiator TLM socket. It fetches, decodes, and executes target instructions in a `SC_THREAD`, converting every memory and MMIO access into a `b_transport()` call on its bus socket. Peripheral models respond to those transactions, and interrupt signals from peripherals flow back to the ISS via `sc_signal<bool>` connections."
