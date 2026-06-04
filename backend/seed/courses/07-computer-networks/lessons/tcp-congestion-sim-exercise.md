# Exercise: TCP Congestion Window Simulator

TCP Reno congestion control passes through two distinct phases as it probes for available bandwidth: **Slow Start** (exponential growth) and **Congestion Avoidance** (linear growth). A loss event resets behavior based on severity.

This exercise simulates TCP Reno round by round, printing the congestion window and phase at the start of each round before applying the round's event.

## TCP Reno Rules

### Slow Start
- Starts when `cwnd < ssthresh`.
- Each round without loss: `cwnd` doubles (`cwnd *= 2`).
- Transitions to Congestion Avoidance as soon as `cwnd >= ssthresh`.

### Congestion Avoidance
- Active when `cwnd >= ssthresh`.
- Each round without loss: `cwnd += 1`.

### Timeout / LOSS event
- `ssthresh = max(cwnd // 2, 1)`
- `cwnd = 1`
- Returns to Slow Start immediately.

### Phase determination
The phase printed for a round is based on the values of `cwnd` and `ssthresh` **at the start of that round**, before any event is applied.

## Significance

Understanding this simulator helps you internalize why TCP throughput follows a sawtooth pattern and why high-latency links (satellite, intercontinental WAN) need algorithms like TCP CUBIC or BBR to fill the available bandwidth efficiently.

## Further Reading

- *TCP Congestion Control* — RFC 5681: https://datatracker.ietf.org/doc/html/rfc5681
- *Computer Networking: A Top-Down Approach* by Kurose & Ross, Chapter 3.7:
  https://archive.org/details/computernetworki0000jame_y6m8
- *An Introduction to Computer Networks* by Dordal, Chapter 19 (TCP Congestion Control):
  https://eng.libretexts.org/Bookshelves/Computer_Science/Networks/An_Introduction_to_Computer_Networks_(Dordal)
