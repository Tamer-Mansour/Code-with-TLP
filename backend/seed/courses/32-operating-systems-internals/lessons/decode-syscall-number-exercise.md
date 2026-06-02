# Exercise: Dispatch System Calls From a Numbered Argument Stream

In this exercise you will simulate the core of a kernel syscall dispatcher. Real kernels index a function-pointer table by the syscall number in `rax`; you will do the same thing in software, reading a stream of numbered operations and producing the correct output for each.

## What You Will Implement

You will write a program that reads a sequence of syscall records from standard input. Each record specifies:

- A **syscall number** (integer).
- A set of **arguments** appropriate for that syscall.

Your program must dispatch each record to the correct handler and print the result to standard output.

### Supported Syscall Numbers

| Number | Name | Arguments | Action |
|---|---|---|---|
| 1 | `write` | `fd count "string"` | If fd=1 print string (up to count chars); return bytes written |
| 3 | `getpid` | *(none)* | Return the simulated PID (always 42) |
| 4 | `getuid` | *(none)* | Return the simulated UID (always 1000) |
| 6 | `close` | `fd` | If fd is open return 0, else return -9 (EBADF) |
| 9 | `exit` | `status` | Print "exit(status)" and stop processing further records |

For `write`, the only valid fd is 1 (stdout). Any other fd returns -9 (EBADF). The output for a `write` to fd=1 is the string itself on its own line (the printed content), and then a separate line with the return value.

For all other syscalls, print only the return value on one line.

If an unknown syscall number is encountered, print `-38` (ENOSYS) and continue.

## Skills Practiced

- Array/table-driven dispatch (the kernel's `sys_call_table` pattern).
- Argument parsing and validation.
- Error code conventions (`-EBADF`, `-ENOSYS`).
- Systematic handling of a stream of operations with early termination.

## Getting Started

Read from stdin line by line. The first token on each line is the syscall number (integer). Parse the remaining tokens as arguments. Dispatch using a dictionary or match statement keyed on the syscall number.

Open the prompt file `os-decode-syscall-number-exercise.prompt.md` for the full input/output specification and sample test cases.
