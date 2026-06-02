# Reading and Analyzing an Instruction Trace

An instruction trace is a chronological log of every instruction the CPU executed: its address (PC), its encoding, its mnemonic, and optionally the register file state after execution. It is the most detailed record of software behaviour you can produce on a virtual prototype, and it is indispensable for debugging hangs, fault handlers, and subtle control-flow bugs.

## Anatomy of an Instruction Trace Line

A typical ARM Cortex-A instruction trace looks like:

```
1234567  0x00010054  e3a00001  MOV r0, #1          r0=0x00000001
1234568  0x00010058  e5801000  STR r0, [r0]         (fault at next)
1234569  0x00000018  e59ff014  LDR pc, [pc, #20]    pc=0x00010070
```

| Column | Meaning |
|---|---|
| Instruction count | Monotonically increasing; useful for bisecting |
| PC (hex) | Address of the instruction |
| Encoding | Raw 32-bit (or 16-bit Thumb) word |
| Mnemonic | Human-readable disassembly |
| Side effect | Changed registers or memory (optional but valuable) |

## Step 1: Find the Starting Point

You usually have a symptom — a crash address, a hang. Start from there and work backwards. Use `grep` to find the first occurrence of the crash address:

```bash
grep "0x00000018" trace.log | head -5
```

The `0x00000018` is the ARM data-abort vector. The preceding line is the faulting instruction.

## Step 2: Identify Loop Patterns

A hang manifests as a repeating PC sequence. Scan for blocks of addresses that repeat:

```bash
# Extract just the PC column and find repeated sequences
awk '{print $2}' trace.log | uniq -c | sort -rn | head -20
```

Output:
```
 100000 0x000100a4
  99999 0x000100a0
```

Two addresses alternating 100k times is a spin loop. Examine those two instructions:

```asm
0x000100a0:  LDR  r1, [r0]       ; load status register
0x000100a4:  TST  r1, #0x1       ; test ready bit
             BEQ  0x000100a0     ; loop if not ready
```

The peripheral never set bit 0. The model is missing that behaviour.

## Step 3: Trace a Function Call Chain

Look for `BL` / `BLX` (branch-with-link) instructions to reconstruct the call stack without gdb:

```
...
0x000102c0  BL   0x00010300    ; call uart_putchar
0x00010300  PUSH {r4, lr}
...
0x0001033c  POP  {r4, pc}     ; return
0x000102c4  ...               ; next instruction after call
```

Cross-reference with the ELF's symbol table:

```bash
arm-none-eabi-nm --numeric-sort firmware.elf | grep -A1 "00010300"
```

## Step 4: Check for Exception Entry

ARM exception entry has a distinctive signature — the PC jumps to the vector table (typically `0x00000000–0x0000003C` or remapped by VBAR), then SPSR is saved. Identify these jumps:

```
0x000105a0  LDR  r0, [r1]       ; this causes a fault
0x00000010  LDR  pc, [pc, #...] ; undefined instruction vector
```

If you see repeated trips into the vector table, the software is stuck in an exception loop.

## Worked Example: Tracing a NULL Dereference

The trace below is 5 instructions before and after a crash:

```asm
; 1000: r0 = 0x20001000  (valid pointer)
0x000102a0  LDR  r0, [r1, #8]    r0=0x00000000   ; BUG: loaded NULL
0x000102a4  LDR  r2, [r0]        ; dereference NULL -> data abort
; --- vector table ---
0x00000018  LDR  pc, [pc, #20]   pc=0x00010070   ; data abort handler
```

Root cause: the struct field at offset 8 (`[r1, #8]`) is zero — an uninitialized pointer. The model correctly reflects this; the bug is in the software.

## Common Pitfalls

- **Trace files are enormous.** A 1-second run at 100 MIPS produces 100 million lines. Use circular trace buffers (keep last N instructions) or trigger-based capture.
- **Thumb vs ARM mismatch.** If the ISS logs raw encodings, make sure you disassemble with the correct ISA mode. Thumb-2 16-bit instructions look wrong if decoded as 32-bit ARM.
- **Instruction count vs cycle count.** The instruction count advances by 1 per instruction. The cycle count may advance by more if the ISS models multi-cycle instructions. Use the right counter for the right question.

> **Interview answer:** "I look for repeating PC patterns (spin loops), vector-table jumps (exception storms), and work backwards from the fault address using the instruction count as a timeline. The trace never lies about what the CPU did — the question is always why."
