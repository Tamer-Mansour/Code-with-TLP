# Video: TCP and the Transport Layer

This video provides a thorough walkthrough of TCP and UDP, covering the three-way handshake, sequence numbers, acknowledgements, flow control via the sliding window, and congestion control (slow start and AIMD). It contrasts TCP's reliability guarantees against UDP's simplicity for latency-sensitive applications.

Key takeaways: TCP is connection-oriented and provides ordered, reliable delivery through retransmission and ACKs; UDP is connectionless and fast but provides no guarantees; understanding the congestion window (cwnd) is essential for reasoning about TCP throughput on high-latency links. Live demos show Wireshark traces of a TCP handshake and data transfer.

Timestamps: 0:00 — UDP vs TCP comparison; ~15 min — TCP three-way handshake; ~30 min — reliability and retransmission; ~50 min — congestion control; ~1:10 — modern variants (CUBIC, BBR, QUIC).
