# Client-Server Architecture and HTTP

When you open a web page, a structured conversation happens between your browser and a remote computer. This conversation follows rules defined by the **HTTP** protocol within a **client-server** architecture. Understanding this model explains how the web works, why web APIs are designed the way they are, and what every web developer needs to know before writing a single line of server code.

## The Client-Server Model

The Internet organises devices into two roles:

| Role | Description | Examples |
|------|-------------|---------|
| **Client** | Initiates requests for a service or resource | Web browser (Chrome, Firefox), mobile app, `curl`, Postman |
| **Server** | Listens for requests and provides the service | Web server (Nginx, Apache), app server (Django, Express), database server |

**Key properties:**
- A server is always **listening** (waiting) for requests on a specific port. A client **initiates** the conversation.
- One server can handle thousands (or millions) of clients simultaneously, using multiple processes, threads, or async I/O.
- Clients and servers communicate over a network—they may be on the same machine or continents apart.
- The model enforces **separation of concerns**: clients handle presentation and user interaction; servers handle data and business logic.

### Peer-to-Peer (P2P) as an Alternative

Not all networked systems are client-server. In **P2P** systems (BitTorrent, WebRTC), every participant is both a client and a server. P2P is efficient for large file distribution but harder to secure and manage than a centralised server model.

## Ports

A single computer runs many services simultaneously (web server, email, SSH, database…). **Ports** are numbered channels (0–65535) that distinguish different services on the same IP address.

Think of an IP address as a building address and a port as a room number. The IP gets you to the right building; the port tells you which room to knock on.

| Port | Protocol | Service |
|------|----------|---------|
| 20, 21 | FTP | File transfer (data and control) |
| 22 | SSH | Secure shell (remote terminal) |
| 25 | SMTP | Outgoing email |
| 53 | DNS | Domain name lookups (UDP and TCP) |
| 80 | HTTP | Unencrypted web |
| 110 | POP3 | Incoming email (older) |
| 143 | IMAP | Incoming email (modern) |
| 443 | HTTPS | Encrypted web |
| 3306 | MySQL | Database connections |
| 5432 | PostgreSQL | Database connections |
| 6379 | Redis | In-memory data store |
| 8080 | HTTP alt | Development web servers often use this |

Ports 0–1023 are **well-known ports** reserved for system services. Ports 1024–49151 are registered ports for applications. Ports 49152–65535 are ephemeral (temporary) ports assigned to client connections.

When your browser connects to `https://example.com`, it opens a connection to port **443** at example.com's IP address.

## HTTP: HyperText Transfer Protocol

**HTTP** is the application-layer protocol the web uses to transfer data. It was designed by Tim Berners-Lee in 1989 and has evolved from HTTP/1.0 to HTTP/3. Every web page load is a series of HTTP request-response transactions.

HTTP is a **text-based, stateless** protocol:
- **Text-based**: requests and responses are human-readable ASCII text (in HTTP/1.x; HTTP/2+ uses binary frames).
- **Stateless**: each request is independent. The server has no built-in memory of previous requests. Cookies and session tokens are how applications add statefulness on top.

### HTTP Methods

HTTP defines **methods** (also called verbs) that indicate the desired action:

| Method | Purpose | Body? | Idempotent? | Safe? |
|--------|---------|-------|-------------|-------|
| GET | Retrieve a resource | No | Yes | Yes |
| HEAD | Retrieve headers only (no body) | No | Yes | Yes |
| POST | Submit data; create new resource | Yes | No | No |
| PUT | Replace entire resource | Yes | Yes | No |
| PATCH | Partially update resource | Yes | No | No |
| DELETE | Remove resource | Optional | Yes | No |
| OPTIONS | Discover what methods are allowed | No | Yes | Yes |

**Idempotent**: calling the method multiple times has the same effect as calling it once. PUT and DELETE are idempotent; POST is not (two POST requests create two records).

**Safe**: the method does not modify server state. GET and HEAD are safe; POST, PUT, DELETE are not.

### An HTTP Request in Full Detail

When you visit `https://example.com/about`:

```
GET /about HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: session=abc123; theme=dark
```

Components:
- **Request line**: method (`GET`), path (`/about`), HTTP version (`HTTP/1.1`)
- **Headers**: key-value pairs with metadata
  - `Host`: which virtual host is being requested (one server can host many domains)
  - `User-Agent`: browser and OS identification
  - `Accept`: what content types the client can handle
  - `Cookie`: client-side state being sent to the server

### An HTTP Response in Full Detail

```
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 12:00:00 GMT
Server: nginx/1.24.0
Content-Type: text/html; charset=utf-8
Content-Length: 4823
Content-Encoding: gzip
Cache-Control: public, max-age=3600
ETag: "abc123def456"
Set-Cookie: visit=1; Path=/; Secure; HttpOnly

<!DOCTYPE html>
<html lang="en">
  <head>…</head>
  <body>…</body>
</html>
```

Components:
- **Status line**: HTTP version, status code, status text
- **Headers**: metadata about the response
  - `Content-Type`: what format the body is in
  - `Cache-Control`: how long the client/proxy can cache this response
  - `Set-Cookie`: server asking the client to store a cookie
- **Blank line**: separates headers from body
- **Body**: the actual content (HTML, JSON, image bytes, etc.)

### HTTP Status Codes

Status codes are 3-digit numbers grouped by category:

| Range | Category | Meaning |
|-------|---------|---------|
| 1xx | Informational | Request received, continuing |
| 2xx | Success | Request processed successfully |
| 3xx | Redirection | Client must take further action |
| 4xx | Client error | The request had a problem |
| 5xx | Server error | The server failed to process a valid request |

