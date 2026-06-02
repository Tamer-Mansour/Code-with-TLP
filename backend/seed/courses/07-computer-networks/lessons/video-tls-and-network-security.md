# Video: TLS, Cryptography, and Network Security

This video explains the mechanics of TLS (Transport Layer Security) from first principles: symmetric and asymmetric encryption, certificate authorities, the TLS 1.3 handshake, and how HTTPS protects data in transit. It also covers common network attacks (man-in-the-middle, DDoS, DNS spoofing) and how firewalls and IDS/IPS systems defend against them.

Key takeaways: TLS 1.3 reduces the handshake to one round trip using ECDHE key exchange; X.509 certificates bind a public key to a domain name and are signed by a trusted CA; forward secrecy ensures that compromise of the server's long-term key does not decrypt past sessions. Wireshark captures show the TLS ClientHello, ServerHello, and certificate exchange.

Timestamps: 0:00 — symmetric vs. asymmetric cryptography; ~20 min — X.509 certificates and PKI; ~40 min — TLS 1.3 handshake walkthrough; ~1:00 — HTTPS in the browser; ~1:20 — common attacks (MITM, DDoS, spoofing); ~1:40 — firewalls and VPNs.
