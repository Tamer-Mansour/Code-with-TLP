# Message Queues and Mailboxes

Message queues give processes a **structured, persistent rendezvous point** managed by the kernel. Unlike pipes, message queues preserve **message boundaries** — each `send` delivers one discrete unit that the receiver reads in a single `receive` call. They also survive as long as the kernel keeps them, even if both communicating processes have exited.

## Two Flavors: POSIX vs System V

Unix systems offer two message queue APIs with different trade-offs:

| Feature | POSIX mq | System V msgq |
|---|---|---|
| Header | `<mqueue.h>` | `<sys/msg.h>` |
| Naming | `/name` in filesystem | Integer key via `ftok()` |
| Priority support | Yes (0–31) | No (type field only) |
| Notification | `mq_notify()` (async) | Poll or block only |
| Portability | POSIX standard | XSI / older Unix |

Modern code should prefer POSIX message queues.

## POSIX Message Queue Basics

```c
#include <mqueue.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>

// --- Producer ---
int main_producer() {
    // Open (or create) a queue; max 10 messages of 256 bytes each
    struct mq_attr attr = { .mq_maxmsg = 10, .mq_msgsize = 256 };
    mqd_t mq = mq_open("/myqueue", O_CREAT | O_WRONLY, 0644, &attr);

    const char *msg = "job:render:42";
    mq_send(mq, msg, strlen(msg) + 1, 0 /*priority*/);
    mq_close(mq);
    return 0;
}

// --- Consumer ---
int main_consumer() {
    mqd_t mq = mq_open("/myqueue", O_RDONLY);

    char buf[256];
    unsigned int prio;
    ssize_t n = mq_receive(mq, buf, sizeof(buf), &prio);
    printf("Received (%zd bytes): %s\n", n, buf);

    mq_close(mq);
    mq_unlink("/myqueue");   // remove the queue name
    return 0;
}
```

A few details worth internalizing:

- `mq_receive` **blocks** when the queue is empty (unless `O_NONBLOCK` is set).
- `mq_send` **blocks** when the queue is full — natural back-pressure, just like pipes.
- Message size must not exceed `mq_msgsize`; the kernel rejects oversized sends.
- Priority: higher numeric value = higher priority. `mq_receive` always dequeues the highest-priority message first.

## System V Message Queues

Older but still common in embedded Linux and legacy code:

```c
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>

struct msgbuf {
    long mtype;      // must be > 0; used as message "type" for selective receive
    char mtext[256];
};

// Create / attach
key_t key = ftok("/tmp/myapp", 42);
int qid = msgget(key, IPC_CREAT | 0644);

// Send
struct msgbuf m = { .mtype = 1 };
strcpy(m.mtext, "ping");
msgsnd(qid, &m, sizeof(m.mtext), 0);

// Receive only type-1 messages
msgrcv(qid, &m, sizeof(m.mtext), 1 /*mtype*/, 0);

// Destroy
msgctl(qid, IPC_RMID, NULL);
```

Selective receive (`mtype > 0`) lets a single queue act like multiple logical channels — a useful pattern for worker pools.

## Performance and Limits

- Each message is **copied twice**: sender's buffer → kernel queue → receiver's buffer.
- Kernel enforces system-wide limits (`/proc/sys/fs/mqueue/` for POSIX).
- Typical max queue message size: 8 KB (POSIX default, tunable).
- For high-throughput scenarios (millions of messages/sec), consider shared memory with a ring buffer instead.

## Mailbox Abstraction in Operating Systems Theory

Operating systems textbooks often use the term **mailbox** to describe the general concept: a named buffer in kernel space where senders deposit messages and receivers pick them up asynchronously. Message queues are the Unix implementation of this abstraction. The concept also appears in Windows (mailslots), Android (Binder), and microkernel designs (L4, seL4).

## Common Pitfalls

- **Forgetting `mq_unlink`** — POSIX queues persist in the kernel until explicitly unlinked, leaking resources across reboots on some systems.
- **Assuming atomicity for large messages** — the queue enforces a max message size; plan your wire format carefully.
- **Mixing POSIX and System V** — they are entirely separate APIs and cannot interoperate.

## Interview Answer

> "Message queues are kernel-managed buffers that preserve message boundaries and support priority ordering. Unlike pipes (byte streams), each send/receive is one atomic message. They persist beyond process lifetime and support asynchronous notification. The main cost is two copies per message, making them slower than shared memory for bulk data."
