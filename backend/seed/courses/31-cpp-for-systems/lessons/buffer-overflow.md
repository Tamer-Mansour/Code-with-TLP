# Buffer Overflow: Heap and Stack

A **buffer overflow** happens when a write exceeds the bounds of an allocated region and overwrites adjacent memory. It is one of the oldest and most exploited vulnerability classes in systems software.

## Stack Buffer Overflow

Stack memory holds local variables, saved registers, and the return address of the current function. When a local array is overwritten past its end, the excess bytes overwrite that metadata.

```cpp
void greet(const char* name) {
    char buf[16];
    strcpy(buf, name);   // no bounds check — classic vulnerability
    printf("Hello, %s\n", buf);
}

int main() {
    greet("A very long name that is way longer than 16 bytes!!");
}
```

**Memory layout on the stack (simplified):**

```
Low address
┌────────────┐
│  buf[0..15]│  ← local buffer
├────────────┤
│  saved rbp │  ← frame pointer
├────────────┤
│  ret addr  │  ← where to jump after return
└────────────┘
High address
```

If `name` is 50 bytes, `strcpy` writes through `buf`, over `saved rbp`, and into `ret addr`. When the function returns, the CPU jumps to a corrupted address. An attacker who controls `name` can set the return address to shellcode.

## Heap Buffer Overflow

Heap overflows overwrite adjacent heap objects. Because heap blocks include allocator metadata (size, flags, free-list pointers), corrupting them can be leveraged to write arbitrary values to arbitrary addresses.

```cpp
int* arr = new int[4];
arr[4] = 0xdeadbeef;   // overflows into allocator metadata or next block
delete[] arr;           // allocator now processes corrupt metadata → crash or exploit
```

Heap overflows are harder to trigger reliably but harder to detect — they often corrupt silently until `delete` or a future `malloc` processes the mangled metadata.

## Safe Alternatives

| Unsafe function | Safe replacement |
|---|---|
| `strcpy(dst, src)` | `strncpy` / `strlcpy` / `std::string` |
| `gets(buf)` | `fgets(buf, sizeof buf, stdin)` |
| `sprintf(buf, fmt, ...)` | `snprintf(buf, sizeof buf, fmt, ...)` |
| Raw `new T[n]` | `std::vector<T>` with `.at(i)` |

`std::vector::at()` throws `std::out_of_range` instead of overflowing. In performance-critical paths use the checked debug build, then switch to `operator[]` only when correctness is proven.

## Stack Canaries

Compilers insert a random **stack canary** value between local buffers and the return address:

```
┌────────────┐
│  buf[0..15]│
├────────────┤
│  canary    │  ← random value written at function entry
├────────────┤
│  ret addr  │
└────────────┘
```

Before returning, the compiler checks that the canary is unchanged. If overwritten, the program calls `__stack_chk_fail` and aborts instead of jumping to attacker-controlled code.

Enable with:
```bash
g++ -fstack-protector-strong my_file.cpp -o my_prog
```

## ASLR and DEP/NX

Modern OS mitigations make exploiting overflows harder:

- **ASLR (Address Space Layout Randomization):** randomizes stack, heap, and library base addresses so an attacker cannot predict where to redirect control flow.
- **NX/DEP (No-Execute / Data Execution Prevention):** marks stack and heap pages non-executable, preventing injected shellcode from running.

These are mitigations, not fixes. The underlying overflow is still UB and still corrupts memory.

## Detection

```bash
# Compile with ASan to catch overflows at runtime
g++ -fsanitize=address -g -O1 prog.cpp -o prog
./prog
# ==ERROR: AddressSanitizer: stack-buffer-overflow on address ...
```

ASan wraps allocations with "red zones" — poisoned shadow memory that triggers immediately when overflowed, before corruption propagates.

## Key Takeaway

> **Interview answer:** A buffer overflow writes past the end of a buffer into adjacent memory. Stack overflows can corrupt the return address and enable code execution; heap overflows corrupt allocator metadata or adjacent objects. Mitigations include bounds-checked containers, stack canaries, ASLR, and NX, but the root fix is eliminating unbounded writes.
