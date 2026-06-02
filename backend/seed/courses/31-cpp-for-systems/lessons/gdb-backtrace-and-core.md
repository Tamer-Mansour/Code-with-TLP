# gdb Backtraces and Examining Memory

A backtrace is the most important piece of information after a crash. It tells you exactly what sequence of function calls led to the fault. This lesson goes deeper into reading backtraces, navigating frames, and using gdb's memory examination tools to understand what the program's memory contained at the point of failure.

## Reading a Backtrace

When a program crashes or hits a breakpoint, type `bt` (or `backtrace`) to see the call stack:

```
(gdb) bt
#0  free (ptr=0x602048) at malloc.c:2934
#1  0x0000000000401182 in destroy_node (node=0x602040) at tree.cpp:88
#2  0x00000000004012a0 in remove_subtree (root=0x602040) at tree.cpp:115
#3  0x0000000000401350 in main () at tree.cpp:201
```

- Frame `#0` is the innermost (current) function — where execution stopped.
- Frame `#3` is `main()` — the outermost caller in this trace.
- Each frame shows the function name, argument values, source file, and line number.

Read from bottom to top to understand causality: `main` called `remove_subtree`, which called `destroy_node`, which called `free` with a bad pointer.

## Navigating Frames

```
(gdb) frame 2               # jump to remove_subtree frame
(gdb) info locals            # local variables in that frame
(gdb) info args              # function arguments in that frame
(gdb) list                   # show source code around current line
```

Jumping to a specific frame lets you inspect the local state at every level of the call chain — not just at the crash site.

```
(gdb) frame 3               # switch to main()
(gdb) print root             # inspect the pointer passed to remove_subtree
$1 = (Node *) 0x602040
(gdb) print *root            # dereference — see the struct contents
$2 = {value = 42, left = 0x0, right = 0x602090, refcount = 0}
```

## Examining Memory Directly

The `x` (examine) command reads raw memory at any address:

```
x/[count][format][size] address
```

| Format | Meaning |
|--------|---------|
| `x` | Hexadecimal |
| `d` | Decimal |
| `u` | Unsigned decimal |
| `o` | Octal |
| `t` | Binary |
| `s` | Null-terminated string |
| `i` | Machine instructions |

| Size | Meaning |
|------|---------|
| `b` | 1 byte |
| `h` | 2 bytes (halfword) |
| `w` | 4 bytes (word) |
| `g` | 8 bytes (giant) |

```
(gdb) x/8xw 0x602040        # 8 words in hex starting at 0x602040
0x602040:  0x0000002a  0x00000000  0x00602090  0x00000000
0x602050:  0x00000000  0x00000000  0x00000000  0x00000000
```

```
(gdb) x/s 0x400698           # print memory as a C string
0x400698:  "Hello, World!"
```

```
(gdb) x/5i $pc               # disassemble 5 instructions at instruction pointer
```

## Displaying Registers

```
(gdb) info registers         # all CPU registers
(gdb) print $rsp             # stack pointer
(gdb) print $rip             # instruction pointer (current PC on x86-64)
(gdb) print $rbp             # base pointer (frame pointer)
```

This is useful when debugging at the assembly level or analyzing stack corruption.

## Pretty-Printing Structures

gdb can display complex types automatically:

```
(gdb) print v                # std::vector
$1 = std::vector of length 3, capacity 4 = {10, 20, 30}

(gdb) print m                # std::map
$2 = std::map with 2 elements = {["alpha"] = 1, ["beta"] = 2}
```

If pretty-printers are not loaded automatically, install the libstdc++ gdb helpers:

```bash
# Usually included with GCC; activate in ~/.gdbinit:
python import sys; sys.path.insert(0, '/usr/share/gcc/python')
python from libstdcxx.v6.printers import register_libstdcxx_printers
python register_libstdcxx_printers(None)
```

## Worked Example: Heap Corruption Diagnosis

```cpp
struct Buffer {
    int  magic;    // should always be 0xDEADBEEF
    char data[16];
    int  checksum;
};
```

After a crash inside a checksum function:

```
(gdb) frame 1
(gdb) print *buf
$1 = {magic = 1735289172, data = "AAAAAAAAAAAAAAAA\000", checksum = 1094795585}

(gdb) print/x buf->magic
$2 = 0x676e6f57   # "Wnog" in ASCII — not 0xDEADBEEF
```

The magic value has been overwritten with ASCII characters — a strong sign that a string was written past the end of an adjacent buffer, corrupting this struct.

```
(gdb) x/32xb buf - 16       # look at memory before the struct
```

This technique of examining surrounding memory often reveals the source of a corruption.

## gdb Scripting

Automate repetitive inspection with `define`:

```
(gdb) define pnode
>   print *((Node*)$arg0)
>   print ((Node*)$arg0)->left
>   print ((Node*)$arg0)->right
> end
(gdb) pnode 0x602040
```

Or write a `.gdbinit` file in the project directory to auto-load breakpoints and pretty-printers each session.

> **Interview answer:** `bt` shows the call chain at crash time; `frame N` jumps to any level so you can inspect local variables with `info locals`; `x/Nformat addr` reads raw memory in any format. Together these let you reconstruct exactly what the program's state was the moment it failed.
