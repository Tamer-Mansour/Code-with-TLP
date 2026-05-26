# Practice: Bounded Buffer Simulation

The **bounded buffer** (producer-consumer) problem is a classic synchronization scenario. A finite-capacity buffer holds items produced by producers and consumed by consumers. This exercise simulates the buffer sequentially to understand ordering and capacity constraints.

## What You'll Practice

Given a buffer capacity and a sequence of produce/consume operations, simulate the buffer and print all items that were successfully consumed in order.

## Rules

1. **Produce (P n):** Add item `n` to the back of the buffer. If the buffer is already at full capacity, the produce operation is **skipped** (the item is dropped).
2. **Consume (C):** Remove and record the front item. If the buffer is empty, the consume operation is **skipped** (nothing is recorded).
3. Operations are processed sequentially in the order given.

## Example

Buffer capacity = 2, operations: `P 10`, `P 20`, `P 30` (skip), `C`, `C`, `C` (skip)

```
P 10 → buffer: [10]        (size 1/2)
P 20 → buffer: [10, 20]    (size 2/2, full)
P 30 → SKIPPED             (buffer full)
C    → consume 10          (buffer: [20])
C    → consume 20          (buffer: [])
C    → SKIPPED             (buffer empty)

Output: 10 20
```

## Another Example

Buffer capacity = 3, operations: `C`, `P 5`, `P 6`, `C`, `C`

```
C    → SKIPPED  (empty)
P 5  → buffer: [5]
P 6  → buffer: [5, 6]
C    → consume 5
C    → consume 6

Output: 5 6
```

If no items were consumed at all, output `EMPTY`.
