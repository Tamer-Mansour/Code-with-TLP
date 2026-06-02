# mtvec: The Trap Vector Base Register

`mtvec` (machine trap-vector base-address register, CSR 0x305) tells the processor where to jump when any M-mode trap fires. It is the single most critical register to configure before enabling interrupts or accepting exceptions.

## Register Layout

```
 XLEN-1          2  1 0
 ┌──────────────────┬───┐
 │       BASE       │MOD│
 └──────────────────┴───┘
```

- **BASE** (bits [XLEN-1:2]): the base address of the trap handler(s), always aligned to at least 4 bytes (the bottom two bits are always 0 in the stored address).
- **MODE** (bits [1:0]): selects the vectoring mode.

## Vectoring Modes

| MODE | Name    | Behavior |
|------|---------|----------|
| 0    | Direct  | All traps jump to BASE |
| 1    | Vectored| Exceptions jump to BASE; interrupt N jumps to BASE + 4*N |
| 2–3  | Reserved| Implementation-defined |

### Direct Mode

The entire trap handler starts at a single address. The handler must read `mcause` to determine what happened and dispatch accordingly.

```asm
    .align 4
trap_entry:
    csrr  t0, mcause
    bltz  t0, is_interrupt   # bit 31 (XLEN-1) set => interrupt
    j     handle_exception
is_interrupt:
    ...
```

### Vectored Mode

The processor computes the handler address as `BASE + 4 * cause_number`, where `cause_number` is the interrupt number from `mcause` (bit 31 cleared). This creates a jump table in memory:

```asm
    .align 64               # BASE must be 64-byte aligned in vectored mode
vector_table:
    j  handle_user_sw_int    # cause 0: user software interrupt
    j  handle_super_sw_int   # cause 1: supervisor software interrupt
    .word 0                  # cause 2: reserved
    j  handle_mach_sw_int    # cause 3: machine software interrupt
    j  handle_user_timer     # cause 4: user timer interrupt
    j  handle_super_timer    # cause 5: supervisor timer interrupt
    .word 0                  # cause 6: reserved
    j  handle_mach_timer     # cause 7: machine timer interrupt
    ...
```

> Note: vectoring only applies to **interrupts**. Exceptions always jump to BASE in both modes.

## Alignment Requirements

- **Direct mode**: BASE must be 4-byte aligned (bits [1:0] == 0).
- **Vectored mode**: the RISC-V spec requires BASE to be aligned to the total size of the vector table, or at minimum 4-byte aligned; many implementations require 64-byte or 256-byte alignment. Check your target's implementation notes.

## Configuring mtvec

```asm
    la    t0, trap_entry     # load address of handler
    # For direct mode, just write it:
    csrw  mtvec, t0          # MODE = 0 (direct) because bottom 2 bits are 0

    # For vectored mode, set bit 0:
    la    t0, vector_table
    ori   t0, t0, 1          # MODE = 1 (vectored)
    csrw  mtvec, t0
```

Reading back `mtvec` and masking off the MODE bits recovers the BASE address:

```asm
    csrr  t0, mtvec
    andi  t1, t0, 3          # t1 = MODE
    andi  t0, t0, ~3         # t0 = BASE (mask bottom 2 bits)
```

## Choosing Direct vs. Vectored

| Criterion | Direct | Vectored |
|-----------|--------|----------|
| Code size | Smaller (one handler) | Larger (jump table) |
| Dispatch latency | Higher (software switch) | Lower (hardware dispatch) |
| Exception handling | Same as interrupts | Same as direct |
| Best for | Simple bare-metal, RTOS | High-performance interrupt handling |

For an RTOS with many interrupt sources, vectored mode reduces latency by eliminating the software-dispatch branch. For simple embedded firmware, direct mode with a software switch is easier to maintain.

## Common Pitfalls

- **Unaligned BASE**: if BASE is not properly aligned for the chosen MODE, behavior is implementation-defined — often a lockup.
- **Writing mtvec too late**: any trap before `mtvec` is configured jumps to address 0 (or whatever reset left in the register), usually crashing.
- **Forgetting that exceptions are never vectored**: even in vectored mode, `ecall`, page faults, and illegal instructions all land at BASE.

> **Interview answer:** `mtvec` holds the trap handler base address in its upper bits and a 2-bit MODE field. MODE 0 (direct) sends all traps to BASE; MODE 1 (vectored) sends interrupt N to BASE + 4*N but always sends exceptions to BASE.
