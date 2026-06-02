# Video: How Programs Run — CPUs, Machine Code, and Compilers

This video explains the fetch-decode-execute cycle that every CPU performs billions of times per second, and traces the journey from high-level source code all the way down to the binary machine instructions that the hardware actually executes.

**Key topics covered:**
- CPU registers, the program counter, and the instruction register
- The fetch-decode-execute cycle in detail
- Instruction set architectures (ISA): what machine code actually looks like
- How a compiler translates high-level code (C, Java) into machine code
- How an interpreter (Python, JavaScript) executes source code line-by-line
- Just-in-time (JIT) compilation as a hybrid strategy

**Recommended timestamps to focus on:**
- 0:00 – CPU internals: registers and the ALU
- ~12:00 – The fetch-decode-execute loop animated
- ~22:00 – Compiler pipeline: lexer → parser → code generator
- ~35:00 – Interpreter vs compiler trade-offs in practice

Pay particular attention to how the program counter advances through instructions — this explains both how loops work and how a function call changes the flow of execution.
