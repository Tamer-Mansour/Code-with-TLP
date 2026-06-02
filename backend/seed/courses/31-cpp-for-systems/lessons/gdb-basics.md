# gdb: Breakpoints, Stepping, and Inspecting State

gdb (the GNU Debugger) is the standard interactive debugger for C and C++ programs on Linux. Learning its core commands lets you pause a running program at any point, inspect every variable, and step through execution one instruction at a time. This is fundamentally more powerful than `printf` debugging.

## Starting a Session

Always compile with `-g` before debugging:

```bash
g++ -g -O0 -o server server.cpp
gdb ./server
```

To debug with command-line arguments:

```bash
gdb --args ./server --port 8080 --config /etc/server.conf
```

To attach to a running process:

```bash
gdb -p <pid>
```

## Breakpoints

A breakpoint pauses execution at a specific location. gdb resumes when you tell it to.

```
(gdb) break main              # break at function entry
(gdb) break server.cpp:42    # break at file:line
(gdb) break MyClass::process  # break at member function
(gdb) b connect              # 'b' is the shorthand
```

Conditional breakpoints — only pause when an expression is true:

```
(gdb) break server.cpp:42 if fd < 0
(gdb) break loop if i == 100
```

List and delete breakpoints:

```
(gdb) info breakpoints       # show all breakpoints
(gdb) delete 2               # delete breakpoint #2
(gdb) disable 1              # disable without deleting
(gdb) enable 1               # re-enable
```

## Running and Stepping

```
(gdb) run                    # start the program
(gdb) run arg1 arg2          # start with arguments
(gdb) continue               # resume after a pause (shorthand: c)
(gdb) next                   # execute next line, step OVER function calls (n)
(gdb) step                   # execute next line, step INTO function calls (s)
(gdb) finish                 # run until current function returns
(gdb) until 55               # run until line 55
```

The difference between `next` and `step` is critical: `next` treats a function call as a single step, while `step` descends into it.

## Inspecting Variables and Memory

```
(gdb) print x                # print variable x
(gdb) print *ptr             # dereference a pointer
(gdb) print arr[3]           # array element
(gdb) print obj.field        # struct/class member
(gdb) p sizeof(MyStruct)     # evaluate expressions
```

Examine raw memory with `x` (examine):

```
(gdb) x/4xw 0x7ffd1234      # 4 words in hex at address
(gdb) x/s ptr               # print as a C string
(gdb) x/16bx buf            # 16 bytes in hex
```

Format codes: `x` = hex, `d` = decimal, `b` = byte, `w` = word (4 bytes), `g` = giant (8 bytes), `s` = string, `i` = instruction.

Watchpoints — pause when a variable's value changes:

```
(gdb) watch x               # break when x is written
(gdb) rwatch x              # break when x is read
(gdb) awatch x              # break on any access
```

## Inspecting the Call Stack

```
(gdb) backtrace              # show full call stack (bt)
(gdb) frame 3               # switch to frame #3
(gdb) info locals            # all local variables in current frame
(gdb) info args              # function arguments in current frame
(gdb) up                    # move one frame up the stack
(gdb) down                  # move one frame down
```

## Worked Example: Null Pointer Crash

```cpp
// buggy.cpp
#include <cstring>

void copy_data(const char* src, char* dst) {
    strcpy(dst, src);   // crash if src or dst is null
}

int main() {
    char* buf = nullptr;
    copy_data("hello", buf);   // line 9 — crash here
    return 0;
}
```

```bash
g++ -g -O0 -o buggy buggy.cpp
gdb ./buggy
```

```
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
__strcpy_sse2_unaligned () from /lib/x86_64-linux-gnu/libc.so.6

(gdb) bt
#0  __strcpy_sse2_unaligned () from /lib/x86_64-linux-gnu/libc.so.6
#1  0x00000000004005d2 in copy_data (src=0x400698 "hello", dst=0x0)
    at buggy.cpp:5
#2  0x000000000040060e in main () at buggy.cpp:9

(gdb) frame 1
(gdb) print dst
$1 = 0x0
```

The backtrace immediately reveals that `dst` is null, and frame 2 shows exactly which line in `main` passed it that way.

## Useful Shortcuts

| Command | Shorthand | Action |
|---------|-----------|--------|
| `break` | `b` | Set breakpoint |
| `continue` | `c` | Resume execution |
| `next` | `n` | Step over |
| `step` | `s` | Step into |
| `print` | `p` | Print expression |
| `backtrace` | `bt` | Show call stack |
| `quit` | `q` | Exit gdb |

Pressing Enter with no command repeats the last command — very useful when stepping through a loop with `n` or `s`.

> **Interview answer:** Set a breakpoint with `break file:line`, run with `run`, step line by line with `next`/`step`, inspect variables with `print`, and see the call stack with `backtrace`. Conditional breakpoints (`break x if cond`) and watchpoints (`watch var`) are essential for debugging complex state corruption.
