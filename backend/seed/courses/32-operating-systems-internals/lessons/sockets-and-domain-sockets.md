# Sockets and Unix Domain Sockets

Sockets are the most versatile IPC mechanism: they work between threads in the same process, between processes on the same machine, and across the network to a remote host — all using the same API. This uniformity makes sockets the foundation of virtually every client-server system, from web browsers to databases to microservices.

## Socket Families

The `socket()` call takes an **address family** that determines the transport:

| Family | Constant | Use case |
|---|---|---|
| Internet (IPv4) | `AF_INET` | Network communication over TCP/UDP |
| Internet (IPv6) | `AF_INET6` | Network communication over TCP/UDP |
| Unix domain | `AF_UNIX` / `AF_LOCAL` | Same-host IPC via filesystem path |

The **type** parameter selects stream vs. datagram:
- `SOCK_STREAM` — reliable, ordered byte stream (TCP over network; SOCK_STREAM over Unix)
- `SOCK_DGRAM` — unreliable, message-preserving datagrams (UDP; also Unix datagram sockets)

## Unix Domain Sockets

Unix domain sockets (UDS) behave identically to TCP sockets in the API but use a filesystem path as the address instead of an IP/port. They never leave the machine, so the kernel can skip the TCP/IP stack entirely — making them significantly faster than loopback TCP.

```c
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

#define SOCKET_PATH "/tmp/myapp.sock"

// --- Server ---
void run_server() {
    int srv = socket(AF_UNIX, SOCK_STREAM, 0);

    struct sockaddr_un addr = { .sun_family = AF_UNIX };
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    unlink(SOCKET_PATH);   // remove stale socket file
    bind(srv, (struct sockaddr *)&addr, sizeof(addr));
    listen(srv, 5);

    int cli = accept(srv, NULL, NULL);
    char buf[128];
    ssize_t n = recv(cli, buf, sizeof(buf) - 1, 0);
    buf[n] = '\0';
    printf("Server received: %s\n", buf);

    send(cli, "ack", 3, 0);
    close(cli);
    close(srv);
    unlink(SOCKET_PATH);
}

// --- Client ---
void run_client() {
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);

    struct sockaddr_un addr = { .sun_family = AF_UNIX };
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    send(fd, "hello", 5, 0);

    char buf[16];
    recv(fd, buf, sizeof(buf), 0);
    printf("Client received: %.*s\n", 3, buf);
    close(fd);
}
```

## UDS vs. Loopback TCP: Performance

| Metric | Loopback TCP | Unix Domain Socket |
|---|---|---|
| Throughput | ~10–20 GB/s | ~30–50 GB/s (system-dependent) |
| Latency | ~20–60 µs | ~5–15 µs |
| Extra headers | TCP + IP (40 bytes) | None |
| NAT/firewall rules | Possible | Not applicable |

Real-world systems like PostgreSQL, MySQL, Redis, and Docker all accept Unix domain socket connections for local clients. Nginx proxies to backends over UDS when both are on the same host.

## File Descriptor Passing

Unix domain sockets have a unique capability not possible with network sockets: they can **transfer open file descriptors** between processes using `SCM_RIGHTS` ancillary messages. This allows a privileged server to open a file and hand the descriptor to an unprivileged client without sharing the path.

```c
// Conceptual: send fd to peer via UDS
struct msghdr msg = { 0 };
struct cmsghdr *cmsg;
char buf[CMSG_SPACE(sizeof(int))];
msg.msg_control = buf;
msg.msg_controllen = sizeof(buf);
cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type  = SCM_RIGHTS;
cmsg->cmsg_len   = CMSG_LEN(sizeof(int));
memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));
sendmsg(uds_fd, &msg, 0);
```

This technique is used by systemd socket activation, Chrome's multi-process architecture, and container runtimes.

## When to Choose Sockets

- **Need to cross machine boundaries** — network sockets are the only option.
- **Same-host IPC with network-compatible protocol** — UDS gives the same API with better performance.
- **Bidirectional communication** — unlike pipes, both ends can read and write.
- **Fan-out (many clients)** — `accept()` in a loop serves multiple clients on one listening socket.

## Common Pitfalls

- **Stale socket file** — if the server crashes, the socket path remains. Always `unlink()` before `bind()`.
- **Framing on SOCK_STREAM** — like pipes, TCP/UDS streams do not preserve message boundaries. Implement length-prefixed framing or use `SOCK_SEQPACKET` (UDS only) for message boundaries.
- **`sun_path` overflow** — the path is limited to 108 characters (Linux). Long paths are silently truncated.

## Interview Answer

> "Unix domain sockets use the same BSD socket API as network sockets but address by filesystem path, staying entirely in the kernel. They are 2–5x faster than loopback TCP because the TCP/IP stack is bypassed. They also uniquely support file descriptor passing via ancillary messages. The main pitfall is that SOCK_STREAM is still a byte stream — you need explicit framing to delineate messages."
