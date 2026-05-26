# Quiz: Link Layer

**Q1. What is the standard maximum payload (MTU) of a classic Ethernet frame?**
- [ ] 512 bytes
- [ ] 1024 bytes
- [x] 1500 bytes
- [ ] 9000 bytes (that is a jumbo frame, not standard)

**Q2. What does a network switch do when it receives a frame destined for a MAC address not yet in its MAC table?**
- [ ] Drops the frame silently.
- [ ] Forwards the frame to the default gateway.
- [x] Floods the frame out all ports except the incoming port, then learns the source MAC.
- [ ] Sends an ARP request to discover the destination.

**Q3. What does ARP (Address Resolution Protocol) do?**
- [ ] Maps a domain name to an IP address on the LAN.
- [x] Maps a known IP address to the corresponding MAC address on the same subnet so a frame can be sent.
- [ ] Automatically assigns IP addresses to new hosts.
- [ ] Routes frames between different VLANs.

**Q4. Which error detection code does Ethernet use in its Frame Check Sequence (FCS) field?**
- [ ] MD5 hash
- [ ] Internet Checksum (one's complement)
- [ ] SHA-1
- [x] CRC-32 (32-bit Cyclic Redundancy Check)

**Q5. An attacker sends gratuitous ARP replies claiming their MAC address corresponds to the default gateway's IP. What attack is this, and what is its goal?**
- [ ] MAC flooding — fills the switch's CAM table so it broadcasts all frames.
- [x] ARP poisoning (ARP spoofing) — updates hosts' ARP caches so traffic to the gateway flows through the attacker (man-in-the-middle).
- [ ] A SYN flood — exhausts the gateway's TCP connection table.
- [ ] A replay attack — reuses old ARP packets to cause routing loops.

**Q6. How does a switch differ from a hub at Layer 2?**
- [ ] A hub forwards frames using a MAC address table; a switch broadcasts everything.
- [ ] A hub requires configuration; a switch is plug-and-play.
- [x] A hub broadcasts every incoming frame to all ports (one collision domain); a switch selectively forwards frames only to the destination port based on its MAC table.
- [ ] They are functionally identical; switches just have more ports.
