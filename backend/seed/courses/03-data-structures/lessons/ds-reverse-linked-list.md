# Exercise: Reverse a Linked List

Implement a singly linked list from node values read from stdin, reverse it using the iterative three-pointer technique, then print the result.

## Classic Iterative Approach

The iterative reversal uses three pointers: `prev`, `cur`, and `nxt`.

```python
prev = None
cur = head
while cur:
    nxt = cur.next
    cur.next = prev
    prev = cur
    cur = nxt
return prev   # new head
```

At each step you redirect `cur.next` to point backward, then advance all three pointers.
