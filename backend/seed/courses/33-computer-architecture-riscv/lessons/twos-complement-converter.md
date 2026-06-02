# Exercise: Two's Complement Encode/Decode

In this exercise you will write a program that both **encodes** decimal integers into their two's complement binary representation and **decodes** two's complement binary strings back into signed decimal integers.

This is a fundamental skill for reading register dumps, debugging memory corruption, and understanding how arithmetic overflow manifests at the bit level.

## What You Will Implement

Your program reads a series of operations from standard input. Each operation is one of:

- `ENCODE <width> <decimal>` — given a signed decimal integer and a bit width, output the two's complement representation as a zero-padded binary string.
- `DECODE <width> <binary>` — given a binary string and a bit width, interpret it as a two's complement signed integer and output the decimal value.

Apply the flip-and-add-one rule for encoding negative numbers and the weighted MSB formula for decoding.

## Skills Practiced

- Translating between decimal and binary number representations
- Applying the two's complement encoding/decoding algorithm
- Handling edge cases: zero, INT_MIN (most negative value), and values at the boundary of the representable range

## Getting Started

Your solution should read all operations until EOF, printing one result per line. Focus on correctness first, then verify your edge cases — especially the most-negative value for each bit width.
