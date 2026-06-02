# Video: Processes, fork(), and exec()

This video dives into how an operating system represents and manages running programs through the process abstraction, covering the process control block, state machine, and the UNIX process creation model.

## What This Video Covers

- The anatomy of a process: code segment, data segment, stack, heap, and PCB
- Process state transitions: new, ready, running, waiting, terminated
- How `fork()` duplicates a process and `exec()` replaces its image
- Context switching and the cost it imposes on CPU throughput
- Zombie and orphan processes and how the OS handles them

## Key Timestamps

| Timestamp | Topic |
|-----------|-------|
| 0:00 | Process vs program |
| ~10 min | Process Control Block (PCB) |
| ~25 min | fork() and exec() walkthrough |
| ~45 min | Context switching mechanics |
| ~55 min | Zombie processes and wait() |

## Key Takeaways

`fork()` creates a near-identical copy of the calling process (copy-on-write), while `exec()` loads a new program image into the existing process shell. Together they form the UNIX idiom for launching any program. Context switching saves and restores the CPU register state (PC, SP, general registers) stored in the PCB — this is the only way the OS can share one CPU core across many processes.
