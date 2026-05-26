# HTTP/2 and HTTP/3

HTTP/1.1 was designed in 1997 when a typical web page had a handful of resources. A modern page may load 100–300 separate resources (scripts, stylesheets, images, fonts, API calls). HTTP/2 and HTTP/3 were engineered specifically to eliminate the bottlenecks that emerge at this scale. Understanding them requires first understanding the problems they solve.

## Problems with HTTP/1.1 at Scale

### Head-of-Line Blocking

HTTP/1.1 is strictly sequential within a connection: the next request cannot be sent until the previous response is fully received. If the server is slow to generate one large response, all subsequent requests in the queue wait — **head-of-line (HoL) blocking**.

**Browser workaround:** open 6 parallel TCP connections per origin. 100 resources × 1.5 RTT handshake each = painful overhead, and ISPs/servers see 6× the connection load.

### Redundant Headers

HTTP/1.1 sends full headers with every request. For an API that makes 50 requests to the same server, the `Host`, `User-Agent`, `Accept`, `Authorization` (Bearer token), and `Cookie` headers are repeated identically in every request — potentially thousands of bytes per request, uncompressed.

### Plain Text Parsing

HTTP/1.1 is a text protocol. Parsers must scan byte-by-byte for CRLF sequences, handle chunked encoding, and manage framing without a binary length field. While not slow per se, binary framing is faster and more extensible.

## HTTP/2 (RFC 7540, 2015)

HTTP/2 was based on Google's SPDY protocol (2009) and standardized in 2015. It is a **binary, multiplexed** protocol that runs over a single TCP connection per origin.

### Binary Framing Layer

All HTTP/2 communication is split into **frames** — small binary messages with a fixed 9-byte header:

```
+──────────────────────────────────────+
│     Length (24 bits)                 │
│  Type (8 b) │  Flags (8 b)          │
│  Stream ID (31 bits)                 │
+──────────────────────────────────────+
│              Payload                 │
+──────────────────────────────────────+
```

Frame types include:
- `DATA` — response/request body.
- `HEADERS` — HTTP headers (compressed with HPACK).
- `SETTINGS` — connection configuration.
- `PING` — liveness check.
- `RST_STREAM` — cancel a single stream.
- `GOAWAY` — shut down the connection.
- `WINDOW_UPDATE` — per-stream flow control.

### Streams and Multiplexing

Each request-response pair is a **stream**, identified by an integer stream ID (client-initiated = odd; server-initiated = even). Multiple streams share the same TCP connection:

```
TCP Connection (single)
├── Stream 1: GET /index.html     → HEADERS frame + DATA frames
├── Stream 3: GET /style.css      → HEADERS frame + DATA frames
├── Stream 5: GET /app.js         → HEADERS frame + DATA frames
└── Stream 7: POST /api/track     → HEADERS frame + DATA frames
                    ↕ frames interleaved
```

All streams are interleaved at the frame level. If the server is slow on Stream 1, frames from Streams 3, 5, 7 can arrive unimpeded — HoL blocking is **eliminated at the HTTP layer**.

### HPACK Header Compression

HPACK (RFC 7541) compresses headers using:
1. **Static table**: 61 predefined header name-value pairs (e.g., `:method GET`, `content-type text/html`). Refer to them by index (1 byte).
2. **Dynamic table**: recently used headers added by both sides, evicted LRU. Sending a previously sent header costs just a 1-byte index.
3. **Huffman encoding**: for strings not in the table.

Result: the `Authorization: Bearer <256-char-JWT>` header sent 50 times costs ~260 bytes on the first request and ~1 byte on every subsequent request within the same connection.

### Server Push

The server can proactively send resources the client hasn't requested yet:
```
Client: GET /index.html
Server: PUSH_PROMISE stream 2 → /style.css
        PUSH_PROMISE stream 4 → /app.js
        DATA (index.html body)
        DATA (style.css body — stream 2)
        DATA (app.js body — stream 4)
```

