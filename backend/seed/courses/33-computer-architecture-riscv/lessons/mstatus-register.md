# The mstatus Register

`mstatus` (machine status, CSR address 0x300) is the most important CSR in M-mode. It records the global interrupt-enable state, tracks the previous privilege level, and controls several memory-model features. Understanding `mstatus` is essential for writing correct trap handlers and OS kernels.

## Key Fields (RV32 and RV64)

| Bit(s) | Name  | Description |
|--------|-------|-------------|
| 3      | MIE   | Machine-mode global interrupt enable |
| 7      | MPIE  | Previous value of MIE (saved on trap entry) |
| 12:11  | MPP   | Previous privilege mode (saved on trap entry) |
| 1      | SIE   | Supervisor-mode global interrupt enable |
| 5      | SPIE  | Previous SIE |
| 8      | SPP   | Previous supervisor privilege (1-bit) |
| 17     | MPRV  | Modify PRiVilege for load/store |
| 18     | SUM   | Supervisor User Memory access |
| 19     | MXR   | Make eXecutable Readable |
| 63:34  | (RV64)| SD, UXL, SXL — extended fields |

Only the M-mode fields (MIE, MPIE, MPP) are required for bare-metal trap handling.

## Trap Entry Sequence Involving mstatus

When a trap fires at M-mode:

1. `mstatus.MPIE` ← current `mstatus.MIE`
2. `mstatus.MIE` ← 0  (interrupts disabled in handler)
3. `mstatus.MPP` ← current privilege level (2-bit encoding)

This three-step operation is **atomic** — the hardware does all three before the first handler instruction executes.

## Privilege Encoding in MPP

| MPP value | Previous privilege |
|-----------|--------------------|
| 0b00      | User (U-mode)      |
| 0b01      | Supervisor (S-mode)|
| 0b11      | Machine (M-mode)   |

(Value 0b10 is reserved.)

## Trap Return with MRET

`MRET` reverses the entry sequence:

1. `mstatus.MIE` ← `mstatus.MPIE`
2. `mstatus.MPIE` ← 1
3. Current privilege ← `mstatus.MPP`
4. `mstatus.MPP` ← U-mode (for security — avoids accidental M-mode re-entry)
5. PC ← `mepc`

The result is a seamless return to the code that was interrupted, with interrupts re-enabled and privilege restored.

## Reading and Writing mstatus

```asm
# Disable global interrupts manually (clear MIE, bit 3)
li    t0, (1 << 3)
csrc  mstatus, t0     # mstatus.MIE = 0

# Re-enable global interrupts
csrs  mstatus, t0     # mstatus.MIE = 1

# Read full mstatus value
csrr  t1, mstatus
```

## The MPRV, SUM, and MXR Bits

These bits affect how loads and stores translate addresses:

- **MPRV = 1**: loads and stores use the privilege mode stored in MPP for translation instead of the current privilege. Useful for OS kernels copying to/from user memory.
- **SUM = 1**: allows supervisor-mode software to access user-accessible pages (normally forbidden).
- **MXR = 1**: allows loads from execute-only pages; treats them as readable.

These bits should be cleared when not actively needed — leaving MPRV set with MPP=U is a common security bug that lets M-mode code accidentally follow user-space pointers.

## Worked Example: Identifying the Interrupted Privilege Level

```asm
# Inside M-mode trap handler
csrr  t0, mstatus
srli  t0, t0, 11       # shift MPP field to bits [1:0]
andi  t0, t0, 3        # mask to get 2-bit MPP
# t0 == 0  => interrupted U-mode
# t0 == 1  => interrupted S-mode
# t0 == 3  => interrupted M-mode
```

## Common Pitfalls

- **Forgetting to save/restore mstatus** in nested-interrupt handlers: if a second trap fires before you save MPIE and MPP, the first trap's context is lost.
- **Clearing MIE early but restoring it late**: leaves a window where interrupts are missed or delivery is delayed.
- **Assuming MPIE==1 after trap entry**: MPIE reflects the old MIE, which may have already been 0 if interrupts were disabled before the trap.

> **Interview answer:** `mstatus` holds the global interrupt-enable bit MIE, and on every trap the hardware atomically saves MIE into MPIE, clears MIE, and stores the pre-trap privilege in MPP. MRET restores all three, enabling a safe return to the interrupted context.
