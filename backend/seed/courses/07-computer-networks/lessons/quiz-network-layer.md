# Quiz: Network Layer

**Q1. What does "longest prefix match" mean in IP routing?**
- [ ] The router prefers routes with the longest AS-PATH attribute.
- [x] When multiple routing table entries match a destination IP, the router selects the one with the most specific (longest) prefix length.
- [ ] The router picks the route that was learned most recently.
- [ ] Packets are forwarded to the interface with the longest uptime.

**Q2. Which routing protocol is used to exchange routes between Autonomous Systems across the Internet?**
- [ ] OSPF (Interior Gateway Protocol — link-state)
- [ ] RIP (Interior Gateway Protocol — distance-vector)
- [ ] EIGRP (Cisco hybrid IGP)
- [x] BGP (Border Gateway Protocol — path-vector, Exterior Gateway Protocol)

**Q3. What is the broadcast address for the subnet 172.16.4.0/22?**
- [ ] 172.16.4.255 (that's only the /24 broadcast)
- [ ] 172.16.5.255 (only covers /23)
- [x] 172.16.7.255 (/22 covers 172.16.4.0–172.16.7.255)
- [ ] 172.16.255.255 (that would be /16)

**Q4. What problem does Network Address Translation (NAT) solve?**
- [ ] It encrypts all outbound packets for privacy.
- [x] It allows many private IPv4 devices to share a single public IP address, conserving the limited IPv4 address space.
- [ ] It speeds up routing by caching frequently accessed IP addresses.
- [ ] It automatically converts IPv4 packets to IPv6 at the gateway.

**Q5. How many usable host addresses does a /28 subnet provide?**
- [ ] 32 total, 30 usable
- [ ] 16 total, 16 usable
- [x] 16 total, 14 usable (subtract network and broadcast addresses)
- [ ] 32 total, 32 usable

**Q6. Which feature is present in IPv6 but absent in IPv4?**
- [ ] Fragmentation by intermediate routers (IPv4 has this; IPv6 does not).
- [ ] Broadcast addresses (IPv4 has these; IPv6 uses multicast instead).
- [x] Stateless Address Autoconfiguration (SLAAC) — hosts derive their own global address from the prefix.
- [ ] A TTL field in the header (IPv4 calls it TTL; IPv6 calls it Hop Limit — both exist).
