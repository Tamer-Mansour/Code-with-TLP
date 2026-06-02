# mcause: Identifying the Trap Cause

`mcause` (machine cause register, CSR 0x342) is written by the hardware on every trap to indicate why the trap occurred. A single bit distinguishes interrupts from exceptions; the remaining bits encode the specific cause.

## Register Layout

```
 XLEN-1                    0
 ┌───┬─────────────────────┐
 │ I │    Exception Code   │
 └───┴─────────────────────┘
```

- **Bit XLEN-1 (the "interrupt bit")**: 1 = interrupt, 0 = exception.
- **Bits [XLEN-2:0] (exception code)**: a non-negative integer identifying the specific cause.

In RV32, XLEN=32 so the interrupt bit is bit 31. In RV64, it is bit 63.

## Standard Exception Codes (interrupt bit = 0)

| Code | Exception |
|------|-----------|
| 0    | Instruction address misaligned |
| 1    | Instruction access fault |
| 2    | Illegal instruction |
| 3    | Breakpoint (EBREAK) |
| 4    | Load address misaligned |
| 5    | Load access fault |
| 6    | Store/AMO address misaligned |
| 7    | Store/AMO access fault |
| 8    | Environment call from U-mode |
| 9    | Environment call from S-mode |
| 11   | Environment call from M-mode |
| 12   | Instruction page fault |
| 13   | Load page fault |
| 15   | Store/AMO page fault |

## Standard Interrupt Codes (interrupt bit = 1)

| Code | Interrupt |
|------|-----------|
| 1    | Supervisor software interrupt |
| 3    | Machine software interrupt |
| 5    | Supervisor timer interrupt |
| 7    | Machine timer interrupt |
| 9    | Supervisor external interrupt |
| 11   | Machine external interrupt |

Platform-specific (e.g., PLIC) interrupts use codes ≥ 16.

## Reading and Decoding mcause

```asm
csrr   t0, mcause

# Test the interrupt bit
bltz   t0, is_interrupt   # branch if bit XLEN-1 is set (signed < 0)

# Exception path: extract code
# Bottom XLEN-1 bits already hold the code (bit 31/63 == 0)
li     t1, 8
beq    t0, t1, ecall_umode    # code 8 = ecall from U-mode
li     t1, 11
beq    t0, t1, ecall_mmode    # code 11 = ecall from M-mode
j      other_exception

is_interrupt:
# Clear the interrupt bit to get the code
slli   t0, t0, 1
srli   t0, t0, 1              # arithmetic trick; or:
# li   t1, (1 << 31); xor t0, t0, t1  # XOR away bit 31 (RV32)
li     t1, 7
beq    t0, t1, timer_isr      # code 7 = machine timer interrupt
```

In C (bare-metal):

```c
#include <stdint.h>

void trap_handler(void) {
    uintptr_t cause = read_csr(mcause);
    int       is_irq = (intptr_t)cause < 0;          // signed test
    unsigned  code   = cause & ~(1UL << (sizeof(uintptr_t)*8 - 1));

    if (is_irq) {
        switch (code) {
            case 7:  machine_timer_isr();   break;
            case 11: machine_extern_isr();  break;
            default: unknown_interrupt();   break;
        }
    } else {
        switch (code) {
            case 8: case 9: case 11: syscall_handler(); break;
            case 2:  illegal_insn_handler(); break;
            default: fatal_exception(code); break;
        }
    }
}
```

## Why the Signed Test Works

Treating `mcause` as a **signed** integer is the canonical way to check the interrupt bit without knowing XLEN at compile time. When the interrupt bit (the MSB) is 1, the signed value is negative, so `bltz` / `(intptr_t)cause < 0` catches all interrupts on both RV32 and RV64 with no magic constants.

## mcause on Reset

After reset, `mcause` is implementation-defined (often 0). Software should not rely on its value without first triggering a trap.

## Common Pitfalls

- **Treating mcause as purely unsigned**: you miss the elegant signed-negative shortcut for interrupt detection.
- **Forgetting that ecall has three codes** (8=U, 9=S, 11=M): a handler that only checks for code 8 will silently miss M-mode self-ecalls.
- **Assuming codes are contiguous**: the standard leaves gaps (e.g., code 10 is reserved) and platforms add custom codes ≥ 16. Always use explicit comparisons.

> **Interview answer:** `mcause` uses its most-significant bit to distinguish interrupts (1) from exceptions (0), and the remaining bits encode the specific cause number. Reading it as a signed integer lets you test "is this an interrupt?" with a single negative check, regardless of whether you are on RV32 or RV64.
