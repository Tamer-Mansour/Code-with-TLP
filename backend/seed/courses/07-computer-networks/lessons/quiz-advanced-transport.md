# Quiz: TCP Congestion Control

**Q1. TCP's congestion control algorithm is called AIMD. What do the letters stand for, and what triggers the multiplicative decrease?**
- [ ] Adaptive Increase Minimum Decrease; triggered when rwnd drops to zero.
- [x] Additive Increase Multiplicative Decrease; triggered by packet loss (3 dup ACKs or timeout).
- [ ] Asynchronous Increment Maximum Decrement; triggered by high round-trip time.
- [ ] Asymmetric Increase Maximum Delay; triggered when ssthresh is exceeded.

**Q2. At the start of a new TCP connection, cwnd = 1 MSS. After 3 round trips with no packet loss, what is cwnd (assuming ssthresh > 8 MSS)?**
- [ ] 4 MSS (linear growth)
- [ ] 6 MSS
- [x] 8 MSS (doubles each RTT: 1 → 2 → 4 → 8)
- [ ] 3 MSS

**Q3. What is the key advantage of SACK (Selective Acknowledgement) over standard cumulative ACKs in TCP?**
- [ ] SACK reduces the TCP header size.
- [ ] SACK allows the receiver to buffer more data before sending ACKs.
- [x] SACK lets the receiver report exactly which byte ranges it has received, allowing the sender to retransmit only the missing segments rather than everything after the gap.
- [ ] SACK prevents duplicate ACKs from being sent.

**Q4. BBR congestion control differs from Cubic because:**
- [ ] BBR uses packet loss as the primary congestion signal, just like Cubic.
- [x] BBR models the bottleneck bandwidth and minimum RTT directly, rather than reacting to packet loss, keeping queues nearly empty.
- [ ] BBR increases cwnd by a cubic function of time since the last loss.
- [ ] BBR only works over high-speed fiber links.

**Q5. After a TCP timeout (not fast retransmit), what happens to cwnd and ssthresh in TCP Reno?**
- [ ] ssthresh stays the same; cwnd is halved.
- [ ] Both ssthresh and cwnd are halved.
- [x] ssthresh is set to cwnd/2 and cwnd is reset to 1 MSS, restarting slow start from scratch.
- [ ] cwnd is set to ssthresh and additive increase resumes immediately.
