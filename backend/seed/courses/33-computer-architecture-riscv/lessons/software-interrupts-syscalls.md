# Software Interrupts and System Calls

Not all traps come from hardware. A program can deliberately trigger a trap to request a service from a more privileged layer — this is the mechanism behind **system calls**. RISC-V provides two dedicated instructions for deliberate software traps: `ecall` and `ebreak`.

---

## Why software traps exist

User-mode code cannot directly access hardware registers, physical memory, or kernel data structures — the processor enforces privilege boundaries. A software trap voluntarily elevates privilege for the duration of a single, controlled handler invocation, then returns to user mode. This is the foundation of the OS ABI.

---

## `ecall` — Environment Call

`ecall` causes an **Environment Call** exception. The exact cause code depends on the current privilege level:

| Privilege at `ecall` | `mcause` code | Name |
|----------------------|---------------|------|
| User (U-mode)        | 8  | Environment call from U-mode |
| Supervisor (S-mode)  | 9  | Environment call from S-mode |
| Machine (M-mode)     | 11 | Environment call from M-mode |

### Linux RISC-V syscall convention

Linux uses the following register convention for system calls on RISC-V:

| Register | Purpose |
|----------|---------|
| `a7` | Syscall number |
| `a0`–`a5` | Arguments (up to 6) |
| `a0` | Return value (after handler) |
| `a1` | Second return value (e.g., `fork` parent PID) |

```asm
# write(1, buf, len) — syscall number 64 on RISC-V Linux
li    a7, 64        # __NR_write
li    a0, 1         # fd = stdout
la    a1, message   # buf
li    a2, 13        # len
ecall
# a0 now holds the return value (bytes written, or -errno)
```

### Kernel-side dispatch

```c
// Simplified kernel syscall dispatcher
void handle_ecall_from_user(struct trapframe *tf) {
    long syscall_nr = tf->regs[17];   // a7 = x17
    switch (syscall_nr) {
        case 64: tf->regs[10] = sys_write(tf->regs[10],
                                           (void*)tf->regs[11],
                                           tf->regs[12]);
                 break;
        // ...
        default: tf->regs[10] = -ENOSYS;
    }
    tf->mepc += 4;  // advance past ecall instruction
}
```

Note the `mepc += 4` — unlike page faults (which re-execute the faulting instruction), a successful `ecall` should advance past the `ecall` itself.

---

## `ebreak` — Breakpoint

`ebreak` causes a **Breakpoint** exception (`mcause = 3`). It is used by:

- **Debuggers** — GDB replaces an instruction with `ebreak` to set a software breakpoint.
- **Semihosting** — embedded firmware uses `ebreak` with a specific `a0`/`a1` convention to request services from a debug host (OpenOCD, QEMU).

```asm
ebreak   # cause mcause=3, mepc = address of this ebreak
```

A debugger's handler checks `mepc` to find which breakpoint fired, executes the replaced instruction out-of-line, then returns.

---

## Software interrupts (inter-processor interrupts)

RISC-V also supports **Machine Software Interrupts (MSI)**, which are interrupts one hart (CPU core) sends to another by writing to a memory-mapped register. Despite the name "software interrupt," they behave like hardware interrupts (asynchronous, `mcause` bit 31 set):

```
mcause = 0x80000003   # machine software interrupt
```

Used for:
- **IPI (Inter-Processor Interrupts)** — scheduler TLB shootdown, remote function call.
- **Test-and-set** synchronization primitives in multicore firmware.

```c
// Send MSI to hart 1 (CLINT base address varies by platform)
#define CLINT_BASE 0x2000000
volatile uint32_t *msip = (uint32_t *)(CLINT_BASE + 4 * 1);
*msip = 1;   // set software interrupt pending for hart 1
```

---

## Supervisor Binary Interface (SBI)

In a standard RISC-V system the firmware (OpenSBI) runs at M-mode and the OS kernel runs at S-mode. The kernel uses `ecall` (from S-mode, `mcause = 9`) to request M-mode services via the **SBI**:

```c
// SBI call: set timer (extension 0x54494D45, function 0)
struct sbiret sbi_set_timer(uint64_t stime_value) {
    register long a0 asm("a0") = stime_value;
    register long a6 asm("a6") = 0;             // function ID
    register long a7 asm("a7") = 0x54494D45;    // extension ID "TIME"
    asm volatile("ecall" : "+r"(a0) : "r"(a6), "r"(a7) : "memory");
    return (struct sbiret){ .error = a0 };
}
```

---

## Trap privilege routing

RISC-V routes traps based on delegation registers:

```
medeleg — exception delegation (M→S)
mideleg — interrupt delegation (M→S)
```

If bit N is set in `medeleg`, exception cause N is handled in S-mode directly, without passing through M-mode first. This lets the OS kernel handle page faults and syscalls without firmware involvement.

---

> **Interview answer:** `ecall` is a synchronous software trap instruction used to implement system calls — the user program places the syscall number in `a7` and arguments in `a0`–`a5`, then executes `ecall`; the kernel handler reads `mcause`, dispatches the call, writes the result to `a0`, advances `mepc` by 4, and returns with `mret`. `ebreak` is a breakpoint trap used by debuggers. Machine software interrupts (MSI) are asynchronous inter-processor signals written to memory-mapped registers.
