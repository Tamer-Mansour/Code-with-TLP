# TLS, Encryption, and Firewalls

**TLS (Transport Layer Security)** is the cryptographic protocol that secures most Internet traffic. When you see `https://` in your browser, TLS is providing confidentiality, integrity, and authentication. TLS sits between the Application and Transport layers — it is a transparent security wrapper that HTTP, SMTP, IMAP, and other application protocols use unchanged.

## Cryptography Foundations

### Symmetric Encryption

Both parties share the same secret key. A symmetric cipher is fast and efficient for bulk data encryption.

```
Encrypt: Plaintext + Key → Ciphertext
Decrypt: Ciphertext + Key → Plaintext
```

| Algorithm | Key size | Block/Stream | Notes |
|-----------|---------|-------------|-------|
| AES-128 | 128 bits | Block (128-bit blocks) | Standard; NIST-approved |
| AES-256 | 256 bits | Block | Higher security margin |
| ChaCha20 | 256 bits | Stream | Faster in software without AES-NI |

In TLS, symmetric encryption is always used with an **authenticated encryption** mode:
- **AES-GCM** (Galois/Counter Mode): encrypts and authenticates simultaneously; standard in TLS 1.3.
- **ChaCha20-Poly1305**: ChaCha20 + Poly1305 MAC; preferred on devices without hardware AES acceleration (e.g., mobile).

### Asymmetric Encryption (Public-Key Cryptography)

Each party has a **key pair**: a public key (share freely) and a private key (never share). The two keys are mathematically linked.

- **Encryption with public key**: only the private key can decrypt → confidential messages to a recipient.
- **Signature with private key**: anyone with the public key can verify → authentication and non-repudiation.

| Algorithm | Use in TLS | Notes |
|-----------|-----------|-------|
| RSA | Certificates, key exchange (TLS 1.2) | Widely supported; large key sizes (2048+ bits) |
| ECDSA | Certificate signatures | Elliptic curve; smaller keys (256-bit = 3072-bit RSA security) |
| X25519 | Key exchange (ECDHE) | Modern elliptic curve; fast; high security |

### Diffie-Hellman Key Exchange

DH allows two parties to derive a **shared secret** over a public channel without ever transmitting the secret itself. The mathematical one-wayness of discrete logarithms makes this secure.

Classical DH (RFC 3526):
```
Public parameters: prime p, generator g (both parties know these)

Alice: picks secret a  →  sends g^a mod p  →  Bob
Bob:  picks secret b  →  sends g^b mod p  →  Alice

Alice computes: (g^b)^a mod p = g^(ab) mod p  ← shared secret
Bob computes:   (g^a)^b mod p = g^(ab) mod p  ← same shared secret

Eavesdropper knows g^a mod p and g^b mod p but cannot compute g^(ab) mod p
efficiently (discrete logarithm problem).
```

**ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)** is the modern variant:
- Uses elliptic curve groups instead of integer modular arithmetic.
- **Ephemeral**: fresh key pair generated for every session.
- Provides **Perfect Forward Secrecy (PFS)**: compromise of the server's long-term private key does not compromise past sessions (each used a unique ephemeral key).

## TLS 1.3 Handshake — Detailed Walkthrough

TLS 1.3 (RFC 8446, 2018) reduced the handshake from 2 round trips (TLS 1.2) to **1 round trip**:

```
Client                                        Server
   │                                              │
   │── ClientHello ───────────────────────────►  │
   │   - supported cipher suites                 │
   │   - TLS version = 1.3                       │
   │   - client random (32 bytes)                │
   │   - key_share: ECDHE public key (X25519)    │
   │   - supported_groups, signature_algorithms  │
   │                                              │
   │◄── ServerHello ──────────────────────────── │
   │   - selected cipher suite (e.g. TLS_AES_    │
   │     128_GCM_SHA256)                          │
   │   - server random                           │
   │   - key_share: server's ECDHE public key    │
   │                                              │
   │   [Both sides now compute the shared secret  │
   │    via ECDHE, then derive handshake keys     │
   │    using HKDF. All subsequent messages are   │
   │    encrypted with these handshake keys.]     │
   │                                              │
   │◄── {EncryptedExtensions} ─────────────────── │
   │◄── {Certificate} (server's X.509 cert) ───── │
   │◄── {CertificateVerify} (signature over       │
   │    handshake transcript with server's        │
   │    private key)                              │
   │◄── {Finished} (HMAC over transcript) ─────── │
   │                                              │
   │── {Finished} ──────────────────────────────►│
   │   [Application data keys now derived]        │
   │══════ Application data (encrypted) ══════════│
```

**Key derivation:** TLS 1.3 uses HKDF (HMAC-based Key Derivation Function) to derive multiple keys from the ECDHE shared secret: handshake traffic keys, application traffic keys, and resumption keys. The derivation uses both the ECDHE output and the handshake transcript hash.

**0-RTT (Zero Round-Trip Time Resumption):** If client and server have a prior session, TLS 1.3 allows the client to send application data in the very first flight (alongside ClientHello), reducing latency for repeat connections. Caveat: 0-RTT data has **no replay protection** — not safe for non-idempotent requests.

