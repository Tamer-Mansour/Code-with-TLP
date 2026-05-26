# Quiz: Transport Layer

**Q1. Which transport protocol provides reliable, ordered delivery with flow and congestion control?**
- [ ] UDP
- [x] TCP
- [ ] IP
- [ ] ICMP

**Q2. What is the size of a UDP header?**
- [ ] 4 bytes
- [x] 8 bytes (exactly — always fixed)
- [ ] 20 bytes (that's the minimum TCP header)
- [ ] 40 bytes

**Q3. During TCP's three-way handshake, what does the server send immediately after receiving the initial SYN?**
- [ ] ACK only
- [ ] FIN (to reject the connection)
- [x] SYN-ACK (synchronize + acknowledge)
- [ ] RST (reset)

**Q4. What triggers TCP "fast retransmit" — retransmitting a segment without waiting for a timeout?**
- [ ] The receiver explicitly sends a NACK (negative acknowledgement).
- [ ] The sender's RTO timer expires after a fixed 200 ms.
- [x] The sender receives three duplicate ACKs for the same sequence number, indicating a gap.
- [ ] The receive window (rwnd) drops to zero.

**Q5. In TCP's AIMD congestion control, what happens to the congestion window (cwnd) when loss is detected via three duplicate ACKs (fast retransmit, TCP Reno)?**
- [ ] cwnd is immediately reset to 1 MSS and slow start restarts.
- [ ] cwnd grows by 1 MSS as usual.
- [x] ssthresh is set to cwnd/2, and cwnd is set to ssthresh (halved); slow start is NOT restarted.
- [ ] cwnd is doubled (the network has recovered).

**Q6. A TCP connection is uniquely identified by which of the following?**
- [x] The 4-tuple: (source IP, source port, destination IP, destination port).
- [ ] The destination IP address and port number alone.
- [ ] The session ID exchanged during the three-way handshake.
- [ ] The source MAC address and destination port number.
