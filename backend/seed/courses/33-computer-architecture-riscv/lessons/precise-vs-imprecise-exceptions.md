# Precise vs Imprecise Exceptions

Modern processors execute instructions out of order and may have multiple instructions in flight simultaneously. When an exception occurs, the processor must decide exactly what state to present to the handler. A **precise** exception model makes a strong, programmer-friendly guarantee; an **imprecise** model trades that guarantee for higher hardware performance.

---

## Precise exceptions defined

An exception is **precise** if, at the moment of the trap, the architectural state satisfies all three conditions:

1. **All instructions before the faulting instruction have completed** — their results are committed to the register file and memory.
2. **The faulting instruction has not completed** — its results are NOT visible (or the exception is reported before they become visible).
3. **All instructions after the faulting instruction appear as if they never executed** — they are squashed without side effects.

This gives the handler a clean, consistent view: it sees exactly the state that existed just before the faulting instruction.

```
Instruction stream:   I1  I2  I3[fault]  I4  I5
Precise model:
  I1 visible = YES
  I2 visible = YES
  I3 visible = NO  (faulted, not committed)
  I4 visible = NO  (squashed)
  I5 visible = NO  (squashed)
  mepc = address of I3
```

---

## Why precise exceptions are hard in out-of-order processors

An out-of-order (OoO) processor may have started I5 before finishing I3. If I4 completes (writes its result to the register file) before I3 is found to fault, the state is now "dirty" — the handler would see I4's effects even though I4 comes *after* the faulting instruction.

Implementing precise exceptions in an OoO core requires:

- A **reorder buffer (ROB)** that holds results until they are committed in program order.
- Instructions are committed only when all older instructions have committed without faults.
- On a fault, all younger entries in the ROB are discarded (squashed).

The ROB is one of the most area- and power-hungry structures in a modern OoO core, and handling precise exceptions is a primary reason it exists.

---

## Imprecise exceptions

An **imprecise** exception model relaxes the guarantee: the architectural state at the time of the trap may include results from instructions after the faulting one, or may be missing results from instructions before it.

Historical context: the IBM System/360 Model 91 (1966) introduced out-of-order execution and could not always determine which floating-point instruction caused an error — an early imprecise exception model.

Imprecise exceptions appear today in:
- **Asynchronous errors** such as memory ECC corrections detected after the load has committed.
- **Bus errors** in ARM Cortex-M that report imprecise bus faults (`IMPRECISERR` bit in the BFSR register).
- **Floating-point underflow/overflow** in some architectures where FPU operations post-complete before the main pipeline knows.

---

## Comparison table

| Property | Precise | Imprecise |
|----------|---------|-----------|
| Architectural state at trap | Exact snapshot at fault point | Partially updated, indeterminate |
| Handler can re-execute faulting instruction | Yes | Not generally safe |
| Hardware complexity | High (ROB required) | Lower |
| Debuggability | Easy — `mepc` is exact | Hard — fault may not be reproducible |
| Use case | General-purpose OS, user apps | High-throughput pipelines, async faults |

---

## RISC-V position

RISC-V mandates **precise synchronous exceptions**. The specification states:

> "Instruction exceptions, including illegal instruction, are precise: all instructions before the faulting instruction have completed, and the faulting instruction (and those after it) have not."

For **asynchronous interrupts**, RISC-V only requires that the hardware deliver them at some instruction boundary — which instruction is interrupted may vary. The saved `mepc` points to the next instruction to execute, which is correct and sufficient.

---

## Worked example: page fault recovery

```c
// Kernel page-fault handler (pseudo-code)
void page_fault_handler(uintptr_t mepc, uintptr_t mtval) {
    // mtval = the faulting virtual address
    // Because the exception is precise:
    //   - the load/store that faulted did NOT modify memory
    //   - all prior instructions have committed
    uintptr_t fault_addr = mtval;
    map_page(fault_addr);          // allocate and map the page
    // No state repair needed — just return to mepc (the faulting instruction)
    // and it will retry successfully.
}
```

If the exception were imprecise, the handler would not know whether the load partially wrote a destination register, making it impossible to safely re-execute.

---

## Common pitfalls

- Assuming asynchronous interrupts in RISC-V are precise in the sense that `mepc` points to the offending instruction — they do not; `mepc` is just the resume point.
- Confusing imprecise *exceptions* with imprecise *bus faults* — the latter are a specific subtype.
- OoO designs that claim "mostly precise" exceptions — always verify the errata for which operations can generate imprecise reports.

---

> **Interview answer:** A precise exception guarantees that at the moment of the trap, all instructions before the faulting one have committed and none after it have committed, giving the handler an exact state snapshot and allowing re-execution of the faulting instruction. An imprecise exception relaxes this guarantee for hardware efficiency but makes recovery difficult or impossible. RISC-V mandates precise synchronous exceptions and implements them via a reorder buffer in out-of-order designs.
