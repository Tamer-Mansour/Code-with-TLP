# Sliding Window Protocols

Sending one frame at a time and waiting for an acknowledgement before sending the next is correct but catastrophically slow. A 1 Gbps satellite link with a 600 ms round-trip time can hold 75 megabytes of data "in flight" — yet Stop-and-Wait keeps only one frame in flight at a time. **Sliding window protocols** solve this by letting the sender transmit multiple unacknowledged frames simultaneously.

## Stop-and-Wait: The Baseline

The simplest ARQ (Automatic Repeat reQuest) protocol:

1. Sender transmits frame 0.
2. Sender waits for ACK 0.
3. On ACK: send frame 1. On timeout or NAK: resend frame 0.

**Efficiency** = useful_data / (useful_data + idle_waiting_time).

For a link with propagation delay `a = Tp / Tf` (propagation time / frame transmission time):

```
Utilization = 1 / (1 + 2a)
```

When `a >> 1` (satellite, high-speed WAN), utilization collapses to near zero. A window size `W` is needed:

```
Utilization = W / (1 + 2a)    when W < 1 + 2a
```

## Go-Back-N (GBN)

The sender may have up to `W` unacknowledged frames outstanding. Frames are numbered with sequence numbers modulo `2^n` (for an n-bit field). GBN requires `W ≤ 2^n - 1`.

**Key behaviors:**

- The sender maintains a window of up to `W` outstanding (unACKed) frames.
- The receiver maintains only a single expected sequence number. It accepts only in-order frames and discards any out-of-order frames.
- ACKs are cumulative: `ACK(n)` means "all frames up through n-1 received correctly."
- On a timeout or a NAK: the sender retransmits the errored frame **and all subsequent frames** in the window — even if some were correctly received.

```
Window size W = 4, sequence bits n = 3 (seq 0-7)

Sender:   [0][1][2][3]──────────────────────────
                       lost                     
Receiver: ACK1, ACK2, ── (no ACK for 2)        
Sender timeout: retransmit 2, 3, 4, 5 (even though 3 arrived OK)
```

**GBN waste:** when error rates are high and W is large, GBN retransmits many correctly-received frames. This is its main weakness.

**Real-world use:** GBN is used in HDLC and was used in early TCP implementations.

## Selective Repeat (SR)

The receiver buffers out-of-order frames. Only lost or corrupted frames are retransmitted.

- Sender window: up to `W` outstanding frames.
- Receiver window: also `W` (it buffers received-but-not-yet-in-order frames).
- SR requires `W ≤ 2^(n-1)` to avoid ambiguity between old and new frames.

```
Window size W = 4, seq bits n = 3 (seq 0-7), max W = 4

Sender:   [0][1][2][3]
                  lost
Receiver: ACK0, ACK1, (buffer 3), (buffer 4)
Sender:   timeout on 2, retransmits only 2
Receiver: delivers 2, 3, 4 in order → sends ACK2, ACK3, ACK4
```

**SR efficiency** is higher than GBN under lossy conditions, but requires more receiver-side buffering.

## Protocol Comparison

| Property | Stop-and-Wait | Go-Back-N | Selective Repeat |
|----------|--------------|-----------|------------------|
| Sender window | 1 | W | W |
| Receiver window | 1 | 1 | W |
| On error: retransmit | 1 frame | W frames (all outstanding) | 1 frame only |
| Seq bits needed | 1 bit | n bits, W ≤ 2^n - 1 | n bits, W ≤ 2^(n-1) |
| Buffering at receiver | None | None | W frames |
| Complexity | Low | Medium | High |

## Sequence Number Arithmetic

Why does SR need `W ≤ 2^(n-1)` while GBN allows `W ≤ 2^n - 1`?

With GBN: since the receiver accepts only in-order frames, it can never confuse a new frame 0 with a retransmitted old frame 0 — the window can use almost all sequence numbers.

With SR: the receiver has a window of W. If W = 2^n (all sequence numbers used), a retransmitted frame 0 is indistinguishable from a new frame 0 when the receiver window has already advanced. Limiting W to `2^(n-1)` ensures old and new windows never overlap.

## TCP as a Sliding Window Protocol

TCP is a selective-repeat protocol with:
- Byte-stream sequence numbers (not frame numbers)
- Dynamic window sizes (negotiated via `rwnd` and capped by `cwnd`)
- Cumulative ACKs plus SACK options for selective retransmission
- Piggybacked ACKs in full-duplex data segments

Understanding Go-Back-N and Selective Repeat is essential for understanding why TCP behaves as it does during loss recovery — especially the difference between fast retransmit (SR-like, retransmit one segment) and the older Go-Back-N fallback behavior under certain loss patterns.

## Further Reading

- *An Introduction to Computer Networks* by Peter Lars Dordal (Chapter 11: Data Link): https://eng.libretexts.org/Bookshelves/Computer_Science/Networks/An_Introduction_to_Computer_Networks_(Dordal)
- *Computer Networking: A Top-Down Approach* by Kurose & Ross (Chapter 3, Transport Layer, covers sliding windows in the context of TCP): https://archive.org/details/computernetworki0000jame_y6m8