The client receives CSS and JS before the browser even parses the HTML and discovers them. In practice, server push proved hard to implement correctly (push what's not already cached?) and has been deprecated in many implementations.

### Stream Prioritization

Each stream can have a **priority weight** (1–256) and a **dependency** on another stream. The server allocates its bandwidth proportionally: if stream A has weight 256 and stream B has weight 128, stream A gets roughly 2× the bandwidth.

### The Remaining Problem: TCP HoL Blocking

HTTP/2 multiplexes streams, but they all share **one TCP connection**. TCP provides an ordered byte stream: if a TCP segment is lost, *all* HTTP/2 streams on that connection stall until TCP retransmits and the gap is filled — TCP-level HoL blocking. On lossy networks (mobile, Wi-Fi), HTTP/2 can perform worse than HTTP/1.1 with 6 parallel connections because a single lost packet blocks everything instead of just one request.

## HTTP/3 (RFC 9114, 2022) and QUIC (RFC 9000, 2021)

HTTP/3 addresses TCP HoL blocking by replacing TCP with **QUIC** — a new transport protocol built on UDP, developed by Google and standardized by IETF.

### QUIC Features

**Built on UDP:** QUIC implements its own reliability, ordering, and congestion control in user space, on top of UDP. This allows:
- Faster iteration (deploy without kernel changes).
- Per-stream loss recovery (losing a UDP packet only affects the stream it belonged to).
- Built-in TLS 1.3 (QUIC packets are always encrypted).

**Connection ID:** QUIC identifies connections by a **Connection ID** (not by IP:port 4-tuple). When you switch from Wi-Fi to cellular, the Connection ID stays the same — the connection migrates transparently without a new handshake. TCP connections break when the IP changes.

**0-RTT Handshake:** On a repeat visit, the client sends data in the first packet — combining QUIC handshake and TLS 1.3 0-RTT:

```
RTT 0:  Client sends QUIC Initial + TLS ClientHello + HTTP request data
RTT 0:  Server responds with TLS ServerHello + application data
```

For new connections, the combined QUIC+TLS handshake takes **1 RTT** (vs. TCP's 1.5 RTT + TLS 1.3's 1 RTT = 2.5 RTT for HTTPS over TCP).

**Per-Stream Loss Recovery:** QUIC multiplexes streams with independent byte-stream state. A lost QUIC packet only blocks the single stream it belonged to:

```
QUIC stream 0: GET /index.html  →  one packet lost → only stream 0 stalls
QUIC stream 2: GET /style.css   →  unaffected
QUIC stream 4: GET /app.js      →  unaffected
```

### HTTP/3 on QUIC

HTTP/3 is HTTP semantics (methods, status codes, headers) running on QUIC streams instead of TCP. HPACK is replaced by **QPACK** — a variant that works correctly with QUIC's out-of-order delivery.

### Comparison Summary

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 (QUIC) |
|---------|---------|--------|--------------|
| Transport | TCP | TCP | QUIC (UDP) |
| Connections/origin | 6 (browser) | 1 | 1 |
| Protocol format | Text | Binary | Binary |
| Multiplexing | No | Yes (binary frames) | Yes (QUIC streams) |
| Header compression | None | HPACK | QPACK |
| HTTP HoL blocking | Yes | No | No |
| Transport HoL blocking | Per-connection | All streams blocked | Per-stream only |
| TLS required | No | Yes (in practice) | Always (QUIC) |
| 0-RTT | No | No | Yes |
| Connection migration | No | No | Yes (Connection ID) |

### Real-World Performance

- Google reports HTTP/3 reduces latency by 8–12% on fast networks, 20–40% on lossy/mobile networks.
- Cloudflare measures ~35% reduction in HTTP request failure rates with HTTP/3 vs HTTP/2.
- As of 2024, HTTP/3 is supported by Chrome, Firefox, Safari, Edge, and ~30% of the top 10 million websites.

The primary deployment consideration: UDP port 443 must be unblocked by firewalls (some enterprise networks block UDP 443, causing HTTP/3 to fall back to HTTP/2 automatically via HTTPS Alt-Svc headers).
