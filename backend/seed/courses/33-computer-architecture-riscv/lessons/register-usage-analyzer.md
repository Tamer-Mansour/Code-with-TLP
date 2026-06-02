# Exercise: Map Register Numbers to ABI Names

In this exercise you will build a **RISC-V Register Usage Analyzer** — a program that reads a list of register numbers and returns their ABI names, calling-convention roles, and preservation class (caller-saved or callee-saved).

## What You Will Implement

Given one or more register numbers (0–31) on separate lines of stdin, your program must output a formatted report line for each register:

```
x<N> | <ABI name> | <role> | <class>
```

where `<class>` is either `caller-saved`, `callee-saved`, or `special`.

## Why This Matters

ABI fluency is tested in systems-programming interviews. Being able to instantly map `x10` → `a0 | FP argument 0 / return value | caller-saved` signals deep hardware knowledge and is exactly the kind of recall you need when reading disassembly or a crash dump in a 45-minute interview.

## Skills Practiced

- Memorising the full RISC-V integer ABI register table.
- Systematic lookup / table-driven design.
- Clean formatted output with pipes.

## Getting Started

Your program should read register numbers from stdin (one per line) and print the corresponding ABI info. Handle invalid numbers (< 0 or > 31) by printing `invalid register number`.

See the exercise prompt for the exact input/output specification, sample test cases, and constraints.
