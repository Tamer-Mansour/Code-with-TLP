# Exercise: Simulate an Alloc/Free Tracker for Leaks

## Overview

Memory debuggers like Valgrind and AddressSanitizer work by intercepting every allocation and deallocation, recording which addresses are live, and reporting anything still live at program exit.

In this exercise you will simulate that core idea in code: process a log of `ALLOC` and `FREE` events and detect leaks, double-frees, and invalid frees.

## What You Will Implement

Your program reads a sequence of memory events from standard input. Each event is either:

- `ALLOC <id> <size>` — allocate `size` bytes and tag the block with `id` (a positive integer)
- `FREE <id>` — free the block tagged `id`

After processing all events, your program must report:

1. Any **double-free** or **invalid-free** — freeing an `id` that is not currently allocated.
2. Any **leaked blocks** — `id`s that were allocated but never freed, listed in ascending order of `id`.
3. A final summary line.

This models the exact bookkeeping a real memory tracker performs — without any actual heap manipulation.

## Skills Practiced

- Simulating heap state with a dictionary / map
- Detecting ordering errors (double-free, invalid free)
- Reporting state at program termination (leak detection)
- Reading structured input and producing structured output

## Getting Started

Your solution should read all events from stdin, process them in order, and write results to stdout. No files, no third-party libraries.

See the accompanying prompt file for the full input/output specification and sample test cases.
