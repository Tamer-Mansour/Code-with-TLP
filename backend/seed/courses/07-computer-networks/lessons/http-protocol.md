# HTTP: The Web's Protocol

**HTTP (HyperText Transfer Protocol)** is the application-layer protocol that powers the World Wide Web. Every time you load a webpage, your browser sends an HTTP request and the server replies with an HTTP response. HTTP runs over TCP (or QUIC in HTTP/3) and is a text-based, stateless, request-response protocol.

## Request/Response Model

HTTP is a **client-server** protocol. The client (browser) always initiates; the server responds. This is the simplest possible application model, and its simplicity is why HTTP has been reused far beyond web pages: APIs, microservices, webhooks, and health checks all speak HTTP.

```
Client (Browser)                      Server (nginx, Apache, etc.)
      │                                          │
      │──── TCP SYN ─────────────────────────►  │
      │◄─── SYN-ACK ──────────────────────────  │
      │──── ACK ──────────────────────────────► │
      │    [TCP connection established]          │
      │──── HTTP GET /index.html HTTP/1.1 ────► │
      │◄─── HTTP/1.1 200 OK + HTML body ──────  │
      │                                          │
```

## HTTP Request Format — Full Walkthrough

An HTTP/1.1 request has four parts separated by CRLF (`\r\n`):

```
GET /search?q=http+protocol HTTP/1.1\r\n
Host: www.example.com\r\n
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124\r\n
Accept: text/html,application/xhtml+xml;q=0.9,*/*;q=0.8\r\n
Accept-Encoding: gzip, deflate, br\r\n
Accept-Language: en-US,en;q=0.9\r\n
Connection: keep-alive\r\n
\r\n
```

1. **Request line** — `METHOD path HTTP/version`. The path includes the query string.
2. **Headers** — key-value pairs, one per line, terminated by `\r\n`.
3. **Blank line** — a single `\r\n` signals the end of headers.
4. **Body** — present for POST/PUT/PATCH; absent for GET/DELETE.

Key request headers:

| Header | Purpose | Example |
|--------|---------|---------|
| `Host` | Target server (required in HTTP/1.1) | `www.example.com` |
| `User-Agent` | Client software identifier | `Mozilla/5.0 ...` |
| `Accept` | Desired response content types | `text/html, */*` |
| `Accept-Encoding` | Compression formats the client supports | `gzip, br` |
| `Content-Type` | Body format (for POST/PUT) | `application/json` |
| `Content-Length` | Body size in bytes | `312` |
| `Authorization` | Credentials | `Bearer eyJhbG...` |
| `Cookie` | Session tokens | `session=abc123` |

## HTTP Response Format — Full Walkthrough

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html; charset=UTF-8\r\n
Content-Length: 2345\r\n
Content-Encoding: gzip\r\n
Cache-Control: max-age=3600\r\n
ETag: "a1b2c3d4"\r\n
Set-Cookie: session_id=xyz; HttpOnly; Secure; SameSite=Lax\r\n
Strict-Transport-Security: max-age=31536000; includeSubDomains\r\n
X-Content-Type-Options: nosniff\r\n
\r\n
<gzip-compressed HTML body>
```

1. **Status line** — `HTTP/version STATUS_CODE Reason`.
2. **Headers** — metadata about the response.
3. **Blank line** — end of headers.
4. **Body** — the actual content.

## HTTP Methods

| Method  | Purpose                          | Safe? | Idempotent? | Body? |
|---------|----------------------------------|-------|-------------|-------|
| GET     | Retrieve a resource              | Yes   | Yes         | No    |
| HEAD    | Get headers only (no body)       | Yes   | Yes         | No    |
| OPTIONS | Ask what methods are allowed     | Yes   | Yes         | No    |
| POST    | Submit data, create resource     | No    | No          | Yes   |
| PUT     | Replace a resource entirely      | No    | Yes         | Yes   |
| PATCH   | Partially update a resource      | No    | No          | Yes   |
| DELETE  | Delete a resource                | No    | Yes         | No    |

- **Safe**: the request does not change server state (read-only).
- **Idempotent**: sending the same request multiple times has the same effect as sending it once. Important for retries after network failures.

## Common Status Codes

| Code | Meaning               | When used |
|------|-----------------------|-----------|
| 200  | OK                    | Successful GET, PUT, PATCH |
| 201  | Created               | Successful POST that created a resource |
| 204  | No Content            | Successful DELETE or action with no body |
| 301  | Moved Permanently     | URL changed forever; update bookmarks |
| 302  | Found (Temporary)     | URL changed temporarily |
| 304  | Not Modified          | Cached version is still fresh |
| 400  | Bad Request           | Malformed syntax, invalid parameters |
| 401  | Unauthorized          | Missing or invalid authentication |
| 403  | Forbidden             | Authenticated but not authorized |
| 404  | Not Found             | Resource doesn't exist |
| 405  | Method Not Allowed    | e.g., POST to a read-only endpoint |
| 429  | Too Many Requests     | Rate limiting |
| 500  | Internal Server Error | Unhandled exception on server |
| 502  | Bad Gateway           | Upstream server returned an error |
| 503  | Service Unavailable   | Server overloaded or in maintenance |

## Cookies and Sessions

HTTP is **stateless** — each request is independent; the server has no memory of previous requests from the same client. Servers maintain sessions using **cookies** — small key-value tokens stored in the browser and transmitted with every subsequent request to the same domain.

```
Server → browser:
  Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict; Max-Age=86400

