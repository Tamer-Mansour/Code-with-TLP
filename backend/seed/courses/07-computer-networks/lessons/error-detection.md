# Error Detection in Networks

Physical communication channels are imperfect. Electromagnetic interference, signal attenuation, hardware faults, and cosmic ray bit flips can corrupt bits in transit. Networks at every layer use **error detection** (and sometimes **error correction**) schemes to identify and handle corrupted data. Understanding these mechanisms explains why checksums matter, why CRC is in Ethernet, and why TCP still checksums its segments even when running over reliable hardware.

## Types of Transmission Errors

- **Single-bit error**: exactly one bit flips (0→1 or 1→0). Common in memory; less common on modern links.
- **Burst error**: a sequence of consecutive bits are corrupted, e.g., lightning on a copper wire. The burst length is the distance from the first to last corrupted bit.
- **Erasure**: a symbol is lost entirely (more relevant in wireless coding theory).

Error rates:
- Modern fiber links: ~10⁻¹⁵ BER (Bit Error Rate) — one error per 1000 terabits.
- Wi-Fi: ~10⁻⁶ BER — one error per million bits.
- Copper CAT5e at 100 m: ~10⁻¹² BER.

## Parity Bits

The simplest error detection scheme: count the number of 1-bits and append a parity bit to make the total even (or odd).

### Even Parity (single-bit parity)

```
Data:     1 0 1 1 0 0 1   (three 1s — odd count)
Parity:   1               (append 1 to make four 1s — even)
Sent:     1 0 1 1 0 0 1 1

Received: 1 0 1 1 0 0 0 1 (one bit flipped!)
1-count:  three 1s — odd → error detected!
```

**Limitation**: detects only an *odd* number of bit flips. If 2 bits flip, the parity is unchanged — error goes undetected.

### Two-Dimensional Parity (2D Parity)

Arrange data bits in a grid. Compute one parity bit per row AND one per column:

```
Data grid (7 data bits across, 4 rows):
Row 0:  1 0 1 1 0 0 1 | parity = 0  (4 ones → even → 0)
Row 1:  0 1 1 0 1 1 0 | parity = 0
Row 2:  1 0 0 1 0 1 1 | parity = 0
Row 3:  0 1 0 1 1 0 1 | parity = 0
        -────────────
Col par:0 0 0 1 0 0 1  (column parities)
```

If a single bit flips, its row parity and column parity both fail → the *exact position* of the error is identified → it can be corrected by flipping that bit. 2D parity can **detect and correct single-bit errors** and detect all 2-bit errors.

## Internet Checksum (One's Complement Checksum)

Used in **IPv4 header**, **TCP**, and **UDP**. Optimized for fast software computation on 16-bit words.

### Algorithm (sender)

1. Treat the data as a sequence of 16-bit (2-byte) words.
2. Sum all words using **one's complement addition**: if the sum overflows 16 bits, add the carry back into the low 16 bits (wrap-around carry, called "end-around carry").
3. Take the one's complement of the result (flip all bits). This is the checksum.
4. Place the checksum in the header. If the data has an odd number of bytes, pad with a zero byte for checksum computation.

### Verification (receiver)

Sum all 16-bit words *including the checksum field*. If the result is `0xFFFF` (all ones), no error is detected. If not, discard the segment.

### Worked Example

Words: `0xB500`, `0x1700`

```
  0xB500
+ 0x1700
────────
  0xCC00   (no carry)
```

One's complement: `~0xCC00 = 0x33FF` → checksum is `0x33FF`

Verify: `0xB500 + 0x1700 + 0x33FF = 0xFFFF` ✓

### Worked Example with Carry

Words: `0xFFFF`, `0x0002`

```
  0xFFFF
+ 0x0002
────────
 0x10001  (17-bit result — carry!)
 carry:   add 0x0001 back
 result:  0x0002
```

One's complement: `~0x0002 = 0xFFFD` → checksum is `0xFFFD`

Verify: `0xFFFF + 0x0002 + 0xFFFD = 0x1FFFE` → end-around carry → `0xFFFF` ✓

**Limitation of the Internet checksum**: cannot detect all burst errors. If two 16-bit words are corrupted in a way that the errors cancel each other out (e.g., both gain and lose the same total), the checksum passes. Also, reordering of 16-bit words within the data goes undetected.

