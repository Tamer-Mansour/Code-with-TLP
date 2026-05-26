# Compilers vs Interpreters

High-level languages like Python, Java, and C++ are convenient for humans but incomprehensible to a CPU. A **translator** must convert source code into something the hardware can execute. There are two main approaches—**compilation** and **interpretation**—and most modern languages use a blend of both.

## The Core Distinction

| | Compiler | Interpreter |
|--|---------|-------------|
| **When it translates** | All at once, before running | Line by line, while running |
| **Output** | Standalone executable binary | No permanent binary; output only |
| **Analogy** | Translating an entire book into another language before publishing | Translating a speech word-by-word in real time with a live interpreter |

## Compilers

A **compiler** reads the entire source file, analyses it, and translates it into machine code *all at once*, producing an **executable file** that can run later without the compiler being present.

```
Source code  (.c / .cpp / .rs / .go)
      ↓  Compiler  (may take seconds or minutes)
Machine code  (executable binary: .exe, ELF, Mach-O)
      ↓  Run directly on CPU
Output
```

### Steps Inside a Compiler

1. **Lexical analysis (lexing/tokenising)** — break source text into tokens: keywords (`if`, `while`), identifiers (`count`), operators (`+`), literals (`42`).
2. **Parsing (syntax analysis)** — build an **Abstract Syntax Tree (AST)** representing the grammatical structure of the program.
3. **Semantic analysis** — check types and scopes: is `x` declared before use? Can you add a string to an integer?
4. **Intermediate representation (IR)** — translate the AST to a lower-level, hardware-neutral form (LLVM IR, GCC GIMPLE). This is where many optimisations happen.
5. **Optimisation** — dead code elimination, loop unrolling, constant folding, inlining. A modern optimizing compiler (GCC -O3, Clang -O2) can make code 2–10× faster than unoptimised.
6. **Code generation** — emit machine code for the target CPU architecture (x86-64, ARM64, RISC-V).

### A Concrete Example: C Compilation

```c
// hello.c
#include <stdio.h>
int main() {
    int x = 5 + 3;
    printf("Result: %d\n", x);
    return 0;
}
```

```
$ gcc hello.c -o hello     # compile (produces machine code binary)
$ ./hello                  # run the binary directly
Result: 8
```

The binary `hello` contains no C code—only x86-64 machine instructions. You could copy it to another Linux x86-64 machine and it would run without needing `gcc` installed.

**Examples of compiled languages:** C, C++, Rust, Go, Fortran, Ada.

**Advantages of compilation:**
- Fast execution—no translation overhead at runtime.
- Aggressive optimisation across the whole program at compile time.
- Errors caught *before* running: type errors, undeclared variables.
- The executable can be distributed without source code.

**Disadvantages:**
- Compile step adds time to the edit-run-debug cycle (large C++ projects: minutes to hours).
- The binary is specific to one CPU architecture and OS; cross-compilation is complex.
- Less flexible at runtime (no easy `eval` or dynamic code loading).

## Interpreters

An **interpreter** reads source code (or a lightweight intermediate form) and executes it *directly* at runtime, without producing a separate binary.

```
Source code  (.py / .js / .rb / .php)
      ↓  Interpreter  (reads and runs line by line)
Output
```

**Examples of interpreted languages:** Classic BASIC, early PHP, early Ruby (MRI), shell scripts (bash).

**Advantages:**
- No compile step → faster iteration: write a line, run it immediately.
- Portable: the same source runs anywhere the interpreter is installed.
- Dynamic: you can generate and run code strings at runtime (`eval`), inspect and modify the program structure while running.

**Disadvantages:**
- Generally slower than compiled code—each instruction must be translated every time it runs.
- Errors may only surface at the exact line that executes—a typo deep in an unused function might not be caught until it runs.

## Hybrid Approaches

Most modern language runtimes blend both strategies to get the benefits of each.

### Stage 1: Bytecode Compilation

Source code is compiled to **bytecode**—a compact, hardware-neutral instruction set for a virtual machine (VM). This is faster to execute than raw source code, but not as fast as native machine code.

```
Python:  source (.py) → bytecode (.pyc) → CPython VM interprets bytecode
Java:    source (.java) → bytecode (.class) → JVM executes bytecode
```

