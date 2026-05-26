# Email Protocols and Application Models

Email may seem old-fashioned, but its architecture cleanly illustrates important application-layer design patterns: store-and-forward messaging, separation of submission from retrieval, and the contrast between server-centric and peer-to-peer models. This lesson covers email protocols in depth, then compares the two dominant application architectures.

## Email Architecture

Email delivery involves distinct components working together:

```
[Alice's MUA]
      │ SMTP (port 587, STARTTLS)
      ▼
[Alice's Mail Server / MTA]
      │ SMTP (port 25)         ← DNS MX lookup to find Bob's mail server
      ▼
[Bob's Mail Server / MDA]
      │
  [Mailbox storage]
      │
[Bob's MUA] ← IMAP (port 993) or POP3 (port 995)
```

- **MUA** (Mail User Agent): the email client — Outlook, Thunderbird, Apple Mail, Gmail web app.
- **MTA** (Mail Transfer Agent): server software that routes and forwards email between mail servers — Postfix, Exim, Sendmail, Microsoft Exchange.
- **MDA** (Mail Delivery Agent): deposits the message into the recipient's mailbox — Dovecot, Cyrus.
- **Mailbox**: persistent storage on the mail server.

## Email Protocols

### SMTP (Simple Mail Transfer Protocol) — RFC 5321

SMTP is used to **send** email. It is a push protocol — the sending server connects to the receiving server and delivers the message. SMTP uses a text-based, human-readable command-response dialog.

Port assignments:
- **Port 25**: SMTP relay (server-to-server). Many ISPs block outbound port 25 from residential connections to reduce spam.
- **Port 587**: SMTP submission (client-to-server, requires authentication + STARTTLS).
- **Port 465**: SMTP over implicit TLS (older standard, still widely used).

A real SMTP session (simplified):

```
TCP connect to mail.bob.com:25
Server: 220 mail.bob.com ESMTP Postfix
Client: EHLO mail.alice.com
Server: 250-mail.bob.com Hello
        250-SIZE 52428800
        250-STARTTLS
        250 SMTPUTF8
Client: STARTTLS
Server: 220 2.0.0 Ready to start TLS
[TLS handshake completes]
Client: MAIL FROM:<alice@alice.com> SIZE=1234
Server: 250 2.1.0 Ok
Client: RCPT TO:<bob@bob.com>
Server: 250 2.1.5 Ok
Client: DATA
Server: 354 End data with <CR><LF>.<CR><LF>
Client: From: alice@alice.com
        To: bob@bob.com
        Subject: Meeting tomorrow
        Date: Mon, 26 May 2025 09:00:00 +0000
        MIME-Version: 1.0
        Content-Type: text/plain; charset=UTF-8

        Hi Bob, are you free tomorrow?
        .
Server: 250 2.0.0 Ok: queued as 4F7B2A
Client: QUIT
Server: 221 2.0.0 Bye
```

The final `.` (period on a line by itself) terminates the message body. SMTP is still fundamentally the same protocol as it was in 1982, with security added via STARTTLS and authentication extensions.

### Anti-Spam: SPF, DKIM, DMARC

Because SMTP was designed without authentication, anyone can claim `MAIL FROM:<ceo@yourbank.com>`. Three DNS-based mechanisms combat spoofing:

| Mechanism | How it works |
|-----------|-------------|
| **SPF** (Sender Policy Framework) | TXT record lists authorized IP ranges for sending email from a domain. Receiving server checks if the sending IP is in the list. |
| **DKIM** (DomainKeys Identified Mail) | Sending server signs email headers/body with its private key. Public key published in DNS TXT record. Receiver validates. |
| **DMARC** | Policy record: what to do if SPF/DKIM fails (none/quarantine/reject). Enables aggregate reporting. |

### IMAP (Internet Message Access Protocol) — RFC 3501

IMAP is used to **retrieve and manage** email that remains on the server.

