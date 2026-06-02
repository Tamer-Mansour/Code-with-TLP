# mie and mip: Interrupt Enable and Pending

Two CSRs govern which interrupts the processor can accept and which are currently waiting for service. `mie` (machine interrupt enable, CSR 0x304) controls the mask; `mip` (machine interrupt pending, CSR 0x344) reflects real-time hardware signals.

## The Three-Gate Model

For an interrupt to be delivered at M-mode, three conditions must all be true:

1. `mstatus.MIE` = 1 (global interrupt enable)
2. The corresponding bit in `mie` = 1 (per-source enable)
3. The corresponding bit in `mip` = 1 (interrupt is pending)

Think of it as three gates in series: global enable, per-source enable, and a hardware signal. All three must be open for the interrupt to reach the CPU.

## mie — Machine Interrupt Enable

`mie` is a read-write register. Each bit enables one interrupt source:

| Bit | Name  | Interrupt source |
|-----|-------|-----------------|
| 1   | SSIE  | Supervisor software interrupt |
| 3   | MSIE  | Machine software interrupt |
| 5   | STIE  | Supervisor timer interrupt |
| 7   | MTIE  | Machine timer interrupt |
| 9   | SEIE  | Supervisor external interrupt |
| 11  | MEIE  | Machine external interrupt |

Bits not listed are reserved (write 0, read 0).

```asm
# Enable machine timer and machine external interrupts only
li    t0, (1 << 7) | (1 << 11)   # MTIE | MEIE
csrw  mie, t0

# Add supervisor timer without disturbing other bits
li    t0, (1 << 5)                # STIE
csrs  mie, t0                     # mie |= STIE

# Disable machine timer
li    t0, (1 << 7)
csrc  mie, t0                     # mie &= ~MTIE
```

## mip — Machine Interrupt Pending

`mip` is mostly read-only from software's perspective. Bits are set by hardware when an interrupt source asserts its signal. Software can write the software-interrupt bits (MSIP, SSIP) but cannot directly clear timer or external interrupt bits — those are cleared by servicing the hardware source.

| Bit | Name  | Notes |
|-----|-------|-------|
| 1   | SSIP  | Software-writable; triggers S-mode SW interrupt |
| 3   | MSIP  | Software-writable via MSIP memory-mapped register |
| 5   | STIP  | Set by hardware (STIMER); cleared by writing stimecmp |
| 7   | MTIP  | Set by hardware (MTIMER); cleared by writing mtimecmp |
| 9   | SEIP  | Set by hardware (PLIC or CLINT) |
| 11  | MEIP  | Set by hardware (PLIC); cleared by PLIC claim/complete |

## Polling mip Without Interrupts

`mip` can be polled in a busy-wait loop when you want to wait for a specific event without enabling interrupts globally:

```asm
wait_for_timer:
    csrr  t0, mip
    andi  t0, t0, (1 << 7)   # check MTIP
    beqz  t0, wait_for_timer
    # Timer has fired — handle it
```

## Setting a Software Interrupt

Machine software interrupts are typically used for inter-processor interrupts (IPIs). The CLINT (Core-Local INTerrupt) exposes a memory-mapped MSIP register at a platform-defined address. Writing 1 to it sets MSIP in `mip`:

```c
// Platform-specific MSIP address (SiFive CLINT example)
volatile uint32_t *msip = (volatile uint32_t *)0x02000000UL;
*msip = 1;   // triggers machine software interrupt on hart 0
```

Clearing it:

```c
*msip = 0;   // clear MSIP; the interrupt is now de-asserted
```

## Interaction with mstatus.MIE

A common debugging scenario: interrupts are enabled in `mie` and a pending bit is set in `mip`, but no interrupt fires. Check `mstatus.MIE` first — it is often cleared by a preceding trap that was never properly closed with `MRET`.

```asm
# Diagnose: read all three registers
csrr  t0, mstatus
csrr  t1, mie
csrr  t2, mip
# Compare t1 & t2: any set bits indicate enabled-and-pending interrupts
# Check bit 3 of t0 (MIE): if 0, nothing will fire
```

## Priority and Simultaneous Interrupts

When multiple interrupts are pending and enabled simultaneously, RISC-V defines a default priority order (highest to lowest):

MEI > MSI > MTI > SEI > SSI > STI

The implementation delivers the highest-priority pending interrupt first.

## Common Pitfalls

- **Writing to read-only bits of mip**: silently ignored; you cannot force a fake timer interrupt by writing MTIP.
- **Clearing timer interrupt without updating mtimecmp**: MTIP is re-asserted immediately because `mtime >= mtimecmp` is still true.
- **Forgetting `mstatus.MIE`**: enabling `mie.MTIE` is useless if `mstatus.MIE` is 0.

> **Interview answer:** `mie` is a per-source interrupt enable mask; `mip` reflects which interrupts are currently pending. An interrupt fires only when `mstatus.MIE`, the relevant `mie` bit, and the relevant `mip` bit are all set. Most `mip` bits are read-only hardware signals cleared by servicing the source.
