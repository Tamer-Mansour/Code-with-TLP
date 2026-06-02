# Modeling the Fetch-Execute Loop

The fetch-execute loop is the innermost engine of every ISS. It is deceptively simple in description and surprisingly subtle in implementation. Writing a correct loop — one that handles timing, exceptions, interrupts, and debug correctly — is the bulk of building a CPU model from scratch.

## The Canonical Loop Structure

```cpp
void RISCVCPU::run_thread() {
    while (!halted) {
        // 1. Check for pending interrupts (before fetch)
        if (interrupt_pending && interrupts_enabled()) {
            take_interrupt();
            continue;
        }

        // 2. Fetch
        uint32_t instr_word;
        if (!fetch(pc, instr_word)) {
            // fetch raised an instruction-access fault; exception already taken
            continue;
        }

        // 3. Decode
        DecodedInstr instr = decode(instr_word);

        // 4. Execute
        execute(instr);

        // 5. Advance simulation time (temporal decoupling)
        local_time += CYCLE_TIME;
        if (local_time >= quantum) {
            wait(local_time); // sync with SystemC scheduler
            local_time = SC_ZERO_TIME;
        }
    }
}
```

Each step has design choices that affect correctness and performance.

## Step 1: Interrupt Polling

Interrupts must be checked at a precise point in the loop — typically before fetching the next instruction. This ensures that interrupt delivery is "between instructions," which is what every ISA specification requires.

In TLM-based platforms, interrupts arrive via a signal port (an `sc_in<bool>`) or a SystemC event. The ISS typically stores a flag in a shared variable:

```cpp
// Peripheral calls this via a TLP socket or SystemC event
void RISCVCPU::set_interrupt(uint32_t irq_line) {
    pending_irq |= (1u << irq_line);
    interrupt_pending = true;
    interrupt_event.notify(); // wake the ISS if it is waiting
}
```

The loop checks `interrupt_pending` (a `volatile bool` or `std::atomic<bool>`) at the top of each iteration.

## Step 2: Instruction Fetch

Fetch reads `sizeof(instruction)` bytes from the memory model at `pc`. Two important cases:

- **DMI fast path**: If the CPU holds a valid DMI pointer covering `pc`, the fetch is a simple pointer dereference — no TLM overhead.
- **Slow path**: A full `b_transport` call if DMI is not cached or has been invalidated.

```cpp
bool RISCVCPU::fetch(uint32_t addr, uint32_t& out_word) {
    if (dmi_valid && addr >= dmi_start && addr + 3 <= dmi_end) {
        out_word = *(uint32_t*)(dmi_ptr + (addr - dmi_start));
        return true;
    }
    return fetch_slow(addr, out_word); // b_transport + possible DMI request
}
```

A misaligned PC (e.g., `pc & 3 != 0` on a 32-bit ISA without compressed instructions) must raise an **instruction-address misaligned** exception rather than reading garbage bytes.

## Step 3: Decode

Decode parses the instruction word into an opcode, register indices, and immediate values. The goal is to produce a `DecodedInstr` struct that the execute phase can consume without touching the raw bit fields again:

```cpp
struct DecodedInstr {
    Opcode  op;
    uint8_t rd, rs1, rs2;
    int32_t imm;        // sign-extended
    uint32_t raw;       // kept for CSR instructions / illegal-instruction reporting
};
```

Decode should be a **pure function** — it reads only the instruction word and produces the struct. This makes it easy to unit-test independently of the rest of the simulator.

## Step 4: Execute

The execute function dispatches on `op` and modifies CPU state. Important invariants:

- **Write-back last**: read all source registers before writing the destination. Some ISAs allow `rd == rs1` (e.g., `ADD x1, x1, x2`) and the result must be computed from the old `rs1`.
- **x0 is always 0** (RISC-V): either skip writes to `rd == 0` or reset `reg[0] = 0` after every instruction.
- **Branch instructions modify `pc` directly**: the loop must not add 4 to `pc` after a taken branch.

```cpp
void RISCVCPU::execute(const DecodedInstr& d) {
    uint32_t result = 0;
    bool taken = false;

    switch (d.op) {
        case ADD:  result = reg[d.rs1] + reg[d.rs2];       break;
        case ADDI: result = reg[d.rs1] + d.imm;            break;
        case LW:   result = mem_read32(reg[d.rs1] + d.imm); break;
        case SW:   mem_write32(reg[d.rs1] + d.imm, reg[d.rs2]); pc += 4; return;
        case BEQ:
            if (reg[d.rs1] == reg[d.rs2]) { pc += d.imm; return; }
            pc += 4; return;
        case JAL:  result = pc + 4; pc += d.imm; if (d.rd) reg[d.rd] = result; return;
    }
    if (d.rd) reg[d.rd] = result;
    pc += 4;
}
```

## Step 5: Temporal Decoupling and the Quantum

Rather than calling `wait(CYCLE_TIME)` after every single instruction (which would be thousands of SystemC context switches per microsecond), the ISS accumulates time in a local counter and yields to the SystemC scheduler only when the **time quantum** is exhausted.

```cpp
local_time += sc_time(10, SC_NS); // 10 ns per instruction (100 MHz approx)
if (local_time >= quantum) {
    wait(local_time);       // SystemC yield point
    local_time = SC_ZERO_TIME;
}
```

Typical quanta range from 1 µs to 1 ms. Larger quanta mean fewer context switches and faster simulation, but interrupt delivery timing becomes less accurate.

## The Halted State

The ISS must handle a **halt** instruction (e.g., RISC-V `WFI` — Wait For Interrupt). Instead of spinning, it should wait on a SystemC event:

```cpp
case WFI:
    pc += 4;
    wait(interrupt_event); // suspend until interrupt_event.notify() is called
    break;
```

This prevents the simulator from consuming 100% host CPU while the virtual CPU is idle.

## Common Pitfalls

- **Interrupt at the wrong granularity**: Checking interrupts every 1000 instructions instead of every instruction causes incorrect interrupt latency.
- **Exception inside exception**: If `take_exception()` is itself buggy and raises another exception, you get an infinite loop. Add a nesting guard.
- **PC corruption on branch**: Forgetting to `return` after setting `pc` for a branch causes the loop to add 4 again, landing at the wrong address.

## Interview Answer

> "The fetch-execute loop fetches an instruction word at the PC, decodes it, executes it by modifying the register file or memory, and advances the PC. In a TLM-based ISS, interrupts are checked between instructions, temporal decoupling is applied by accumulating time locally and yielding to SystemC only at quantum boundaries, and the WFI (Wait For Interrupt) instruction suspends the ISS on a SystemC event to avoid spinning."
