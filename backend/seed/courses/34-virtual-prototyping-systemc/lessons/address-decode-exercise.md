# Decode an Address to a Target and Offset

In this exercise you will implement the core logic of a TLM router: given a system address map and a physical address, determine **which region** the address falls into and calculate the **target-local offset**.

## What You Will Implement

Write a program that reads an address map (a list of named regions with a base address and size) followed by a list of addresses to decode. For each address, print the region name and the computed offset, or `"UNMAPPED"` if no region contains the address.

## Why This Matters

Every TLM interconnect performs exactly this computation on every transaction. Getting the boundary conditions right (off-by-one on the last valid byte) and handling unmapped accesses cleanly are the two most common sources of bugs in virtual-prototype routers.

## Key Concepts Practiced

- Linear address-map scan with inclusive-base, exclusive-end semantics.
- Offset calculation: `offset = address - base`.
- Boundary validation: the last valid byte is at `base + size - 1`.
- Reporting unmapped gaps instead of silently accessing invalid memory.

## Your Task

Read the input, scan the address map for each query address, and emit either:

```
<region_name> 0x<offset_hex>
```

or

```
UNMAPPED
```

See the prompt file (`vp-address-decode-exercise.prompt.md`) for the full input/output specification and sample test cases.
