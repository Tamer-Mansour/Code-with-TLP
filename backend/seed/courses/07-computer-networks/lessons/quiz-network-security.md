# Quiz: Network Security Basics

**Q1. What does TLS provide that plain TCP alone does not?**
- [ ] Reliable, ordered delivery of segments.
- [ ] Lower latency by switching from TCP to UDP.
- [x] Confidentiality (encryption), integrity (MAC), and server authentication (certificate) for the application data stream.
- [ ] Automatic IP address assignment.

**Q2. Which key-exchange mechanism provides Perfect Forward Secrecy (PFS)?**
- [ ] RSA key exchange — the server decrypts the premaster secret using its private key.
- [x] ECDHE (Elliptic Curve Diffie-Hellman Ephemeral) — ephemeral keys mean past sessions cannot be decrypted even if the server's long-term key is later compromised.
- [ ] MD5-based key derivation.
- [ ] AES-256 symmetric encryption.

**Q3. What is a DDoS amplification attack?**
- [x] The attacker spoofs the victim's IP address and sends small requests to servers (DNS, NTP) that return large responses, overwhelming the victim with traffic it didn't request.
- [ ] The attacker installs malware on a single server to exhaust its CPU.
- [ ] The attacker sends a SYN flood using thousands of botnet machines simultaneously.
- [ ] The attacker intercepts DNS replies and silently redirects the victim to a malicious server.

**Q4. A stateful firewall differs from a stateless packet filter because it:**
- [ ] Can inspect HTTP payloads for SQL injection patterns.
- [ ] Only filters based on IP addresses, ignoring ports.
- [x] Tracks the state of active connections and automatically permits return traffic for established sessions without requiring explicit inbound rules.
- [ ] Operates at the application layer and understands HTTP methods.

**Q5. Which attack does DNSSEC help prevent, and how?**
- [x] DNS cache poisoning — DNSSEC adds cryptographic signatures to DNS records; resolvers verify the signature chain up to the root, making it infeasible to inject forged records.
- [ ] TCP SYN flood — DNSSEC validates source IP addresses.
- [ ] ARP spoofing — DNSSEC authenticates MAC-to-IP mappings.
- [ ] DDoS amplification — DNSSEC reduces the response size of DNS queries.

**Q6. In a TLS 1.3 handshake, when is the server's certificate sent, and how is it protected?**
- [ ] The certificate is sent in the ClientHello, before any key exchange.
- [ ] The certificate is always sent unencrypted so the client can verify it before computing keys.
- [x] The certificate is sent after the ECDHE key exchange completes, and it is encrypted using the handshake traffic key derived from the ECDHE shared secret.
- [ ] The certificate is never sent; the server is authenticated only by the Finished message MAC.
