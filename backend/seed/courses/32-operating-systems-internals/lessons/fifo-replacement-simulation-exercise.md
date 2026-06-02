# Exercise: Simulate FIFO Page Replacement and Count Faults

In this exercise you will implement the **FIFO (First-In, First-Out)** page replacement algorithm and count the total number of page faults for a given reference string and frame count.

## What You Will Implement

You are given:
- A number of frames `f` (the physical memory capacity in pages).
- A reference string of page numbers.

Your program must simulate FIFO page replacement — maintaining a queue of pages in the order they were first loaded — and output the total number of page faults.

A **page fault** occurs whenever the referenced page is not currently in any frame. On a fault:
1. If a free frame exists, load the page there.
2. Otherwise, evict the page that has been in memory the longest (the front of the FIFO queue) and load the new page.

Accessing a page already in memory is a **hit** and does not count as a fault.

## Skills Practiced

- Queue data structure (FIFO discipline)
- Set-based membership testing for O(1) hit detection
- Handling edge cases: duplicate consecutive references, first-load phase

## Getting Started

Read the number of frames, then the space-separated reference string from stdin. Print a single integer — the total page fault count — to stdout.

Implement `fifo_page_faults(frames, pages)` first, then wire it to stdin/stdout. Test your solution against the sample cases before submitting.

## Sample Trace (3 frames)

```
Reference: 1 2 3 4 1 2 5 1 2 3 4 5
Frames:    3

Step  Queue (oldest→newest)  Fault?
  1   [1]                    YES
  2   [1,2]                  YES
  3   [1,2,3]                YES
  4   [2,3,4]  evict 1       YES
  5   [3,4,1]  evict 2       YES
  6   [4,1,2]  evict 3       YES
  7   [1,2,5]  evict 4       YES
  8   [1,2,5]  hit 1         NO
  9   [1,2,5]  hit 2         NO
 10   [2,5,3]  evict 1       YES
 11   [5,3,4]  evict 2       YES
 12   [5,3,4]  hit 5         NO

Total faults: 9
```
