# Microkernels and Message Passing Overhead

The defining characteristic of a microkernel is that cross-component communication happens through **message passing** rather than direct function calls. Understanding the performance cost of this design decision is critical for evaluating microkernel trade-offs.

## Why Message Passing?

In a microkernel, OS services run in separate user-space address spaces. Because processes cannot directly call each other's functions (virtual addresses are private), the kernel must mediate every interaction. This mediation is IPC — inter-process communication — implemented as message passing.

```
Application                File Server
    |                           |
    | 1. send(msg: open("/x"))  |
    |-------------------------->|  (kernel routes message)
    |                           | 2. process request
    | 4. recv(reply: fd=5)      |
    |<--------------------------|  (kernel delivers reply)
    |  3. send(reply)           |
```

## The Performance Cost: A Breakdown

A single synchronous IPC round trip involves:

1. **User-to-kernel mode switch** (system call into the kernel) — ~100 cycles on x86.
2. **Message copy or capability check** — kernel validates and routes the message.
3. **Context switch** to the server process (if blocked) — cache and TLB pressure.
4. **Server processes the request** — actual work.
5. **Kernel-to-server mode switch return** (server now in user mode).
6. **Reply IPC** — server sends back; another round trip.
7. **Context switch back** to the original caller.

Contrast this with a monolithic kernel: a `read()` call is a single mode switch into kernel code that directly invokes the VFS layer — no context switches, no message copies.

```c
// Monolithic: one syscall, one mode switch
ssize_t n = read(fd, buf, 4096);  // ~1 microsecond

// Microkernel equivalent (conceptual):
ipc_send(fs_server_tid, &open_msg);   // mode switch 1
ipc_recv(&reply);                      // mode switch 2 (blocked until reply)
// Total: ~5-10x more latency on naive implementations
```

## The L4 Revolution

Early microkernels (Mach) were notoriously slow — IPC was 100x slower than monolithic system calls. In the mid-1990s, Jochen Liedtke demonstrated with **L4** that microkernel IPC could be made much faster by:

- Keeping the entire IPC path in **L1 cache** (fitting the kernel in ~12 KB).
- Using **registers** to pass small messages, avoiding memory copies.
- Eliminating unnecessary abstractions from the kernel path.

L4's IPC was roughly **20x faster than Mach's**, closing the gap significantly. Modern L4 descendants (seL4, Fiasco.OC) achieve IPC costs of a few hundred cycles.

## Synchronous vs Asynchronous IPC

| IPC Style | Latency | Throughput | Use case |
|-----------|---------|------------|----------|
| Synchronous (rendez-vous) | Low (no buffering) | Limited by round trips | Most microkernel designs |
| Asynchronous (buffered) | Higher | Higher | Batching, pipelining |

Most high-performance microkernels use synchronous IPC for simplicity and predictability — the sender blocks until the receiver is ready, making it easy to reason about ordering.

## Shared Memory as an Optimization

For bulk data transfers (e.g., reading a large file), copying through IPC messages is expensive. Microkernels use **shared memory** mapped into both the client and server address spaces:

```
Client AS: [ code | data | ... | shared region ]
                                      |
Server AS: [ code | data | ... | shared region ]
```

Only the metadata (offsets, lengths) travels via IPC messages; the actual data is accessed in place. This brings bulk-transfer performance close to monolithic levels.

## Pitfalls

- **Priority inversion in IPC** — if a low-priority server holds a resource a high-priority client is blocked on, the system may stall.
- **Server death** — a client blocked waiting for a reply must handle the case where the server crashes mid-request.
- **Cascading delays** — a request might chain through multiple servers (app -> FS server -> block driver server), multiplying latency.

> **Interview answer:** "Microkernel message passing costs multiple mode switches and context switches per IPC round trip, historically 5-20x more overhead than a direct kernel call; L4-family kernels mitigated this by fitting the entire IPC path in L1 cache and passing small messages in registers."
