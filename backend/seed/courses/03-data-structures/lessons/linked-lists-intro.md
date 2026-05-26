# Linked Lists

A **linked list** is a sequence of nodes where each node stores a value and a reference (pointer) to the next node. Unlike arrays, nodes are scattered throughout memory — there is no contiguous allocation and no index arithmetic. The structure is built entirely from pointer chains.

## Node Structure

```python
class Node:
    def __init__(self, val: int):
        self.val = val
        self.next = None   # reference to next Node, or None at the tail
```

A **singly linked list** has one pointer per node (forward only). A **doubly linked list** has two pointers per node (`next` and `prev`), enabling O(1) backward traversal and O(1) deletion of a known node.

```
Singly:   head → [1|→] → [2|→] → [3|∅]

Doubly:   ∅ ← [∅|1|→] ⇄ [←|2|→] ⇄ [←|3|∅] ← tail
```

Each box represents `[prev | val | next]`. On 64-bit systems each pointer occupies 8 bytes, so a doubly-linked node with a 4-byte integer value uses ~20 bytes of object overhead plus 16 bytes of pointers — far more than 4 bytes in a flat array.

## Core Operations with Step-by-Step Walkthroughs

### Traversal — O(n)

Walk the chain from `head` until `node.next is None`:

```python
def print_list(head: Node) -> None:
    cur = head
    while cur:
        print(cur.val, end=" → ")
        cur = cur.next
    print("None")
```

### Insertion at the Front — O(1)

No traversal needed — just rewire two pointers:

```
Before:  head → [20] → [30] → None
Insert 10 at front:
  1. new_node.next = head   →  [10] → [20] → [30] → None
  2. head = new_node         ←  head
```

```python
def prepend(head: Node, val: int) -> Node:
    new_node = Node(val)
    new_node.next = head
    return new_node   # caller must update head
```

### Insertion after a Known Node — O(1)

```
Before:  ... → [A] → [C] → ...
Insert B after A:
  1. B.next = A.next   →  [B] → [C]
  2. A.next = B        →  [A] → [B] → [C]
```

The order matters: step 1 must happen before step 2, or you lose the reference to `C`.

```python
def insert_after(node: Node, val: int) -> None:
    new_node = Node(val)
    new_node.next = node.next   # MUST come first
    node.next = new_node
```

### Insertion at the Tail — O(n) singly / O(1) with tail pointer

Without a tail pointer, you must traverse to the last node (O(n)). Maintaining a separate `tail` reference makes append O(1):

```python
class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, val: int) -> None:
        node = Node(val)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1
```

### Deletion by Value — O(n)

You must traverse to find the node *before* the target. The **dummy head** pattern eliminates the special case of deleting the first real node:

```python
def delete_val(head: Node, val: int) -> Node:
    dummy = Node(0)
    dummy.next = head
    prev = dummy
    cur = head
    while cur:
        if cur.val == val:
            prev.next = cur.next   # bypass cur
            break
        prev = cur
        cur = cur.next
    return dummy.next   # new head (unchanged unless first node was deleted)
```

### Deletion of a Known Node in a Doubly Linked List — O(1)

With `prev` pointers, you can remove a node without traversing from the head:

```python
def delete_node_doubly(node):
    """Remove `node` from a doubly linked list in O(1)."""
    if node.prev:
        node.prev.next = node.next
    if node.next:
        node.next.prev = node.prev
```

### Reversing a Singly Linked List — O(n), O(1) Space

Classic three-pointer iterative reversal:

```
Before:  None ← head  [1] → [2] → [3] → None

Step 1:  prev=None, cur=1
         save nxt=2, set 1.next=None, prev=1, cur=2

Step 2:  prev=1, cur=2
         save nxt=3, set 2.next=1, prev=2, cur=3

Step 3:  prev=2, cur=3
         save nxt=None, set 3.next=2, prev=3, cur=None → done

After:   head → [3] → [2] → [1] → None
```

```python
def reverse(head: Node) -> Node:
    prev = None
    cur = head
    while cur:
        nxt = cur.next    # save forward reference
        cur.next = prev   # reverse the pointer
        prev = cur        # advance prev
        cur = nxt         # advance cur
    return prev           # prev is now the new head
```

## Sentinel (Dummy) Node Pattern

A **dummy head node** (value irrelevant) prepended before the real first element eliminates edge-case logic for the head:

```python
dummy = Node(0)
dummy.next = head
# ... all operations use dummy as the starting point ...
return dummy.next   # the real head
```

Use this in problems involving: insertion-before-head, deletion of the first node, merging two lists, and reordering.

## Detecting a Cycle — Floyd's Algorithm — O(n), O(1) Space

A linked list has a cycle if some node's `next` points back to an earlier node. The **fast/slow pointer** (tortoise-and-hare) algorithm detects cycles without extra memory:

```python
def has_cycle(head: Node) -> bool:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

The fast pointer gains one step per iteration. If a cycle exists, fast eventually laps slow and they meet inside the cycle. If no cycle, fast reaches `None`.

## Finding the Middle of a List — O(n)

```python
def find_middle(head: Node) -> Node:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # for even-length, returns the second middle node
```

## Singly vs. Doubly: When to Choose Which

| Feature                   | Singly                  | Doubly                   |
|---------------------------|-------------------------|--------------------------|
| Memory per node (64-bit)  | val + 8 bytes (1 ptr)   | val + 16 bytes (2 ptrs)  |
| Insert at front           | O(1)                    | O(1)                     |
| Insert at back            | O(n) or O(1) w/ tail    | O(1) w/ tail ptr         |
| Delete head node          | O(1)                    | O(1)                     |
| Delete tail node          | O(n)                    | O(1) w/ tail ptr         |
| Delete arbitrary node     | O(n) — need predecessor | O(1) — use prev pointer  |
| Reverse traversal         | Not possible            | O(n)                     |
| Cache performance         | Slightly better         | Slightly worse           |

**Use singly linked list** for stacks, simple queues, and adjacency lists where you only need forward traversal.  
**Use doubly linked list** for deques, LRU caches (need O(1) delete from middle), and browser history (back/forward navigation).

## Complexity Summary

| Operation                  | Singly LL       | Doubly LL      |
|----------------------------|-----------------|----------------|
| Access by index k          | O(n)            | O(n)           |
| Insert at head             | O(1)            | O(1)           |
| Insert at tail (w/ tail ptr)| O(1)           | O(1)           |
| Insert after known node    | O(1)            | O(1)           |
| Delete head                | O(1)            | O(1)           |
| Delete tail                | O(n)            | O(1)           |
| Delete by value            | O(n)            | O(n)           |
| Delete known node          | O(n)†           | O(1)           |
| Search                     | O(n)            | O(n)           |
| Reverse                    | O(n)            | O(n)           |
| Detect cycle               | O(n), O(1) space| O(n), O(1)     |

†Singly requires traversal from head to find the predecessor.

## Common Bugs

1. **Lost reference:** Always save `cur.next` before rewiring `cur.next = prev`.
2. **Forgetting to return the new head** after operations that may change it.
3. **Off-by-one in fast pointer:** `while fast and fast.next` — both checks required to prevent `AttributeError` when `fast.next` is `None`.
4. **Forgetting the tail pointer update** when implementing an append.
