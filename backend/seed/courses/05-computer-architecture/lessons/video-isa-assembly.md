# Video: Instruction Set Architecture and Assembly Language

This video demystifies ISA design and assembly programming. It contrasts the RISC philosophy (ARM, RISC-V) with CISC (x86), then demonstrates how high-level C code translates into real assembly instructions.

**Key topics covered:**
- RISC vs CISC: instruction count, encoding width, and register conventions
- RISC-V R/I/S/B/U/J instruction formats and how each field is encoded
- Addressing modes: immediate, register-indirect, base+offset, PC-relative
- Walking through a C loop compiled to RISC-V assembly: branches, loads, stores
- Calling conventions: stack frame layout, argument registers, caller vs callee-saved

**Takeaway:** You will understand how a compiler maps C constructs to machine instructions, how addressing modes reduce instruction count, and why ISA choices affect both hardware complexity and compiler quality.
