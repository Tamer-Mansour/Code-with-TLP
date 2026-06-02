# Address Binding: Compile, Load, and Execution Time

A machine instruction ultimately contains a numeric address. **Address binding** is the act of assigning a final numeric address to a symbolic reference (variable name, function name, label). The question is *when* that binding happens, and the answer has deep implications for portability, security, and runtime flexibility.

## The Three Binding Times

### 1. Compile Time

The compiler translates source symbols into addresses, assuming the program will always be placed at a **fixed location** in memory.

```asm
; Compiler knows 'counter' is at absolute address 0x601020
mov eax, [0x601020]    ; hardcoded absolute address
```

- Used in the earliest operating systems and still in some embedded targets with no OS.
- If the program must be loaded elsewhere (e.g., another program is already at that address), it **cannot run without modification**.
- Produces a non-position-independent binary.

### 2. Load Time

The program is compiled with **relocatable addresses** — placeholders relative to a base address. The **linker/loader** resolves them when the binary is placed in memory.

```
Binary on disk:         Relocation table entry:
  mov eax, [BASE+0x20]  → at load time, BASE = actual load address
                         → patched to: mov eax, [0x7f3a00000020]
```

- The loader must **patch** every address reference before the first instruction executes.
- Still dominant in dynamically linked executables (GOT/PLT entries for shared libraries).
- Slower startup proportional to the number of relocations.

### 3. Execution Time (Run Time)

Binding is deferred until the instruction actually executes. This is what virtual memory enables:

- The program uses **virtual addresses** throughout.
- The MMU translates each virtual address to a physical address at the moment of access.
- The OS can **move** the program's physical pages around (e.g., for memory compaction) simply by updating the page table — no binary patching needed.

```c
// The instruction always says virtual address 0x7fff...abc0
// Physical location may change across runs (ASLR) or even at runtime
int *p = &x;   // virtual address; physical is determined by MMU at access time
```

## Position-Independent Code (PIC)

Modern shared libraries and PIE (Position-Independent Executable) binaries use **PC-relative addressing**: every reference is expressed as an offset from the current instruction pointer.

```asm
; Instead of: mov rax, [0x601020]   (absolute)
; PIC uses:   lea rax, [rip + 0x2f8a]  (relative to current RIP)
```

This means the binary can be loaded at *any* virtual address without patching — the offsets remain correct regardless. Combined with ASLR, this drastically reduces the exploitability of memory-corruption bugs.

## Summary Table

| Binding Time | When | Flexibility | Cost | Example |
|---|---|---|---|---|
| Compile time | During compilation | None — fixed address only | Zero at runtime | DOS .COM files, bare-metal firmware |
| Load time | Program startup | Medium — loaded anywhere | Relocation patching | Statically linked ELF, Windows PE |
| Execution time | Each memory access | Maximum — pages movable | TLB translation overhead | All modern OS processes via MMU |

## Worked Example: Where Does `main` Live?

```bash
# Compile without PIE (fixed load address)
gcc -no-pie -o app main.c
readelf -s app | grep main
# Typical output: 0x0000000000401130  FUNC  GLOBAL  main

# Compile with PIE (default on modern distros)
gcc -pie -o app_pie main.c
readelf -s app_pie | grep main
# Output: 0x0000000000001130  FUNC  GLOBAL  main  ← relative to load base
```

Run the PIE binary twice and check where `main` actually lands via ASLR:

```bash
python3 -c "import subprocess; [print(subprocess.check_output(
  ['bash','-c','./app_pie &>/dev/null; cat /proc/$!/maps | grep app_pie | head -1'],
  text=True)) for _ in range(2)]"
# Different base addresses each run!
```

**Common pitfall:** Assuming that a function pointer value is stable across runs. With ASLR and PIE, it is not — log the relative offset, not the absolute address, for debugging.

**Interview answer:** Address binding can happen at compile time (fixed absolute addresses), load time (relocations patched by the loader), or execution time (virtual addresses translated by the MMU on every access); modern systems use execution-time binding via the MMU combined with PIE/ASLR for maximum flexibility and security.
