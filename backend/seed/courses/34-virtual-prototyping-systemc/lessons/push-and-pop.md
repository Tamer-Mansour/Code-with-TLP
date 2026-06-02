# Push and Pop Operations

Push and pop are the two fundamental stack operations. They combine a change to the stack pointer with a memory access into a single conceptual step. On many ISAs they are encoded as a single instruction; on others (like RISC-V) the compiler emits two instructions to achieve the same effect.

## What "Push" Means

A **push** of value `V` does two things atomically from the programmer's perspective:

1. Decrement SP by the size of `V` (because the stack grows downward).
2. Store `V` at the new address pointed to by SP.

```
Before push:   SP → [0x1FF8]  (free)
                    [0x1FF4]  (free)

PUSH 0xDEAD (4-byte word):
  SP ← SP - 4  →  SP = 0x1FF4
  MEM[0x1FF4]  ←  0xDEAD

After push:    SP → [0x1FF4] = 0xDEAD
```

## What "Pop" Means

A **pop** into destination register `R` reverses the operation:

1. Read the value at the address currently in SP into `R`.
2. Increment SP by the size of the value.

```
Before pop:    SP → [0x1FF4] = 0xDEAD
                    [0x1FF8]  (free)

POP R0:
  R0          ←  MEM[0x1FF4]  =  0xDEAD
  SP          ←  SP + 4       =  0x1FF8

After pop:     SP → [0x1FF8]  (effectively freed)
```

Note that the data at `0x1FF4` is not erased — it remains in memory but is no longer considered part of the stack.

## Architecture Examples

### x86-64

```asm
; Push the 64-bit value in RAX onto the stack
push rax       ; RSP ← RSP - 8 ; MEM[RSP] ← RAX

; Pop 64 bits from the stack into RBX
pop rbx        ; RBX ← MEM[RSP] ; RSP ← RSP + 8

; CALL implicitly pushes the return address
call my_func   ; MEM[RSP-8] ← RIP+5 ; RSP ← RSP-8 ; RIP ← my_func

; RET implicitly pops the return address
ret            ; RIP ← MEM[RSP] ; RSP ← RSP + 8
```

### ARM Cortex-M (Thumb-2)

```asm
; Push R4, R5, and LR (link register) onto the stack
PUSH {R4, R5, LR}   ; SP decremented by 12; registers stored in order

; Pop them back (restoring PC from LR effectively returns)
POP  {R4, R5, PC}
```

ARM's `PUSH`/`POP` can save/restore multiple registers in a single instruction, which is more code-dense than x86's one-register-at-a-time approach.

### RISC-V (no dedicated push/pop instruction)

```asm
# Manually "push" ra and s0 (each 4 bytes on RV32)
addi  sp, sp, -8      # decrement SP
sw    ra, 4(sp)       # store return address
sw    s0, 0(sp)       # store frame pointer

# Manually "pop" them
lw    ra, 4(sp)
lw    s0, 0(sp)
addi  sp, sp,  8      # restore SP
ret
```

## Common Pitfalls

- **Mismatched push/pop counts.** Pushing without a matching pop causes SP to drift, corrupting subsequent frames. This is often caught by the compiler but can appear in hand-written assembly.
- **Pushing the wrong size.** On x86-64, `push` always moves SP by 8 bytes regardless of the data type. Forgetting this when mixing 32-bit and 64-bit code leads to alignment faults.
- **Popping into the wrong register.** After a function call, the callee may have pushed registers in a specific order. Popping in the wrong order silently swaps register values — a hard-to-debug class of bug.
- **Assuming popped memory is zeroed.** Security-sensitive code must explicitly zero stack slots before popping to avoid leaking secrets to a later stack user.

## Virtual Prototype Perspective

An ISS decodes each push/pop instruction and issues two TLM transactions: one for the SP update (register file write) and one for the data (memory read or write). The memory transaction's address is the **updated** SP for a push and the **old** SP for a pop. Getting this ordering wrong in an ISS is a common bug that manifests as the VP running firmware that writes garbage return addresses.

> **Interview answer:** Push decrements SP by the operand size and writes the value to the new SP address; pop reads the value at the current SP and then increments SP. The data remains in memory after a pop but is no longer logically on the stack.
