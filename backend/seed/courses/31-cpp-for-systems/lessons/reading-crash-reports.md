# Reading a Crash: From Symptom to Root Cause

Debugging is a detective skill. A crash report — whether a gdb backtrace, an ASan output, or a kernel segfault line — gives you clues, not answers. This lesson presents a systematic process for moving from the symptom you observe to the root cause you fix.

## The General Process

1. **Reproduce** the crash reliably. An unreproducible bug cannot be confirmed fixed.
2. **Read the crash output** fully before touching code.
3. **Identify the type of error** — segfault, assertion, leak, data race.
4. **Find the immediate cause** — what instruction crashed and on what data.
5. **Walk up the call stack** — find where the bad data was created.
6. **Find the root cause** — the code path that created the bad data.
7. **Fix and verify** — run all sanitizers again; the error must not recur.

## Decoding a Segfault

The OS reports a segfault when your program dereferences an invalid address.

```
Segmentation fault (core dumped)
```

First question: which address? Load the core:

```bash
gdb ./myapp core
(gdb) bt
#0  0x0000000000401abc in read_header (conn=0x603000001090) at protocol.cpp:44
#1  0x000000000040200c in handle_request (conn=0x603000001090) at server.cpp:112
#2  0x0000000000403110 in event_loop () at server.cpp:220
```

```
(gdb) frame 0
(gdb) list
44      uint32_t magic = conn->header->magic;
(gdb) print conn
$1 = (Connection *) 0x603000001090
(gdb) print conn->header
$2 = (Header *) 0x0    ← null pointer
```

**Immediate cause:** `conn->header` is null.

Now go to frame 1 to find out why it was null:

```
(gdb) frame 1
(gdb) print conn->state
$3 = HANDSHAKING   ← header not yet set in this state
```

**Root cause:** `handle_request` is called before the handshake sets the `header` pointer. The bug is a missing state check in frame 1, not in frame 0.

## Reading an ASan Report

```
==12345==ERROR: AddressSanitizer: heap-use-after-free on address 0x614000000040
READ of size 8 at 0x614000000040 thread T0
    #0 0x4023e0 in Cache::get(int) cache.cpp:87
    #1 0x40189a in main main.cpp:31

0x614000000040 was freed at:
    #0 0x7f4c in operator delete(void*) (libasan.so)
    #1 0x402210 in Cache::evict() cache.cpp:55
    #2 0x401799 in main main.cpp:28

previously allocated by thread T0 here:
    #0 0x7f2a in operator new(unsigned long) (libasan.so)
    #1 0x4021a0 in Cache::insert(int, Entry*) cache.cpp:40
    #2 0x401780 in main main.cpp:25
```

Read this in three sections:

1. **Where the crash happened** — `Cache::get` at line 87, reading 8 bytes.
2. **Where the object was freed** — `Cache::evict` at line 55, called from `main:28`.
3. **Where the object was allocated** — `Cache::insert` at line 40, called from `main:25`.

The timeline: insert (line 25), evict (line 28), get (line 31). The `get` on line 31 uses an entry that `evict` already deleted on line 28. Fix: remove the entry from the lookup table before or at the same time as freeing it.

## Common Crash Patterns and Their Signatures

| Symptom | Likely Cause | Tool to Use |
|---------|--------------|-------------|
| SIGSEGV at address `0x0` | Null pointer dereference | gdb `print ptr` |
| SIGSEGV at address near `0x10` | Member access through null (`ptr->field`) | gdb `print ptr` |
| SIGABRT | `abort()`, failed `assert()`, or double free detected by libc | gdb `bt` |
| SIGFPE | Integer division by zero | gdb `info registers` |
| Stack smashing detected | Stack buffer overflow (compiler canary) | ASan or gdb |
| "corrupted double-linked list" | Heap corruption (free wrong pointer or double free) | valgrind |
| Random corruption on every run | Data race (unprotected shared state) | TSan |

## A Structured Checklist

When you receive a crash report:

- [ ] Can you reproduce it? If not, add logging and run again.
- [ ] What signal ended the process? (`SIGSEGV`/`SIGABRT`/`SIGFPE`)
- [ ] What is the address of the fault? Null? Wild? Near-null?
- [ ] What does `bt` show? Is frame 0 inside a library (libc, STL)?
- [ ] Jump to the first frame in your own code (`frame N`). What is the bad value?
- [ ] Walk up the call stack. Where was the bad value set?
- [ ] Is this a threading issue? Does it only happen under load?
- [ ] Run with ASan — does it catch it earlier with a clearer message?

## Worked Scenario: Assertion in Production

```
myapp: server.cpp:301: void Server::send(int, const Packet&): Assertion `fd >= 0' failed.
Aborted (core dumped)
```

The assertion is the symptom. The root cause is that `fd` is -1. Load the core:

```bash
gdb ./myapp core
(gdb) bt
#0  raise () from libc
#1  abort () from libc
#2  Server::send (this=..., fd=-1, pkt=...) at server.cpp:301
#3  Session::flush_queue (this=0x6050f0) at session.cpp:188
#4  EventLoop::on_writable (fd=-1) at eventloop.cpp:77
```

Frame 3: `flush_queue` called `send` with `fd=-1`. Check why:

```
(gdb) frame 3
(gdb) print this->fd_
$1 = -1
(gdb) print this->connected_
$2 = false
```

The session is no longer connected (`fd_` was set to -1 on disconnect), but `flush_queue` was still called. Root cause: the disconnect handler did not cancel the pending write event before closing the fd.

> **Interview answer:** Start by reading the full crash output — signal, faulting address, and full backtrace. Find the first frame in your own code, print the bad value, then walk up the stack to find where that value came from. Run ASan or valgrind if the crash is not reproducible cleanly — they often catch the error earlier and with a clearer explanation.
