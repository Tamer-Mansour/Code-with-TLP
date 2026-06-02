# ECALL and EBREAK Across Modes

`ecall` and `ebreak` are two special instructions that intentionally transfer control out of the current context. They look similar but serve entirely different purposes and have distinct behaviors at each privilege level.

## ECALL — Environment Call

`ecall` is the standard mechanism for requesting a service from the next higher privilege level. It is the sole intended gateway for privilege elevation.

**Encoding:** `ecall` is a 32-bit instruction with opcode `SYSTEM` and all other fields zero. It takes no register operands.

```asm
ecall   # 32-bit encoding: 0x00000073
```

### ECALL Behavior by Source Privilege

| Executing from | Cause code in xcause | Typical use |
|---|---|---|
| U-Mode | 8 — Environment call from U-Mode | System call to OS kernel |
| S-Mode | 9 — Environment call from S-Mode | SBI call to M-Mode firmware |
| M-Mode | 11 — Environment call from M-Mode | Rare; testing or firmware self-calls |

The cause code is how the trap handler identifies that it received an `ecall` vs. some other exception.

### System Call Convention (Linux RISC-V)

```asm
# Calling open("/dev/null", O_RDONLY)
li    a7, 56          # syscall number: openat
li    a0, -100        # AT_FDCWD
la    a1, path        # filename
li    a2, 0           # O_RDONLY
li    a3, 0           # mode (ignored for O_RDONLY)
ecall
# a0 = fd on success, or -errno on failure
```

The kernel dispatch table maps `a7` to the correct handler. Arguments follow the integer ABI: `a0`–`a5`, return value in `a0`.

### SBI Call Convention (S-Mode to M-Mode)

```asm
# sbi_set_timer(stime_value)
li    a7, 0x54494D45  # SBI extension: TIME
li    a6, 0           # SBI function: set_timer
mv    a0, s0          # next timer deadline
ecall
# a0 = SBI error code, a1 = SBI value
```

OpenSBI dispatches on `a7` (extension ID) and `a6` (function ID) and returns structured results.

## EBREAK — Environment Break

`ebreak` triggers a **breakpoint exception**. It exists to hand control to a debugger or a higher-privilege monitor without terminating the program.

**Encoding:** `ebreak` shares the opcode with `ecall` but sets bit 20.

```asm
ebreak   # 32-bit encoding: 0x00100073
```

### EBREAK Use Cases

1. **Software debuggers (GDB)** — GDB replaces instructions with `ebreak` to set breakpoints. When the processor executes it, the OS or debug stub catches the breakpoint exception and signals GDB.

2. **Semi-hosting** — In bare-metal development, `ebreak` at M-Mode can be configured to transfer control to a JTAG debug interface (OpenOCD), allowing the host computer to inspect CPU state.

3. **Panic / assertion failure** — Some embedded firmware deliberately executes `ebreak` when an unrecoverable condition is detected, causing a halt that a debugger can analyze.

### EBREAK Cause Code

`ebreak` always produces cause code **3** (Breakpoint) in `xcause`, regardless of which privilege level executed it.

```c
// Kernel-side: check for breakpoint exception
if (scause == 3) {
    // Is there a ptrace-attached debugger?
    if (current_process->ptrace_attached) {
        send_signal(current_process, SIGTRAP);
    } else {
        // No debugger: kill the process
        send_signal(current_process, SIGSEGV);
    }
}
```

## Comparing ECALL and EBREAK

| Property | `ecall` | `ebreak` |
|---|---|---|
| Purpose | Request a service | Signal a breakpoint |
| Cause code | 8, 9, or 11 (depends on mode) | 3 (always) |
| Normal caller | Application, kernel | Debugger, panic code |
| sepc after trap | Points to the `ecall` itself | Points to the `ebreak` itself |
| Handler must advance sepc? | Yes (+4) | Only if execution should continue |

## Common Pitfall

Both `ecall` and `ebreak` set `sepc` (or `mepc`) to the address of the instruction itself — not the next instruction. After handling an `ecall`, the handler must add 4 to `sepc` before issuing `sret`. For `ebreak`, adding 4 is only appropriate if the debugger wants to continue execution past the breakpoint; otherwise, the handler should leave `sepc` unchanged or signal the process.

## Worked Example: Implementing assert() with EBREAK

```c
// Bare-metal assert using ebreak
#define ASSERT(cond)                          \
    do {                                      \
        if (!(cond)) {                        \
            asm volatile("ebreak");           \
        }                                     \
    } while (0)

void divide(int a, int b) {
    ASSERT(b != 0);      // fires ebreak if b == 0
    return a / b;
}
```

When the debugger catches the resulting breakpoint exception, it can inspect `a` and `b` from the register file.

> **Interview answer:** ECALL requests a service from the next higher privilege level (system call from U-Mode, SBI call from S-Mode), while EBREAK signals a breakpoint exception for debugger use; both save the trapping instruction address in sepc/mepc, so the handler must advance past ecall by +4 but may leave ebreak's address unchanged.
