# Quiz: Application Layer

**Q1. Which protocol is used to transfer email between two mail servers on the Internet?**
- [ ] IMAP
- [ ] POP3
- [x] SMTP
- [ ] HTTP

**Q2. What HTTP status code indicates that a resource has been permanently moved to a new URL?**
- [ ] 200 (OK)
- [ ] 302 (Found – temporary redirect)
- [x] 301 (Moved Permanently)
- [ ] 404 (Not Found)

**Q3. Which DNS record type maps a domain name to an IPv6 address?**
- [ ] A (maps to IPv4)
- [x] AAAA
- [ ] CNAME (alias to another name)
- [ ] MX (mail exchanger)

**Q4. What is the key architectural advantage of IMAP over POP3?**
- [ ] IMAP uses less server storage than POP3.
- [ ] IMAP is always faster because it compresses messages.
- [x] IMAP keeps email on the server, enabling consistent access from multiple devices simultaneously.
- [ ] IMAP encrypts all messages end-to-end by default.

**Q5. HTTP/2 improves over HTTP/1.1 primarily by:**
- [ ] Replacing TCP with UDP for all connections.
- [ ] Removing support for cookies to improve privacy.
- [x] Multiplexing multiple request/response streams over a single TCP connection using binary frames, eliminating HTTP-level head-of-line blocking.
- [ ] Encrypting all traffic by default.

**Q6. During a full recursive DNS lookup for "www.example.com", in what order are servers queried?**
- [ ] TLD server → root server → authoritative server
- [ ] Authoritative server → TLD server → root server
- [x] Root server → TLD server (.com) → authoritative server (ns1.example.com)
- [ ] Local DNS server → authoritative server directly
