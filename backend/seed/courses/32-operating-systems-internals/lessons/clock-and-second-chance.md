# Clock and Second-Chance Algorithms

The **clock algorithm** (also called **second-chance**) is the most widely deployed page replacement algorithm in real operating systems. It approximates LRU using only the hardware reference bit, with very low overhead.

## The Second-Chance Idea

When a page is selected as a victim (e.g., by FIFO order), check its **reference bit**:

- If the reference bit is **0** — the page has not been used recently. Evict it.
- If the reference bit is **1** — give the page a "second chance": clear its bit to 0, skip it, and move on to the next candidate.

A page that keeps getting accessed will keep having its bit set to 1 before the clock hand reaches it again, and will survive indefinitely. A page that has not been touched since its last reprieve will be evicted on the next pass.

## The Clock Hand

Instead of a literal queue, arrange all frames in a circular buffer and maintain a **clock hand** (pointer) that sweeps around the circle:

```
         [ page 3 | ref=0 ]
        /                   \
[ page 7 | ref=1 ]     [ page 1 | ref=0 ]
        \                   /
         [ page 5 | ref=1 ]
              ↑
           clock hand
```

On a page fault:
1. Inspect the frame under the clock hand.
2. If `ref == 0`: evict this page, load the new page here, advance the hand.
3. If `ref == 1`: clear `ref` to 0, advance the hand, go to step 1.

In the worst case (all bits = 1), the clock makes a full revolution and the hand returns to its starting point, which now has `ref = 0` after being cleared — effectively degenerating to FIFO for that round.

## Worked Example

Frames: 4, initial state after loading pages A, B, C, D (all ref=1 from recent use).  
Clock hand starts at frame 0. Page fault for page E:

```
Pass 1:
  Frame 0: page A, ref=1 → clear to 0, advance
  Frame 1: page B, ref=1 → clear to 0, advance
  Frame 2: page C, ref=1 → clear to 0, advance
  Frame 3: page D, ref=1 → clear to 0, advance
Pass 2 (hand wraps around):
  Frame 0: page A, ref=0 → EVICT, load E here, advance hand to frame 1
```

## Enhanced Clock (NRU — Not Recently Used)

Extend the second-chance idea by also considering the **dirty bit** (modified bit `M`). Each page now has two bits: `(R, M)`.

Priority for eviction (lower is better):

| Class | R | M | Meaning | Evict preference |
|---|---|---|---|---|
| 0 | 0 | 0 | Not referenced, not modified | Best victim |
| 1 | 0 | 1 | Not referenced, but dirty | OK (write-back needed) |
| 2 | 1 | 0 | Referenced, not dirty | Prefer to keep |
| 3 | 1 | 1 | Referenced and dirty | Last resort |

The clock makes up to four passes, evicting the first page found in the lowest class. Most OSes (including early macOS/classic Mac OS, BSD, and Linux's variant) use a form of this.

## Linux: The Two-List Clock Variant

Linux maintains two LRU lists per zone:
- **Active list**: recently accessed pages (R=1 recently)
- **Inactive list**: candidates for eviction

Pages promoted to active when accessed; demoted to inactive when the active list grows too large. The clock sweeps the inactive list. This two-list scheme resists **scan resistance** issues where a large sequential read would flood the single list and evict hot working-set pages.

## Clock vs. LRU

| Property | Clock | True LRU |
|---|---|---|
| Approximation quality | Good | Exact |
| Hardware requirement | Reference bit only | Reference bit + timestamps or ordering |
| Implementation cost | O(1) amortized per fault | O(1) with doubly linked list |
| Belady's anomaly | No (stack algorithm approx.) | No |
| Used in real OSes? | Yes (widely) | Rarely (too expensive) |

## Common Pitfall

Students confuse "second chance" with resetting a page's age entirely. Clearing the reference bit does not make the page "new" — it just delays eviction by one clock revolution. If the page is not accessed again before the hand returns, it will be evicted next time.

```c
// Simplified clock victim selection
int clock_hand = 0;

int select_victim(Frame frames[], int n_frames) {
    while (1) {
        if (frames[clock_hand].ref == 0) {
            int victim = clock_hand;
            clock_hand = (clock_hand + 1) % n_frames;
            return victim;
        }
        frames[clock_hand].ref = 0;   // give second chance
        clock_hand = (clock_hand + 1) % n_frames;
    }
}
```

> **Interview answer:** The clock algorithm arranges frames in a circle and uses a sweeping hand. Pages with a reference bit of 1 get a second chance (the bit is cleared); pages with a reference bit of 0 are evicted. It approximates LRU with very low overhead and is the basis of most real OS page replacement implementations.
