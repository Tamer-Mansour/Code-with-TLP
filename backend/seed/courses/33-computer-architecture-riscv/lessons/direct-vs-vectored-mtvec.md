# Direct vs Vectored Mode in mtvec

The `mtvec` CSR (Machine Trap Vector base-address register) controls where the processor jumps when a trap is taken. Its two-bit `MODE` field gives system designers a choice between a single centralized handler and a per-interrupt jump table.

## mtvec Layout

```
 XLEN-1                    2  1  0
┌─────────────────────────────┬────┐
│          BASE               │MODE│
└─────────────────────────────┴────┘
```

- **BASE** (bits XLEN-1:2) — the 4-byte-aligned base address of the trap handler or vector table. Always naturally aligned.
- **MODE** (bits 1:0) — selects Direct (0) or Vectored (1). Values 2 and 3 are reserved.

Reading `mtvec`:

```asm
csrr  t0, mtvec       # t0 = full mtvec value
andi  t1, t0, 3       # t1 = MODE (0 or 1)
li    t2, ~3
and   t0, t0, t2      # t0 = BASE (low 2 bits cleared)
```

## Direct Mode (MODE = 0)

In Direct mode **all** traps — exceptions and interrupts — jump to the same address: `BASE`.

```
Any trap → PC = BASE
```

The handler is responsible for reading `mcause` and dispatching to appropriate code:

```asm
.align 4
_trap_handler:            # BASE points here
    csrr  t0, mcause
    bltz  t0, interrupt_dispatch
    j     exception_dispatch
```

**Advantages:**
- Simple to configure — write one address to `mtvec`.
- Works on all RISC-V implementations.
- Handler code is entirely in software, giving full flexibility.

**Disadvantages:**
- Every trap pays the cost of a software dispatch (read `mcause`, branch).
- Latency-sensitive interrupt paths must still branch to the right ISR.

## Vectored Mode (MODE = 1)

In Vectored mode **interrupts** jump to `BASE + 4 × cause_code`. **Exceptions still jump to `BASE`** regardless of cause.

```
Exception      → PC = BASE
Interrupt N    → PC = BASE + 4*N
```

This means the first word at each offset is typically a jump instruction directly to the ISR:

```asm
.align 64             # BASE must be aligned to at least 64 bytes
                      # when using vectored mode with many interrupt codes
_vec_table:
    j  _exception_handler      # BASE + 0  (exceptions; also interrupt 0 if used)
    j  _ssoft_isr              # BASE + 4  (supervisor software interrupt, code 1)
    .word 0                    # BASE + 8  (reserved, code 2)
    j  _msoft_isr              # BASE + 12 (machine software interrupt, code 3)
    .word 0                    # BASE + 16 (reserved, code 4)
    j  _stimer_isr             # BASE + 20 (supervisor timer interrupt, code 5)
    .word 0                    # BASE + 24 (reserved, code 6)
    j  _mtimer_isr             # BASE + 28 (machine timer interrupt, code 7)
    .word 0                    # BASE + 32 (reserved, code 8)
    j  _sext_isr               # BASE + 36 (supervisor external interrupt, code 9)
    .word 0                    # BASE + 40 (reserved, code 10)
    j  _mext_isr               # BASE + 44 (machine external interrupt, code 11)
```

**Advantages:**
- Hardware directly computes the jump target — no `mcause` read needed at the dispatch point.
- Reduces interrupt latency by one branch and one CSR read.
- Clean separation of ISRs at the table level.

**Disadvantages:**
- The vector table layout is dictated by the ISA cause codes, not by priority.
- BASE alignment requirements grow with the number of interrupt sources.
- Exceptions still use BASE, so a dispatcher is still needed there.

## Alignment Requirements

The RISC-V spec requires `BASE` to be aligned to a 4-byte boundary for Direct mode. For Vectored mode implementations often require higher alignment (e.g., 64-byte or 256-byte) so the 4×N offsets do not wrap around. Always check your implementation's alignment requirement before writing `mtvec`.

```c
// Setting mtvec in C (using GCC RISC-V intrinsics)
#define MTVEC_MODE_DIRECT   0UL
#define MTVEC_MODE_VECTORED 1UL

// Direct mode
__asm__ volatile("csrw mtvec, %0"
    :: "r"((uintptr_t)_trap_handler | MTVEC_MODE_DIRECT));

// Vectored mode (vector table must be aligned)
__asm__ volatile("csrw mtvec, %0"
    :: "r"((uintptr_t)_vec_table | MTVEC_MODE_VECTORED));
```

## Choosing Between Modes

| Scenario | Recommended Mode |
|---|---|
| Bare-metal firmware, few interrupt sources | Direct — simpler |
| Real-time system with strict interrupt latency | Vectored — lower latency |
| OS kernel with many device interrupts | Often Vectored for timer/soft; PLIC handles the rest via a single external ISR |
| Simulator or academic exercise | Direct — easier to debug |

> **Interview answer:** `mtvec` MODE 0 (Direct) sends all traps to BASE, requiring software dispatch via `mcause`. MODE 1 (Vectored) sends interrupts to BASE + 4×cause, letting hardware index directly to the ISR while exceptions still go to BASE. Vectored mode reduces interrupt latency at the cost of a fixed vector table layout.

## Common Pitfalls

- Forgetting that **exceptions always go to BASE** even in Vectored mode — placing ISR code at BASE without an exception dispatcher corrupts exception handling.
- Under-aligning the vector table causes the low bits of `mtvec` to encode an unintended MODE value.
- Writing 1 to MODE on hardware that does not support Vectored mode — the hardware may silently round to 0 or produce unpredictable behavior. Always verify MODE was accepted by reading `mtvec` back.