### Certificate Validation

A **digital certificate** (X.509 v3) binds a domain name (Subject Alternative Names) to a public key, signed by a **Certificate Authority (CA)**:

```
Certificate chain:
  Root CA (DigiCert, Let's Encrypt, Comodo, …)
  → trusted by browser's built-in trust store (~150 root CAs)
    └─ Intermediate CA (often offline; signing handled by intermediate)
         └─ Leaf certificate: example.com
              - Subject: CN=example.com, SAN: example.com, www.example.com
              - Public key: ECDSA P-256
              - Validity: 2025-01-01 to 2025-12-31
              - Issuer: Let's Encrypt Authority X3
              - Signed by: Intermediate CA's private key
```

The browser verifies:
1. The certificate chain leads to a trusted root CA.
2. The certificate has not expired.
3. The domain name matches the certificate's Subject Alternative Names.
4. The certificate has not been revoked (via OCSP or CRL).

**Certificate Transparency (CT)**: since 2018, all publicly trusted CAs must log every certificate they issue to public append-only logs. Browsers check that a cert appears in CT logs, making it impossible for a CA to silently issue a rogue cert.

## TLS 1.2 vs TLS 1.3

| Feature | TLS 1.2 | TLS 1.3 |
|---------|---------|---------|
| Handshake RTTs | 2 | 1 |
| 0-RTT | No | Yes (with caveats) |
| Key exchange | RSA or (EC)DHE | ECDHE only |
| Authentication | RSA or ECDSA | RSA or ECDSA |
| Cipher suites | Many (incl. weak ones) | 5 strong suites only |
| Forward secrecy | Optional (RSA key exchange has none) | Always (ECDHE only) |
| Removed | — | RSA key exchange, RC4, DES, 3DES, MD5, SHA-1, compression |
| Server certificate | Sent unencrypted | Sent encrypted |

TLS 1.2 is still widely supported but is no longer recommended for new deployments. TLS 1.3 is the correct choice.

## Firewalls

A **firewall** inspects and filters network traffic based on policy rules. Modern firewalls come in several types:

### Stateless Packet Filter

Examines each packet individually based on L3/L4 headers — source IP, destination IP, source port, destination port, protocol. No memory of prior packets.

```
Rule 1: ALLOW  TCP from any  to 0.0.0.0/0  dport=443
Rule 2: ALLOW  TCP from any  to 0.0.0.0/0  dport=80
Rule 3: ALLOW  UDP from any  to 0.0.0.0/0  dport=53
Rule 4: DENY   ALL
```

Fast and simple, but cannot distinguish a new TCP SYN from a reply ACK — requires explicit rules for inbound return traffic.

### Stateful Firewall

Maintains a **connection tracking table**. Allows return traffic for established connections automatically, without needing explicit inbound rules for each service. Knows the difference between an unsolicited inbound packet and a response to an outbound request.

### Application-Layer Firewall / WAF (Web Application Firewall)

Inspects HTTP/HTTPS payloads — can detect SQL injection, XSS, directory traversal, malformed headers. Deployed in front of web applications. Examples: ModSecurity, AWS WAF, Cloudflare WAF.

### Linux iptables / nftables Example

```bash
# Stateful firewall on Linux (iptables):

# Allow loopback
iptables -A INPUT  -i lo -j ACCEPT

# Allow established/related return traffic (stateful)
iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow HTTPS from the internet
iptables -A INPUT  -p tcp --dport 443 -j ACCEPT

# Allow SSH only from a management subnet
iptables -A INPUT  -p tcp --dport 22 -s 10.0.1.0/24 -j ACCEPT

# Drop everything else inbound
iptables -A INPUT  -j DROP
```

### Network Security Zones

| Zone | Trust level | Contents |
|------|------------|---------|
| Internet | Untrusted | All external traffic |
| DMZ | Semi-trusted | Web servers, DNS, mail relays |
| Internal LAN | Trusted | Employee workstations, file servers |
| Restricted | Highly restricted | Financial systems, HR data, secrets |

Traffic from untrusted zones is heavily filtered before reaching more-trusted zones.

## Authentication Protocols

| Protocol | Mechanism | Security properties |
|----------|-----------|-------------------|
| Password over HTTPS | Knowledge factor | Vulnerable to phishing, credential stuffing |
| TOTP (RFC 6238) | Time-based OTP (Google Authenticator) | Phishing-resistant if server validates token live |
| FIDO2/WebAuthn | Hardware key (YubiKey) or biometric | Fully phishing-resistant; no shared secret |
| Kerberos | Ticket-based SSO (Active Directory) | Single sign-on; ticket replay risk |
| OAuth 2.0 + OIDC | Delegated authorization | Common for web API access |
| mTLS | Client certificate | Machine-to-machine; strong bilateral auth |

**Multi-factor authentication (MFA)** combines factors:
1. **Something you know**: password, PIN.
2. **Something you have**: TOTP app, hardware key.
3. **Something you are**: fingerprint, face ID.

FIDO2 eliminates phishing entirely — the authenticator signs a challenge that includes the origin URL, so a phishing site at `fake-bank.com` cannot successfully relay the signature to `real-bank.com`.
