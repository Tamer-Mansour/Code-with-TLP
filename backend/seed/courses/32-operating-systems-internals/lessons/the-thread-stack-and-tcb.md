# The Thread Stack and Thread Control Block

Every thread needs two things to exist: a place to run (the stack) and a place to be remembered (the Thread Control Block). Understanding both is essential for debugging crashes, implementing schedulers, and answering OS interview questions accurately.

## The Thread Stack

A thread's stack holds:

- **Local variables** declared inside functions
- **Function arguments** passed on the stack (architecture-dependent)
- **Return addresses** — where to resume after a function returns
- **Saved registers** — the caller-saves registers spilled before a call
- **Stack frame metadata** — frame pointer, alignment padding

```
High address
┌─────────────────────┐  ← thread stack base (mmap'd region top)
│  main() frame       │
│  - local vars       │
│  - saved rbp        │
│  - return addr      │
├─────────────────────┤
│  foo() frame        │
│  - local vars       │
│  - saved regs       │
├─────────────────────┤
│  bar() frame        │ ← current stack pointer (rsp)
├─────────────────────┤
│  (free space)       │
│                     │
├─────────────────────┤  ← guard page (PROT_NONE — triggers SIGSEGV)
└─────────────────────┘  ← low address
```

On Linux the default thread stack is 8 MB (RLIMIT_STACK). The OS maps a guard page just below the stack; writing into it causes a segfault rather than silently corrupting adjacent memory.

```bash
# Inspect default stack size
ulimit -s        # prints 8192 (KB) on most Linux systems
```

### Stack Overflow vs Heap Overflow

A stack overflow happens when deep recursion or large local arrays push RSP past the guard page. It is not the same as a heap overflow. The fix is either to reduce recursion depth, move large buffers to the heap, or increase the stack size with `pthread_attr_setstacksize`.

```c
pthread_attr_t attr;
pthread_attr_init(&attr);
pthread_attr_setstacksize(&attr, 16 * 1024 * 1024);  // 16 MB
pthread_create(&tid, &attr, my_func, NULL);
```

## The Thread Control Block (TCB)

The TCB is the kernel data structure that represents a thread. On Linux it is part of the `task_struct`. The TCB stores everything the scheduler needs to suspend and resume a thread:

| Field | Purpose |
|---|---|
| Thread ID (TID) | Unique identifier |
| State | Running / Runnable / Blocked / Zombie |
| Saved register set | PC, SP, general-purpose regs, EFLAGS |
| Stack pointer / base | Where the thread's stack lives |
| Priority / scheduling class | SCHED_OTHER, SCHED_FIFO, etc. |
| Signal mask | Which signals are blocked |
| Pointer to PCB | Links thread back to its owning process |
| TLS pointer (fs/gs base) | Per-thread storage area |

```c
// Simplified kernel TCB (conceptual, not actual Linux source)
struct tcb {
    pid_t           tid;
    enum state      state;
    struct cpu_ctx  saved_ctx;   // registers saved on context switch
    void           *stack_base;
    size_t          stack_size;
    struct pcb     *process;     // owning process
    void           *tls_area;
};
```

## How Context Switch Uses the TCB

When the scheduler preempts thread A to run thread B:

1. Hardware interrupt (timer) fires → CPU enters kernel mode.
2. Kernel saves all of thread A's registers into **A's TCB**.
3. Kernel loads thread B's registers from **B's TCB**.
4. Kernel switches the stack pointer to **B's stack**.
5. `iret` (or `sysretq`) returns to user space at B's saved PC.

```asm
; Simplified x86-64 context switch (conceptual)
save_context:
    mov [tcb_a + ctx.rsp], rsp
    mov [tcb_a + ctx.rbp], rbp
    mov [tcb_a + ctx.rip], rip   ; via call/ret trick

load_context:
    mov rsp, [tcb_b + ctx.rsp]
    mov rbp, [tcb_b + ctx.rbp]
    jmp [tcb_b + ctx.rip]
```

## Common Pitfall

Candidates often confuse the TCB with the PCB. The PCB (Process Control Block) holds process-wide resources — address space, open files, PID. The TCB holds per-thread execution state. One PCB can have many TCBs attached.

> **Interview answer:** The thread stack stores the call chain, local variables, and saved registers for one thread's execution path. The Thread Control Block is the kernel's bookkeeping structure for a thread, containing its saved register state, stack pointer, scheduling info, and a link back to the owning process. Together they are everything the scheduler needs to pause and resume a thread.
