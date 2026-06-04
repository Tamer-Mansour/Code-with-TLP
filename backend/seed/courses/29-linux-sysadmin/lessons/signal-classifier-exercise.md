# Process Signal Classifier

Classify POSIX signals by name and whether they can be caught or ignored by a process.

## What you'll practice

- POSIX signal numbers and names
- The critical distinction between catchable and non-catchable signals
- Reading structured integer input and producing formatted output

## Key concept

**SIGKILL (9) and SIGSTOP (19)** are the only two signals that user-space code can never catch, block, or ignore. Every other standard signal can be handled with a custom handler or masked. This is why `kill -9` is the "last resort" — but even it has limits: a process stuck in uninterruptible sleep (state `D`) will not respond until the underlying kernel wait resolves.

## Task

Given `N` signal numbers, print each signal's name and catchability status. Unknown signal numbers should produce `UNKNOWN: catchable assumed`.

See the problem statement for full input/output specification.
