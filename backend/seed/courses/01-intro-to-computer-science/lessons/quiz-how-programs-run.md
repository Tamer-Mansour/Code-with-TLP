# Quiz: How Programs Run

**Q1. What does the Program Counter (PC) hold?**
- [ ] The total number of instructions executed so far
- [x] The memory address of the next instruction to fetch
- [ ] The result of the most recent arithmetic operation
- [ ] The current call stack depth

**Q2. What is the correct order of the fetch-execute cycle?**
- [ ] Execute → Fetch → Decode → Write-back
- [x] Fetch → Decode → Execute → Write-back
- [ ] Decode → Fetch → Execute → Write-back
- [ ] Fetch → Execute → Decode → Write-back

**Q3. Which memory region holds local variables and function call frames?**
- [ ] Text (code) segment
- [ ] Heap
- [ ] Data segment
- [x] Stack

**Q4. What is the main advantage of a JIT (Just-In-Time) compiler over a pure interpreter?**
- [ ] It removes the need for source code
- [ ] It makes programs portable across all platforms
- [x] It compiles frequently-run hot paths to native machine code at runtime for faster execution
- [ ] It catches more errors at compile time

**Q5. Python compiles source code to _______ before the CPython VM runs it.**
- [ ] Native x86 machine code
- [ ] Assembly language
- [x] Bytecode (.pyc files)
- [ ] JavaScript

**Q6. Which of the following languages uses ahead-of-time compilation to native machine code?**
- [ ] Python (CPython)
- [ ] JavaScript (in a browser)
- [x] C (with GCC)
- [ ] Java (standard JVM)

**Q7. A buffer overflow vulnerability typically occurs when:**
- [ ] A program requests more RAM than the OS allows
- [ ] A floating-point computation overflows to infinity
- [x] Writing past the end of a fixed-size buffer overwrites adjacent memory, potentially hijacking control flow
- [ ] The heap and stack sizes exceed available RAM

**Q8. Why does Python run slower than equivalent C code for CPU-intensive tasks?**
- [ ] Python uses more registers than C
- [ ] Python programs are larger binary files
- [x] Python adds bytecode interpretation overhead plus dynamic typing with heap-allocated objects for every value
- [ ] Python cannot use multi-core processors
