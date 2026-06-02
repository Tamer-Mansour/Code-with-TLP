# Apply Write-1-to-Clear Register Semantics

In this exercise you will simulate a sequence of hardware events and firmware register accesses on a W1C interrupt status register, producing the correct register value after each operation.

## What You Will Implement

A peripheral has a 32-bit **Interrupt Status Register (ISR)** where every bit is W1C. Hardware events asynchronously set individual bits. Firmware clears bits by writing 1 to them.

Given a sequence of operations — either a hardware SET of certain bits or a firmware WRITE of a certain value — output the ISR value after each operation.

Operations:
- `HW_SET <hex_mask>` — hardware logic ORs the mask into the current ISR value (sets those bits).
- `FW_WRITE <hex_value>` — firmware writes the value; W1C semantics apply: bits where the written value has a 1 are cleared in ISR.

## Skills Practiced

- Implementing W1C semantics correctly: `isr &= ~written`
- Distinguishing hardware-driven bit setting from firmware acknowledgement
- Processing a stateful sequence of register operations

## Why This Matters

Interrupt status registers are among the most common W1C registers in real SoCs. A common firmware bug is writing the wrong mask to the ISR, leaving stale flags set and causing spurious re-entry into interrupt handlers. Simulating the model correctly prevents this class of bug from reaching silicon validation.

## Example Walkthrough

Starting ISR value: `0x00000000`

```
HW_SET  0x00000005   -> ISR = 0x00000005  (bits 0 and 2 set by hardware)
HW_SET  0x00000003   -> ISR = 0x00000007  (bits 0 and 1 also set)
FW_WRITE 0x00000001  -> ISR = 0x00000006  (bit 0 cleared by firmware)
FW_WRITE 0x00000006  -> ISR = 0x00000000  (bits 1 and 2 cleared)
```

Your program reads the number of operations and each operation line, then prints the ISR value after each operation.