**Common codes to know:**

| Code | Name | When it occurs |
|------|------|---------------|
| 200 | OK | Normal success |
| 201 | Created | POST that created a new resource |
| 204 | No Content | Success but no body (e.g., DELETE) |
| 301 | Moved Permanently | URL has changed forever; update your bookmarks |
| 302 | Found | Temporary redirect |
| 304 | Not Modified | Cached version is still valid; use it |
| 400 | Bad Request | Malformed syntax, invalid parameters |
| 401 | Unauthorized | Authentication required (not yet logged in) |
| 403 | Forbidden | Authenticated but not permitted |
| 404 | Not Found | Resource does not exist |
| 405 | Method Not Allowed | e.g., sending DELETE to a read-only endpoint |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unhandled exception in server code |
| 502 | Bad Gateway | Proxy received invalid response from upstream |
| 503 | Service Unavailable | Server overloaded or down for maintenance |

## HTTPS: Encrypted HTTP

**HTTPS** (HTTP Secure) wraps HTTP inside **TLS** (Transport Layer Security, formerly SSL), encrypting all communication between client and server.

Without HTTPS, anyone on the same network (Wi-Fi hotspot, ISP, a router in between) can read your data in plaintext—including passwords, credit card numbers, and session tokens. This is called a **man-in-the-middle attack**.

What TLS provides:
1. **Encryption** — data is encrypted so eavesdroppers see only ciphertext.
2. **Authentication** — the server proves its identity with a digital certificate issued by a trusted Certificate Authority (CA), preventing impersonation.
3. **Integrity** — a MAC (Message Authentication Code) ensures data was not tampered with in transit.

The TLS handshake happens before any HTTP data is exchanged:

```
Client                                    Server
  │─── ClientHello (TLS version, ciphers) ────→│
  │←─── ServerHello + Certificate ────────────│
  │←─── ServerHelloDone ──────────────────────│
  │─── ClientKeyExchange ─────────────────────→│
  │─── ChangeCipherSpec + Finished ───────────→│
  │←─── ChangeCipherSpec + Finished ──────────│
  │═══════ Encrypted HTTP traffic begins ══════│
```

All modern websites use HTTPS. Browsers mark HTTP sites as "Not secure" and may block them.

## A Complete Web Page Load: Step by Step

```
1. User types https://news.example.com in the browser
        ↓
2. Browser checks DNS cache (miss → queries DNS)
   DNS resolves news.example.com → 203.0.113.5
        ↓
3. Browser opens a TCP connection to 203.0.113.5 on port 443
   (TCP 3-way handshake: SYN → SYN-ACK → ACK)
        ↓
4. TLS handshake (verify certificate, negotiate encryption keys)
        ↓
5. Browser sends HTTP request:
   GET / HTTP/1.1
   Host: news.example.com
        ↓
6. Server sends HTTP response:
   200 OK + HTML body
        ↓
7. Browser parses HTML, discovers linked resources:
   - <link rel="stylesheet" href="/main.css">
   - <script src="/app.js">
   - <img src="/hero.jpg">
        ↓
8. Browser sends parallel GET requests for each asset
   (often reusing the existing TCP/TLS connection via HTTP Keep-Alive
    or HTTP/2 multiplexing)
        ↓
9. Browser assembles the DOM, applies CSS, runs JavaScript
        ↓
10. Page is visible. Total time: typically 0.5–3 seconds
```

## REST: A Design Style for Web APIs

**REST (Representational State Transfer)** is a set of architectural principles for designing web APIs that use HTTP naturally:

- Use URLs to identify resources: `/users/42`, `/posts/123/comments`
- Use HTTP methods for actions: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- Responses use standard formats (JSON or XML)
- Stateless: each request contains all the information needed; the server stores no client state

A RESTful API for a blog might look like:

```
GET    /posts          → list all posts
POST   /posts          → create a new post (body: JSON)
GET    /posts/5        → get post with id=5
PUT    /posts/5        → replace post 5 (body: full replacement JSON)
PATCH  /posts/5        → update fields of post 5 (body: partial JSON)
DELETE /posts/5        → delete post 5
```

## Common Misconceptions

**"HTTP and TCP are the same."**
HTTP is an application-layer protocol that defines what to request and how responses are structured. TCP is a transport-layer protocol that provides reliable delivery of bytes. HTTP typically runs on top of TCP (and TLS for HTTPS). They are distinct layers.

**"A 404 means the server is down."**
A 404 means the server is **running and responded**, but the specific resource does not exist. If the server were down, you would get a connection error (no response at all) or a 502/503. 404 is a client error—you (or a broken link) asked for something that is not there.

**"Cookies are always tracking you."**
Cookies have many legitimate uses: keeping you logged in (session cookies), saving preferences, shopping cart items. Tracking cookies that follow you across sites are one specific use of the cookie mechanism, not the mechanism itself.

## Key Takeaways

- The **client-server model** separates devices into requesters (clients) and responders (servers); servers listen on ports.
- **Ports** distinguish services on the same IP: HTTP=80, HTTPS=443, SSH=22.
- **HTTP** is a text-based, stateless request-response protocol; methods (GET, POST, PUT, DELETE) indicate intended actions.
- **Status codes** communicate outcomes: 2xx=success, 3xx=redirect, 4xx=client error, 5xx=server error.
- **HTTPS** adds TLS to HTTP, providing encryption, authentication, and integrity—essential for any real application.
- Every page load involves DNS lookup, TCP connection, TLS handshake, and multiple HTTP round trips.