- **Port 143** (STARTTLS) / **993** (implicit TLS).
- Email is stored permanently on the server; the client synchronizes folder state.
- Supports folders, flags (read, starred, deleted), server-side search.
- Multiple devices (phone + laptop + webmail) all see the same inbox — this is IMAP's key advantage.
- IMAP4rev2 (RFC 9051, 2021) adds improvements including more secure authentication.

### POP3 (Post Office Protocol v3) — RFC 1939

POP3 downloads email to the client device, typically deleting it from the server.

- **Port 110** (plain) / **995** (TLS).
- Simple protocol: connect, authenticate, list, retrieve, delete, quit.
- Suitable for a single-device user who wants full offline access.
- Poor fit for multi-device usage.

| Feature               | IMAP                       | POP3                      |
|-----------------------|----------------------------|---------------------------|
| Email location        | Stays on server             | Downloaded to client      |
| Multi-device access   | Yes (full sync)             | No (first device gets it) |
| Server-side folders   | Yes                         | No                        |
| Server-side search    | Yes                         | No                        |
| Offline access        | Partial (client caches)     | Full (local copy)         |
| Server storage needed | Significant                 | Minimal after download    |
| Protocol complexity   | High (stateful, commands)   | Low                       |

## Client-Server Model

In the **client-server** model, a small number of always-on servers with static IP addresses and large resources serve many intermittent clients.

```
Client A ─────────────────────────► Server
Client B ─────────────────────────►        (always on, public IP)
Client C ─────────────────────────►
```

The server must scale horizontally (add machines) as user count grows.

**Examples:** HTTP/HTTPS web, DNS (sort of), SMTP, IMAP, SSH, relational database queries.

**Advantages:** Centralized control and management; easy to secure and audit; consistent behavior; easy to update.

**Disadvantages:** Single point of failure (mitigated by replication); server is the bandwidth bottleneck; cost scales with usage.

## Peer-to-Peer (P2P) Model

In the **P2P** model, there is no fixed server. Every node (*peer*) is simultaneously a client and a server. The system is *self-scaling* — adding more peers increases both demand and capacity.

```
  A ──── B
  │  ╲╱  │
  │  ╱╲  │
  C ──── D
```

### BitTorrent — canonical P2P example

1. A **.torrent file** or **magnet link** contains a hash of the content and tracker URLs.
2. The **tracker** (or a DHT — Distributed Hash Table — for trackerless torrents) helps peers find each other.
3. The file is split into **pieces** (typically 256 KB–4 MB). Each piece has a SHA-1 hash for integrity verification.
4. Peers download pieces from multiple other peers simultaneously (**parallelism**) and upload pieces to others while downloading (**tit-for-tat** incentive).
5. A **seeder** is a peer that has the full file. A **leecher** is still downloading.

Throughput scales with the number of seeders — the exact opposite of client-server, where adding users hurts performance.

**Advantages:** Self-scaling (more users = more capacity); no central infrastructure cost; resilient — no single point of failure.

**Disadvantages:** Harder to control content; variable performance depending on peer availability; complex protocols; susceptible to free-riding.

## Hybrid Models

Modern systems rarely use pure client-server or pure P2P:

- **WhatsApp / Signal**: end-to-end encryption uses a P2P key agreement protocol; but messages are routed through Signal's central servers (acting as a reliable relay), which delete messages after delivery.
- **CDN (Content Delivery Network)**: geographically distributed caches that pre-position content near users. Looks like P2P from a topology perspective (data comes from many different edge nodes) but is centrally managed. Cloudflare, Akamai, Fastly are examples.
- **WebRTC**: the signaling channel (offer/answer, ICE candidates) goes through a central server; once the P2P path is established, media flows directly peer-to-peer, bypassing the server.
- **Blockchain / Bitcoin**: fully decentralized P2P network — no authoritative node, all nodes validate transactions. Sacrifices speed and simplicity for censorship resistance.

Understanding which model a system uses predicts its scalability, failure modes, operational cost, and security surface.
