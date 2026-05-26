# UDP vs TCP

The **Transport Layer** sits between the Application Layer and the Network (IP) Layer. Its job is to take the host-to-host delivery service offered by IP and extend it to process-to-process delivery via **port numbers**, and optionally to add reliability and ordering. The two main protocols — **UDP** and **TCP** — have radically different design philosophies. Choosing the right one is a fundamental engineering decision that affects latency, throughput, complexity, and correctness.

## Ports and Sockets

Both UDP and TCP use **port numbers** (16-bit, 0–65535) to multiplex multiple application conversations over a single IP address:

- **Well-known ports** (0–1023): assigned by IANA (HTTP=80, HTTPS=443, SSH=22, DNS=53, SMTP=25).
- **Registered ports** (1024–49151): voluntarily registered applications (PostgreSQL=5432, Redis=6379).
- **Dynamic / ephemeral ports** (49152–65535): assigned by the OS for outgoing connections.

A **socket** is the endpoint of a communication channel, uniquely identified by `(IP address, port, protocol)`. A TCP *connection* is uniquely identified by the **4-tuple**: `(src_ip, src_port, dst_ip, dst_port)`. Two different clients connecting to the same server port are distinguished by their different source IPs/ports.

## UDP: User Datagram Protocol (RFC 768)

UDP is the **minimal** transport layer. It adds only two things on top of raw IP: port numbers and a checksum. Everything else is left to the application.

### UDP Header (8 bytes — always exactly 8 bytes)

```
 0               15 16             31
+─────────────────+─────────────────+
│   Source Port   │   Dest Port     │
+─────────────────+─────────────────+
│     Length      │    Checksum     │
+─────────────────+─────────────────+
│           Data payload            │
│              ...                  │
```

| Field | Size | Description |
|-------|------|-------------|
| Source Port | 16 bits | Sender's port (may be 0 if reply not needed) |
| Dest Port | 16 bits | Receiver's port |
| Length | 16 bits | Header + data in bytes (min 8) |
| Checksum | 16 bits | One's-complement checksum; optional in IPv4, mandatory in IPv6 |

### UDP Semantics

UDP provides **no connection setup**, **no acknowledgements**, **no retransmissions**, **no ordering guarantees**, **no flow control**, and **no congestion control**. If a datagram is lost, duplicated, or reordered, the application must handle it — or ignore it.

### When to Use UDP

| Use Case | Why UDP Works |
|----------|--------------|
| DNS queries | Small, single request-response; retransmit logic in the client |
| Video/audio streaming (WebRTC, RTP) | Dropping a frame is better than stalling playback |
| Online gaming (position updates) | Stale state is useless; latest packet is all that matters |
| DHCP | Broadcast-based pre-IP assignment (no IP yet for TCP) |
| NTP (time sync) | Single request-response; precision more important than reliability |
| QUIC (HTTP/3) | UDP as a foundation; QUIC implements its own reliability |
| IoT telemetry | Occasional missed readings are acceptable |
| Anycast DNS, SNMP | Low overhead required |

## TCP: Transmission Control Protocol (RFC 793)

TCP provides **reliable, ordered, connection-oriented, byte-stream** delivery. It is significantly more complex than UDP but removes the burden of reliability from every application that needs it.

### TCP Header (20–60 bytes)

```
 0                  15 16                 31
+─────────────────────+─────────────────────+
│     Source Port     │  Destination Port   │
+─────────────────────────────────────────--+
│              Sequence Number              │
+───────────────────────────────────────────+
│           Acknowledgement Number          │
+──────┬──────────────┬─────────────────────+
│DataOf│   Flags      │    Window Size      │
│(4b)  │ (12 bits)    │    (16 bits)        │
+──────┴──────────────┴─────────────────────+
│       Checksum      │   Urgent Pointer    │
+─────────────────────────────────────────--+
│              Options (0–40 bytes)         │
+───────────────────────────────────────────+
```

Important flag bits:

| Flag | Meaning |
|------|---------|
| SYN | Synchronize — initiate connection, exchange ISNs |
| ACK | Acknowledgement number is valid |
| FIN | No more data from sender — begin teardown |
| RST | Reset — abrupt connection termination |
| PSH | Push data to application immediately (don't buffer) |
| URG | Urgent pointer field is valid (rarely used today) |

### TCP Three-Way Handshake (Connection Establishment)

Before any data can flow, TCP performs a **three-way handshake** to establish the connection and exchange **Initial Sequence Numbers (ISNs)**. ISNs are random to prevent old packets from interfering with new connections (RFC 6528).

```
Client                                    Server
  │                                          │
  │── SYN (seq=x, SYN flag) ───────────────►│  [SYN_SENT]
  │                                          │  [SYN_RECEIVED]
  │◄── SYN-ACK (seq=y, ack=x+1) ────────────│
  │                                          │
  │── ACK (seq=x+1, ack=y+1) ──────────────►│  [ESTABLISHED]
  │                                          │  [ESTABLISHED]
  │  [Data can now flow in both directions]  │
```

- `x` and `y` are randomly chosen ISNs for each direction of the byte stream.
- The handshake costs **1.5 round trips** (1.5 × RTT) before the first data byte can be sent.
- This is why TLS 1.3's 0-RTT and HTTP/3's QUIC matter — eliminating unnecessary round trips.

### TCP Connection Teardown (Four-Way FIN Handshake)

TCP connections are **full-duplex**: each direction is closed independently.

```
Client                                    Server
  │── FIN (seq=u) ────────────────────────►│  [FIN_WAIT_1]
  │◄── ACK (ack=u+1) ───────────────────── │  [CLOSE_WAIT]
  │   [Client can still receive data]       │  [Server may send more data]
  │◄── FIN (seq=v) ─────────────────────── │  [LAST_ACK]
  │── ACK (ack=v+1) ───────────────────────►│  [CLOSED]
  │   [TIME_WAIT: 2 × MSL ≈ 60–120 s]      │
```

**TIME_WAIT** ensures the final ACK reaches the server and that stale packets from this connection are absorbed before the 4-tuple is reused. Linux's `tcp_tw_reuse` and `SO_REUSEPORT` options can reduce TIME_WAIT impact on high-throughput servers.

## Side-by-Side Comparison

| Feature            | UDP                        | TCP                              |
|--------------------|----------------------------|----------------------------------|
| Connection model   | Connectionless             | Connection-oriented              |
| Reliability        | None (best-effort)         | Guaranteed delivery + ordering   |
| Byte ordering      | No                         | Yes (sequence numbers)           |
| Header size        | 8 bytes (fixed)            | 20–60 bytes                      |
| Setup cost         | None                       | 1.5 RTT (SYN, SYN-ACK, ACK)     |
| Flow control       | No                         | Yes (sliding window, rwnd)       |
| Congestion control | No                         | Yes (AIMD, slow-start, cubic)    |
| Broadcast/Multicast| Yes                        | No (unicast only)                |
| Typical latency    | Minimal                    | Added by handshake + acks        |
| Use cases          | DNS, streaming, gaming     | HTTP, SSH, FTP, databases        |

## Why Congestion Control Matters

UDP has no congestion control — an application using UDP can flood the network without restraint. This is why QUIC (which underlies HTTP/3) implements its own congestion control on top of UDP, and why UDP-based applications (like game servers) must be designed carefully to avoid becoming a nuisance.

TCP's congestion control is a **cooperative mechanism**: every TCP sender voluntarily backs off when it detects congestion, keeping the Internet stable. If all applications switched to uncongestion-controlled UDP, the Internet would experience **congestion collapse** — total throughput would plummet even as routers drop packets.
