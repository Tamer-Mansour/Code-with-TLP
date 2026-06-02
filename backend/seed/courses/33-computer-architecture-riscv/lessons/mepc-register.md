# mepc: The Machine Exception Program Counter

`mepc` (machine exception program counter, CSR 0x341) stores the address the processor should return to after handling a trap. It is written automatically by hardware on every trap entry and read by the `MRET` instruction to resume normal execution.

## What Gets Saved in mepc

The value written to `mepc` depends on the trap type:

| Trap type | Value saved in mepc |
|-----------|---------------------|
| Exception (synchronous) | Address of the faulting instruction |
| Interrupt (asynchronous) | Address of the next instruction that would have executed |

This distinction is critical for correct trap handling. After an interrupt the handler can simply execute `MRET` and execution continues from where it left off. After an exception the handler must decide whether to retry the faulting instruction (return to `mepc` unchanged) or skip it (increment `mepc` by the instruction size before returning).

## Hardware Guarantees

- `mepc` is always written before the first instruction of the trap handler executes.
- The stored value always has its bottom bit cleared (bit 0 = 0), because RISC-V PCs are always even. In RV32/RV64 without the C extension, bit 1 is also 0 (4-byte alignment).
- With the C extension (compressed instructions), the stored value may be 2-byte aligned.

## Using mepc in a Trap Handler

### Returning to the interrupted point (interrupt case)

```asm
trap_handler:
    # ... save registers, handle interrupt ...
    mret              # PC = mepc; restores MIE and MPP from mstatus
```

### Skipping a faulting instruction (exception case)

To advance past the instruction that caused the exception, add 4 (or 2 for a compressed instruction) to `mepc` before returning:

```asm
exception_handler:
    csrr  t0, mepc
    addi  t0, t0, 4   # skip the 32-bit faulting instruction
    csrw  mepc, t0
    mret
```

To handle both 16-bit and 32-bit instructions, read the instruction word and check the opcode:

```asm
    csrr  t0, mepc
    lhu   t1, 0(t0)        # load the faulting instruction (16 bits)
    andi  t2, t1, 0x3      # check bottom 2 bits
    li    t3, 0x3
    beq   t2, t3, is_32bit # if 0b11, it's a 32-bit instruction
    addi  t0, t0, 2        # 16-bit (compressed) — skip 2 bytes
    j     done
is_32bit:
    addi  t0, t0, 4        # 32-bit — skip 4 bytes
done:
    csrw  mepc, t0
    mret
```

## Modifying mepc to Jump Elsewhere

`mepc` is a writable CSR. You can redirect execution to any target by writing a new address before `MRET`. This is how operating systems implement `ecall`-based system calls:

```asm
# ecall handler: return to the instruction AFTER the ecall
# and place the return value in a0
ecall_handler:
    csrr  t0, mepc
    addi  t0, t0, 4     # ecall is always 4 bytes
    csrw  mepc, t0
    # ... compute result, write to a0 ...
    mret
```

The OS can also use this to implement signal delivery, longjmp across privilege levels, or to redirect execution to an emulation routine.

## Nested Traps and mepc

`mepc` is a single register — it is **overwritten** on every trap entry. If a trap handler takes a second trap (e.g., a page fault inside the handler), the original `mepc` value is lost unless the handler saved it first.

Best practice for handlers that may re-enable interrupts:

```asm
trap_handler:
    csrr  t0, mepc         # save mepc before re-enabling interrupts
    sw    t0, saved_mepc, t1
    # ... enable interrupts, do work ...
    lw    t0, saved_mepc, t1
    csrw  mepc, t0         # restore before mret
    mret
```

## Common Pitfalls

- **Returning to mepc after an exception without advancing it**: causes an infinite fault loop.
- **Hardcoding +4 when C extension is active**: skips two instructions instead of one.
- **Not saving mepc before nested interrupts**: corrupts the return address of the outer trap.

> **Interview answer:** `mepc` holds the PC value saved when a trap fires. For exceptions it points to the faulting instruction (so the handler can retry or skip it); for interrupts it points to the next instruction to execute. `MRET` reads `mepc` to restore the PC.