Browser → server (every subsequent request):
  Cookie: session_id=abc123
```

- `HttpOnly` prevents JavaScript from reading the cookie — mitigates XSS theft.
- `Secure` transmits the cookie only over HTTPS.
- `SameSite=Strict` blocks the cookie from being sent in cross-site requests — mitigates CSRF.

## Caching

HTTP has a rich caching model that dramatically reduces server load and latency for repeat visits:

- `Cache-Control: max-age=3600` — the browser may use a cached copy for up to 1 hour without checking the server.
- `Cache-Control: no-cache` — always revalidate with the server before using cached copy.
- `Cache-Control: no-store` — never cache (sensitive data).
- `ETag: "a1b2c3"` + `If-None-Match: "a1b2c3"` — server returns 304 if the content hasn't changed.
- `Last-Modified` + `If-Modified-Since` — time-based conditional GET.

## HTTP Versions

### HTTP/1.0 (1996)
One request per TCP connection. Every request requires a full TCP handshake (1.5 round trips) before any data flows — catastrophically inefficient for pages with many resources.

### HTTP/1.1 (1997 — RFC 2616, updated 2014)
Introduced **persistent connections** (`Connection: keep-alive` is now the default). One TCP connection can carry many sequential request-response pairs. Also added **pipelining** (send multiple requests without waiting for each response), though pipelining is rarely used in practice because of **head-of-line blocking** — a slow response blocks all later responses in the queue.

### HTTP/2 (2015 — RFC 7540)
Key improvements:
- **Binary framing layer**: all messages are split into binary frames, not text. Faster to parse, easier to multiplex.
- **Multiplexing**: multiple streams (requests) share a single TCP connection, interleaved as frames. No head-of-line blocking at the HTTP level.
- **HPACK header compression**: headers are compressed using a shared compression table, drastically reducing overhead on APIs that send large `Authorization` headers repeatedly.
- **Server push**: server can proactively send resources the client hasn't requested yet.

HTTP/2 still suffers from **TCP-level head-of-line blocking**: if one TCP segment is lost, all HTTP/2 streams on that connection stall while TCP retransmits.

### HTTP/3 (2022 — RFC 9114)
HTTP/3 replaces TCP with **QUIC** (RFC 9000), a UDP-based transport:
- QUIC multiplexes streams with independent loss recovery — a lost UDP packet only stalls the one stream it belongs to, not all streams.
- **0-RTT connection establishment**: repeat visitors can send data in the first packet, achieving sub-millisecond latency improvements.
- Built-in TLS 1.3 — QUIC encrypts everything by default.

| Feature                  | HTTP/1.1    | HTTP/2       | HTTP/3 (QUIC) |
|--------------------------|-------------|--------------|----------------|
| Transport                | TCP         | TCP          | QUIC (UDP)     |
| Connections per origin   | 6 (browsers)| 1            | 1              |
| Multiplexing             | No          | Yes          | Yes            |
| Header compression       | No          | HPACK        | QPACK          |
| HoL blocking (HTTP)      | Yes         | No           | No             |
| HoL blocking (transport) | Yes         | Yes (TCP)    | No             |
| TLS required             | No          | Yes (in practice) | Always    |
| 0-RTT                    | No          | No           | Yes            |

As of 2024, HTTP/3 accounts for roughly 30% of web traffic. Major CDNs (Cloudflare, Akamai, Google) support it by default.
