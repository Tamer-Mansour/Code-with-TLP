# Quiz: Debugging, Tooling, and Diagnostics

Test your understanding of the debugging tools and techniques covered in this module.

---

**Q1. You compile a program with `g++ -O2 -o app app.cpp` and try to inspect a local variable in gdb. gdb reports `<optimized out>`. What is the most direct fix?**

- [ ] Use `valgrind --track-origins=yes` instead of gdb
- [ ] Add `-DDEBUG` to re-enable the variable
- [x] Recompile with `-g -O0` (or at least `-Og`) to disable optimizations and add debug symbols
- [ ] Run `strip --remove-section=.debug_info app` to restore the symbols

The `-O2` flag allows the compiler to eliminate variables from the binary. `-g` adds symbol information, but without `-O0` or `-Og`, variables may still be optimized away and show as `<optimized out>` in gdb.

---

**Q2. A program crashes with `SIGSEGV`. You load the core dump into gdb and type `bt`. Frame 0 is inside `__strcpy_avx` in libc and frame 1 is in your function `copy_name` at line 88. What should you do next?**

- [ ] File a bug against glibc — it is the one that crashed
- [ ] Recompile libc with `-g` to debug frame 0
- [x] Type `frame 1` to jump to your code, then `print` the source and destination pointers to find the invalid argument
- [ ] Run the program again with `valgrind --tool=callgrind`

The crash is inside a library function but caused by invalid arguments from your code. `frame 1` moves to your code; inspecting the pointer arguments there reveals whether they are null, uninitialized, or point to freed memory.

---

**Q3. Which sanitizer is the correct choice for detecting a data race between two threads modifying a shared integer without a mutex?**

- [ ] AddressSanitizer (`-fsanitize=address`)
- [ ] UndefinedBehaviorSanitizer (`-fsanitize=undefined`)
- [ ] LeakSanitizer (`-fsanitize=leak`)
- [x] ThreadSanitizer (`-fsanitize=thread`)

ThreadSanitizer instruments all memory accesses and synchronization operations to detect concurrent accesses where at least one is a write and no lock is held. ASan detects memory corruption, UBSan detects undefined behavior, and LSan detects leaks — none of them track thread synchronization.

---

**Q4. You run `valgrind --leak-check=full ./app` and see the line `definitely lost: 4,096 bytes in 1 blocks`. What does "definitely lost" mean?**

- [ ] The memory was freed but then accessed again
- [ ] A pointer to the memory exists but points to the interior, not the base
- [x] No pointer to this allocation exists anywhere in the program at exit — it is unreachable and cannot be freed
- [ ] The memory was freed twice

"Definitely lost" means valgrind searched every writable memory location and found no pointer that leads to the start of this block. It is the most severe category and represents a true leak. "Possibly lost" means an interior pointer exists; "still reachable" means a live pointer exists but `free` was never called.

---

**Q5. What does the compiler flag `-Werror` do, and why is it typically used in CI pipelines but not always in local development?**

- [ ] Enables all error-detecting warnings across the codebase
- [ ] Converts runtime errors into compile-time assertions
- [x] Treats every compiler warning as a hard compile error, which prevents new warnings from being merged but can slow iteration locally when developing
- [ ] Enables UBSan at compile time so undefined behavior aborts with an error

`-Werror` makes the compiler exit with a non-zero status code on any warning, causing the build to fail. In CI this enforces a zero-warning policy. During local development it can be frustrating because a warning in unfinished code blocks compilation entirely.

---

**Q6. You want to enable core dumps for a process on Linux. Which command must you run before starting the program, and what file does the OS write when the process crashes?**

- [ ] `export CORE_DUMP=1`; the OS writes `/var/log/core.log`
- [ ] `sysctl -w kernel.dumpable=1`; the OS writes `/proc/<pid>/core`
- [x] `ulimit -c unlimited`; the OS writes a file named according to `/proc/sys/kernel/core_pattern` (e.g., `core` or `core.<pid>` in the process working directory)
- [ ] `strace -e signal ./app`; strace captures the core dump automatically

`ulimit -c 0` (the default) suppresses core dumps. Setting it to `unlimited` allows dumps of any size. The filename and path come from `kernel.core_pattern`; by default it is simply `core` in the current directory.
