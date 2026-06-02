# Video: Operating System Fundamentals

This video provides a comprehensive introduction to operating systems — what they are, why they exist, and how they manage hardware resources on behalf of applications.

## What This Video Covers

- The role of the OS as resource manager, abstraction layer, and protection boundary
- The distinction between the kernel and user space
- How system calls form the boundary between applications and the OS kernel
- A tour of major OS families: Linux, Windows NT, and macOS/XNU

## Key Timestamps

| Timestamp | Topic |
|-----------|-------|
| 0:00 | What is an OS? |
| ~15 min | Kernel vs user mode |
| ~30 min | System call internals |
| ~50 min | OS history and major families |

## Key Takeaways

Every request from a user-space program to access hardware — reading a file, opening a socket, creating a process — must cross the kernel boundary through a controlled **system call**. The OS uses this boundary to enforce isolation, security, and fair resource sharing across all running programs.