You can see CPython's bytecode:

```python
import dis
def add(a, b):
    return a + b
dis.dis(add)
# LOAD_FAST  0 (a)
# LOAD_FAST  1 (b)
# BINARY_OP  0 (+)
# RETURN_VALUE
```

The bytecode is simpler for the VM to interpret than raw Python source text.

### Stage 2: Just-In-Time (JIT) Compilation

A **JIT compiler** monitors which functions run frequently ("hot spots") and compiles them to native machine code at runtime. The first few times a function runs, it is interpreted. Once it is detected as "hot," the JIT compiles it—and all subsequent calls hit native code.

```
JavaScript (V8):
  source → AST → bytecode (Ignition) → hot paths → optimised machine code (TurboFan)

Python (PyPy):
  source → RPython → bytecode → hot paths → native machine code

Java (HotSpot JVM):
  .class bytecode → hot paths → JIT-compiled native code
```

**The warm-up effect:** A JIT-compiled program may run slowly for the first few seconds (the JIT is compiling). Long-running server processes eventually run at near-compiled speed.

### Stage 3: Ahead-of-Time (AOT) Compilation

Some systems compile to native code before deployment, like a classical compiler, but from a language that was traditionally JIT-compiled:

- **GraalVM Native Image** — compiles Java to native ahead of time.
- **Dart AOT** — used for Flutter mobile apps (fast startup, no JIT overhead).
- **Kotlin/Native** — compiles Kotlin to native binaries.

## Summary Comparison

| Feature | Ahead-of-Time Compiled | Bytecode + Interpreted | JIT Hybrid | AOT + JIT |
|---------|----------------------|----------------------|------------|-----------|
| Execution speed | Fastest | Slowest | Fast (after warmup) | Fastest |
| Startup time | Fast | Moderate | Slow (warmup) | Fast |
| Development speed | Slower | Fastest | Fast | Moderate |
| Portability | Low (OS/arch-specific) | High | High | Low |
| Error detection | Compile time | Runtime | Mixed | Compile time |
| Examples | C, Rust, Go | CPython, old PHP | Java, JS (V8), PyPy | GraalVM Native |

## How Python Specifically Works

```
.py source code
      ↓  (1) CPython compiler (fast, part of the interpreter)
.pyc bytecode  (cached in __pycache__/)
      ↓  (2) CPython interpreter loop (itself compiled C code)
C-level function calls
      ↓  (3) CPU executes the C machine code of cpython binary
Output
```

**Key facts:**
- Python compiles to bytecode automatically; you usually do not see it.
- The interpreter loop is a giant C `switch` statement reading bytecode opcodes.
- CPython has a **Global Interpreter Lock (GIL)**: only one thread runs Python bytecode at a time, even on multi-core machines. (Being removed in Python 3.13+.)
- **PyPy** is an alternative Python implementation with a JIT compiler, typically 5–10× faster than CPython for compute-intensive loops.

## Common Misconceptions

**"Python is slow because it's interpreted."**
Python is slower than C partly because of interpretation, but also because of dynamic typing (every variable is a heap-allocated object with a type tag), garbage collection, and the GIL. The interpretation layer is one factor among several.

**"Compiled languages cannot be portable."**
C and C++ are highly portable at the *source* level—the same source code compiles on Linux, Windows, and macOS. The compiled *binary* is not portable, but the source is. Java and Python are portable at the *binary* level—the bytecode or source runs anywhere.

**"JIT compilation makes Python fast."**
Standard CPython does **not** have a JIT. PyPy does. CPython 3.11+ introduced a specialising adaptive interpreter that speeds up some patterns, and Python 3.13+ is adding a JIT for the first time.

## Key Takeaways

- A **compiler** translates the whole program before running it, producing a standalone binary; an **interpreter** translates line by line at runtime.
- Compiled code is generally faster; interpreted code iterates faster and is more portable.
- Most modern runtimes use a **hybrid**: source → bytecode → JIT-compiled hot paths.
- Python uses CPython, which compiles to bytecode and then interprets it—giving portability and ease of use at the cost of raw speed.
- JIT compilation delivers near-native speed for long-running programs but requires warm-up time.