## CRC (Cyclic Redundancy Check)

CRC is a much stronger error detection scheme used in **Ethernet (CRC-32)**, **Wi-Fi**, **HDLC**, **USB**, and storage media. It is based on polynomial division over GF(2) (binary field, where addition is XOR).

### CRC Concept

The data bits are treated as the coefficients of a polynomial D(x). Both sender and receiver agree on a **generator polynomial** G(x). The sender appends r zeros to the data (where r = degree of G), then divides by G using XOR division. The remainder R(x) is the **FCS** (Frame Check Sequence), appended to the frame.

The receiver divides the received frame (data + FCS) by G. If the remainder is 0, no error was detected.

### CRC-32 Properties

CRC-32 uses the generator polynomial `G(x) = x³² + x²⁶ + x²³ + ... + 1` (hex: `0x04C11DB7`).

It guarantees detection of:
- All single-bit errors.
- All double-bit errors.
- All odd numbers of bit errors.
- All burst errors of length ≤ 32.
- Most burst errors of length > 32 (probability of missing one is 2⁻³²).

### Conceptual XOR Division Example (CRC-4)

Generator: `10011` (represents x⁴ + x + 1, so r=4)
Data: `110100`

```
Append 4 zeros → 1101000000
Divide by 10011:

1101000000
÷ 10011
──────────
 Step 1: 11010 ÷ 10011 = 1, remainder = 11010 XOR 10011 = 01001
 Step 2: 010010 ÷ 10011 = 1 when leading bit = 1…
 (full XOR long division — remainder = FCS)
```

In practice, CRC is computed via a lookup table or dedicated hardware shift registers — not by polynomial long division in software.

## Forward Error Correction (FEC)

Error **detection** requires retransmission when errors are found. For channels where retransmission is impractical (satellite, broadcast media, real-time audio), **FEC** adds redundant bits that allow the **receiver** to correct errors without retransmitting.

**Hamming codes**: Interleave parity bits at positions 1, 2, 4, 8, … Each parity bit covers a specific subset of data bits. A single-bit error causes the wrong subset of parities to fail, and their XOR points to the exact error position.

```
7-bit Hamming code for 4 data bits d1 d2 d3 d4:
Position: 1  2  3  4  5  6  7
Bits:     p1 p2 d1 p3 d2 d3 d4

p1 covers positions 1, 3, 5, 7
p2 covers positions 2, 3, 6, 7
p3 covers positions 4, 5, 6, 7
```

| FEC Code | Used in | Capability |
|----------|---------|------------|
| Hamming(7,4) | Memory ECC | Correct 1 bit, detect 2 |
| Reed-Solomon | CDs, DVDs, QR codes, DSL | Correct multiple symbol errors |
| LDPC | Wi-Fi (802.11n+), 4G/5G | Near Shannon capacity |
| Turbo codes | 3G cellular | High error rate recovery |
| Polar codes | 5G NR | Shannon-limit performance |

**Trade-off:** FEC adds overhead (redundant bits) and encoding/decoding latency, but eliminates retransmission. Best when RTT is large (satellite: 600 ms RTT) or retransmission is impossible (broadcast TV).

## Summary: Where Each Scheme Is Used

| Location | Scheme | Why |
|----------|--------|-----|
| Ethernet FCS | CRC-32 | Strong burst error detection on LAN |
| IP header | Internet Checksum | Fast 16-bit sum; header-only check |
| TCP/UDP | Internet Checksum | Catches corruption in segment + pseudo-header |
| Wi-Fi (802.11) | CRC-32 + CCMP | Error detection + encryption |
| USB | CRC-16, CRC-32 | Data integrity over short cable |
| SONET/SDH | CRC-16/32 | Fiber backbone framing |
| 4G LTE | Turbo + CRC | Wireless channel with FEC |
| 5G NR | LDPC + Polar | Approaching Shannon limit |
| Hard disk | Reed-Solomon + CRC | Correct sector-level errors |
| QR codes | Reed-Solomon | Readable even when 30% obscured |

Understanding these schemes helps you choose the right level of redundancy for your application — whether you need detection only (fast), correction (costly but no retransmit), or both.
