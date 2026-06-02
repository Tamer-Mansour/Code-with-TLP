# Machine Mode (M-Mode)

Machine Mode is the most privileged execution level in RISC-V. Every RISC-V processor boots into M-Mode and remains there until software explicitly delegates authority to lower levels. It is the bedrock on which everything else is built.

## What Makes M-Mode Special

- **Unrestricted hardware access** — M-Mode code can read and write any physical address, configure any CSR, and execute any instruction the hardware supports.
- **First software to run** — After reset, the program counter is loaded from a platform-specific reset vector in M-Mode. There is no prior software to check permissions.
- **Owns all traps by default** — Every exception, interrupt, and system call initially traps to M-Mode. M-Mode software can then delegate selected traps to S-Mode.

## Key CSRs in M-Mode

Control and Status Registers (CSRs) are the primary interface to machine-level state.

| CSR | Purpose |
|---|---|
| `mstatus` | Global interrupt enable, previous privilege level, etc. |
| `mtvec` | Trap vector base address (where traps land) |
| `mepc` | Exception program counter — return address after trap |
| `mcause` | Reason for the most recent trap |
| `mtval` | Trap-specific value (faulting address for page faults) |
| `mie` / `mip` | Interrupt enable / interrupt pending bits |
| `medeleg` / `mideleg` | Delegate exceptions/interrupts to S-Mode |

CSR names beginning with `m` are accessible only from M-Mode. Attempting to read or write them from S-Mode or U-Mode raises an illegal instruction exception.

## Reading and Writing CSRs

RISC-V provides dedicated CSR instructions:

```asm
# Read mstatus into t0
csrr  t0, mstatus

# Set the MIE bit (bit 3) in mstatus to enable machine interrupts
csrsi mstatus, 8

# Write a new trap vector address into mtvec
la    t1, trap_handler
csrw  mtvec, t1
```

The `csrr`, `csrw`, `csrs`, and `csrc` pseudo-instructions map to `CSRRW`, `CSRRS`, and `CSRRC` hardware instructions.

## Delegation: Passing Authority Down

By default, all traps arrive at M-Mode. For a system with an OS kernel in S-Mode, it is inefficient to bounce every syscall up to M-Mode before routing it back down. The `medeleg` and `mideleg` registers let M-Mode say: "For these specific trap causes, deliver the trap directly to S-Mode."

```asm
# Delegate all synchronous exceptions to S-Mode
li    t0, 0xFFFF
csrw  medeleg, t0

# Delegate all standard interrupts to S-Mode
csrw  mideleg, t0
```

Once delegated, a trap arriving while in U-Mode or S-Mode goes directly to S-Mode's `stvec` handler without passing through M-Mode.

## Physical Memory Protection (PMP)

M-Mode controls PMP, the hardware mechanism that restricts which physical memory regions S-Mode and U-Mode code can access. PMP is crucial on systems without virtual memory (embedded RISC-V) to sandbox S-Mode and U-Mode.

```asm
# Grant full RWX access to all physical memory (open policy)
li    t0, 0x1F
csrw  pmpcfg0, t0
li    t0, -1          # all ones = top of address space
csrw  pmpaddr0, t0
```

## Common Pitfall

M-Mode cannot be entered from S-Mode by a normal call — you cannot `jal` your way into M-Mode. The only way to elevate privilege is through a trap (exception, interrupt, or `ecall`). This is intentional: every privilege escalation is hardware-mediated.

## Worked Example: Minimal M-Mode Boot Stub

```asm
_start:
    # Set trap vector
    la    t0, m_trap_handler
    csrw  mtvec, t0

    # Delegate exceptions to S-Mode
    li    t0, 0xB109        # common exception causes
    csrw  medeleg, t0

    # Set mepc to supervisor entry point
    la    t0, kernel_start
    csrw  mepc, t0

    # Set MPP=01 (Supervisor) in mstatus, then mret
    li    t0, 0x800         # MPP[1:0] = 01 at bits [12:11]
    csrw  mstatus, t0
    mret                    # jumps to kernel_start in S-Mode
```

> **Interview answer:** Machine Mode is the highest RISC-V privilege level — the first mode entered after reset — with unrestricted access to all hardware, responsible for platform initialization and delegating trap handling to the OS kernel in S-Mode.
