# Route Transactions Through an Address-Mapped Bus

In this exercise you will implement the core routing logic of a TLM bus model — in Python. You will read an address map and a sequence of transactions, decode each transaction's address to find the correct target, strip the base address, and report the result. This mirrors exactly what a `b_transport()` decode step does in a SystemC bus.

## What You Will Implement

Write a program that:

1. Reads an address map (base address, size, target name) for N regions.
2. Reads M transaction records (address, size in bytes, command R or W).
3. For each transaction, finds which region the address falls in (or reports `UNMAPPED`).
4. Outputs the target name and the target-local (base-stripped) address.

## Skills Practiced

- Address decode with base-offset translation
- Handling unmapped addresses with an error response
- Thinking in hex — addresses are given in hexadecimal

## Example

Given a map with `ROM` at `0x00000000` size `0x10000` and `UART` at `0x40000000` size `0x1000`, a transaction to address `0x40000008` maps to `UART` at local offset `0x00000008`.

## Getting Started

Your solution reads from standard input and writes to standard output. No files, no third-party libraries — pure Python. Work through the sample input in the prompt file before coding to make sure your decode logic handles edge cases.
