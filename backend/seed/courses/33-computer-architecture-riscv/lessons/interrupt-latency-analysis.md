# Interrupt Latency Analysis

**Interrupt latency** is the elapsed time between when a hardware event asserts an interrupt request and when the first instruction of the interrupt service routine (ISR) begins execution. Minimizing and bounding this latency is critical in real-time systems, where missing a deadline can have safety consequences.

---

## Components of interrupt latency

Total latency is the sum of several sequential delays:

```
|-- Recognition --|-- Pipeline flush --|-- Vector fetch --|-- Context save --|-- ISR body --|
     L_rec              L_flush              L_vec               L_ctx
```

| Component | Description | Typical range |
|-----------|-------------|---------------|
| **Recognition (L_rec)** | Hardware samples the IRQ line; may be synchronous to clock edge | 1–3 cycles |
| **Instruction completion (L_instr)** | Current instruction must complete before the trap is taken | 1–N cycles (multicycle instructions) |
| **Pipeline flush (L_flush)** | In-flight instructions squashed and pipeline drained | 2–10 cycles |
| **Vector fetch (L_vec)** | Fetch the ISR address from `mtvec` (direct) or vector table entry | 1–5 cycles (cache miss: 100+) |
| **Context save (L_ctx)** | Prologue saves registers to the stack | ~(N_regs × 1) cycles |
| **Branch prediction miss** | If vectored mode jumps cause BTB misses | 5–15 cycles |

---

## Worst-case interrupt latency (WCIL)

For real-time certification, designers must prove the **Worst-Case Interrupt Latency (WCIL)**:

```
WCIL = L_rec + L_instr_max + L_flush + L_vec + L_ctx_full
```

Example for a simple in-order RISC-V core at 100 MHz:

```
L_rec        =  2 cycles  =  20 ns
L_instr_max  =  5 cycles  =  50 ns  (divide instruction)
L_flush      =  3 cycles  =  30 ns
L_vec        =  2 cycles  =  20 ns  (instruction cache hit)
L_ctx        = 34 cycles  = 340 ns  (17 × sd + addi sp)
-------------------------------------------------
WCIL         = 46 cycles  = 460 ns
```

---

## Factors that increase latency

- **Cache misses** — if `mtvec` address or the first ISR instruction is not in the instruction cache, a DRAM fetch adds 50–200 ns on typical embedded systems.
- **Long instructions** — division, `fence`, or memory barrier instructions that must complete before the trap is taken.
- **Interrupt masking** — critical sections with `MIE=0` add the duration of the masked window.
- **Nested interrupts** — the outer handler's context save runs before the inner ISR starts.
- **Interrupt controller latency** — PLIC claim/priority evaluation is a memory-mapped operation adding 2–10 cycles.

---

## Techniques to reduce latency

### 1. Vectored mode

Switch `mtvec` to vectored mode to skip software dispatch:

```asm
la   t0, vector_table
ori  t0, t0, 1
csrw mtvec, t0
```

Saves 10–20 cycles over a long dispatch chain.

### 2. Minimal context save

Save only caller-saved registers if the handler is a leaf:

```c
// compiler attribute: no function-call prologue generated
void __attribute__((interrupt("machine"))) timer_isr(void) {
    TIMER->clear = 1;
    tick_count++;
}
```

GCC generates a minimal save/restore frame for ISRs marked with this attribute.

### 3. Lock the ISR in cache

On cores with lockable instruction caches, pin the ISR code so it is never evicted:

```c
// Platform-specific cache lock (pseudocode)
cache_lock_region((uintptr_t)timer_isr, 64);
```

### 4. Shorten critical sections

Replace long critical sections with **lock-free** data structures or move work out of the masked window:

```c
// Bad: long critical section
disable_irq();
result = expensive_computation(data);
shared_var = result;
enable_irq();

// Better: only the assignment is protected
result = expensive_computation(data);
disable_irq();
shared_var = result;
enable_irq();
```

---

## Measuring latency with a GPIO toggle

A standard embedded technique uses a logic analyzer:

```c
void timer_isr(void) {
    GPIO->out ^= 1;    // toggle pin — first instruction of ISR
    // handler body ...
    GPIO->out ^= 1;    // toggle pin — last instruction before mret
}
```

The rising edge of the GPIO relative to the timer signal on a logic analyzer gives the actual measured latency under real conditions.

---

## Jitter

**Interrupt jitter** is the variation in latency across multiple occurrences of the same interrupt. High jitter is problematic for audio, motor control, and communication protocols. Sources of jitter include cache miss variability, branch mispredictions, and the position within a variable-length critical section.

---

> **Interview answer:** Interrupt latency is the time from hardware assertion to the first ISR instruction, comprising recognition time, instruction completion, pipeline flush, vector fetch, and context save. It is minimized by using vectored `mtvec` mode (skipping software dispatch), keeping critical sections short, locking the ISR in cache, and saving only the registers actually needed. For real-time certification, you must compute the worst-case latency including cache miss penalties.
