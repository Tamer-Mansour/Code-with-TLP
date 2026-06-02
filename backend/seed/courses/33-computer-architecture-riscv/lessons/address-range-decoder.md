# Exercise: Map Addresses to Devices via Decoding

Address decoding is the hardware mechanism that maps a flat CPU address space to individual devices. In this exercise you will implement a software model of an address decoder — given a set of address ranges assigned to named devices and a list of addresses to look up, your program identifies which device (or "UNMAPPED") each address belongs to.

## What You Will Implement

You are given:
1. A set of devices, each with a base address and a size (in bytes). The range for a device is `[base, base + size - 1]` inclusive.
2. A list of addresses to decode.

For each query address, print the name of the device whose range contains that address, or `UNMAPPED` if no device covers it.

## Why This Matters

This is exactly what a hardware address decoder does every clock cycle — it evaluates which chip-select to assert based on the incoming address. Getting it right is critical: overlapping ranges cause bus fights; gaps cause unmapped faults. Building a mental model through code makes the hardware concept concrete.

## Input / Output Format

See the accompanying prompt file for the exact specification, constraints, and sample cases.

## Concepts Practiced

- Address range arithmetic (`base` to `base + size - 1`)
- Handling unmapped addresses (gaps in the address space)
- Efficient range lookup
- Hexadecimal address parsing
