# OS Security and Protection

An operating system is the final arbiter of what code can do on a machine. Security in OS design means ensuring that processes cannot exceed their authorized capabilities — even when software contains bugs. This lesson covers the main protection mechanisms, common attack vectors, and OS-level defenses.

## Protection Rings and Privilege Levels

Modern CPUs enforce privilege through hardware **protection rings** (also called privilege levels or CPL on x86):

```
Ring 0  (most privileged)  ─── OS Kernel, device drivers
Ring 1                     ─── (Historically: OS services; mostly unused on modern OSes)
Ring 2                     ─── (Historically: OS services; mostly unused on modern OSes)
Ring 3  (least privileged) ─── User applications (your programs)
```

The x86-64 architecture uses only rings 0 and 3 in practice. A process in ring 3 **cannot** execute privileged instructions (like `LGDT`, `LIDT`, `IN`, `OUT`) — attempting them generates a General Protection Fault (GPF), which the OS handles by sending SIGSEGV to the offending process.

The ring transition from 3 → 0 happens only through a controlled gate: a **system call** (via `SYSCALL`/`SYSENTER` instructions or a software interrupt like `int 0x80`). The CPU validates the transition and jumps to a known kernel entry point.

## Access Control

### Access Control Matrix

The theoretical model: a matrix where rows are **subjects** (users, processes) and columns are **objects** (files, devices, memory regions). Each cell lists the permitted operations:

```
         File A    File B    Socket    Printer
Alice    r, w      r         connect   print
Bob      r         r, w      ---       ---
Kernel   r,w,x     r,w,x     all       all
```

This matrix is never stored whole (too large), but it is the conceptual foundation for:

### Access Control Lists (ACLs)

Store the matrix **column-wise**: each object stores a list of (subject, permissions) pairs.

```bash
# Linux extended ACL on a file
getfacl report.txt
# user::rw-
# user:alice:rw-
# user:bob:r--
# group::r--
# mask::rw-
# other::---
```

ACLs are expressive but expensive to check for every access (scan the list).

### Capability Lists

Store the matrix **row-wise**: each process holds a list of unforgeable **capabilities** (tokens) that represent permitted operations on specific objects. The process presents its capability when accessing an object.

```
Process (Alice):
  cap[0] = (File A, read | write)
  cap[1] = (Socket 8080, connect)
```

Capabilities cannot be forged (kernel-managed). Easy to transfer (give a capability to another process = delegate access). Used in microkernel designs (seL4, QNX) and modern OS features like Linux file descriptor passing over Unix sockets.

### Linux DAC (Discretionary Access Control)

Linux's traditional model: every file has an owner (UID), a group (GID), and three permission triplets (owner, group, other) each with read/write/execute bits. The kernel checks these on every `open()`, `exec()`, etc.

```bash
ls -la secret.txt
# -rw-r----- 1 alice devteam 1024 Jun 01 secret.txt
#  ^^^  Owner: alice (rw-), group devteam (r--), others (---)
```

### Linux MAC: SELinux and AppArmor

**Mandatory Access Control (MAC)** policies are enforced by the kernel regardless of file permissions. SELinux labels every process and file with a type; a policy defines which type-to-type transitions are allowed.

```
# SELinux denies nginx from reading /etc/shadow even if file permissions allow it
nginx_t → shadow_t:file:read → DENIED by policy
```

## Common Attack Vectors

### Buffer Overflow

The classic vulnerability: writing past the end of a stack-allocated array overwrites adjacent memory — including the saved return address:

```c
void vulnerable(char *input) {
    char buf[64];
    strcpy(buf, input);  // No bounds check! If input > 64 bytes, overflow.
}
// Stack layout:
//  [buf (64 bytes)] [saved rbp (8)] [return address (8)]
//                                          ^
//                          attacker overwrites this with shellcode address
```

The attacker controls what address the function returns to — typically shellcode injected into the buffer itself.

### Return-to-libc (ret2libc)

A refinement that avoids injecting shellcode (which is blocked by NX/DEP): instead of returning to injected code, return to existing libc functions like `system("/bin/sh")`. Because `system()` is always mapped into the process, its address is predictable in the absence of ASLR.

### Return-Oriented Programming (ROP)

Even more powerful: chain together small existing code sequences ending in `RET` (called **gadgets**). Each gadget does a small operation (load register, add, system call), and the attacker constructs a full attack by linking gadgets. ROP defeats NX/DEP because the code being executed was always present in memory — no injection needed.

## OS Defenses

### Address Space Layout Randomization (ASLR)

The OS maps the stack, heap, libraries, and executable to **random virtual addresses** on each execution:

```
Without ASLR:    libc always at 0x7ffff7a00000 → attacker can hardcode ret2libc address
With ASLR:       libc at random offset each run → attacker cannot predict the address
```

- Linux: `echo 2 > /proc/sys/kernel/randomize_va_space` (2 = full randomization)
- 64-bit ASLR provides ~128 bits of randomness for the stack → brute-force infeasible
- 32-bit ASLR: only ~16 bits of entropy → still brute-forceable in ~65,536 attempts

### Stack Canaries

The compiler inserts a random **canary value** between local variables and the saved return address. Before returning, the function checks if the canary was modified:

```
Stack:  [buf] [CANARY: 0x5a4b3c2d] [saved rbp] [return address]
                     ^
        If attacker overwrites buf past this point, canary is corrupted.
        check_canary() calls abort() → crash before ret executes.
```

GCC: `-fstack-protector-strong` (enabled by default in most distros).

### NX/DEP (Non-Executable Memory / Data Execution Prevention)

Memory pages are marked either **executable** (code) or **writable** (data), but never both. The CPU enforces this with the NX bit (x86: bit 63 of the page table entry):

```
Stack pages: writable, NOT executable → shellcode in the stack won't run
Code pages:  executable, NOT writable  → cannot overwrite code
```

Implemented via the x86 PAE or 64-bit page tables. Defeats classic buffer-overflow shellcode injection but not ROP.

### ASLR + NX + Canaries Together

Modern systems layer all three defenses:
- ASLR makes addresses unpredictable → ROP gadget addresses unknown
- NX ensures no injected data executes as code
- Canaries detect stack corruption before the return

Together these raise the bar substantially. Complete bypasses require information-disclosure vulnerabilities (to leak addresses and defeat ASLR) combined with ROP gadget construction.

## Key Takeaways

- **Protection rings** enforce the user/kernel privilege boundary in hardware; ring 3 code cannot execute privileged instructions.
- **ACLs** store permissions per-object (column of the access control matrix); **capabilities** store them per-process (row).
- Linux uses DAC (owner/group/other bits + ACLs) and optionally MAC (SELinux/AppArmor).
- **Buffer overflow** → **ret2libc** → **ROP** form an escalating ladder of attack sophistication.
- **ASLR** randomizes memory layout; **NX/DEP** marks data pages non-executable; **stack canaries** detect overflow before return — all three should be deployed together.

## Further Reading

- OSTEP Chapter 37 — File System Security: https://pages.cs.wisc.edu/~remzi/OSTEP/
- MIT 6.828 — Security lectures and labs: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/
