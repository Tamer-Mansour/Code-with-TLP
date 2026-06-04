# Quiz: Linked Lists

**Q1. What is the time complexity of inserting a node at the head of a singly linked list?**
- [ ] O(n) — must traverse to find the position
- [x] O(1) — update the head pointer and the new node's next pointer
- [ ] O(log n) — binary search for the insertion point
- [ ] O(n²) — shifting elements to make room

**Q2. What is the time complexity of accessing the k-th element in a singly linked list?**
- [ ] O(1) — index arithmetic like an array
- [ ] O(log n) — binary search
- [x] O(n) — must traverse from the head through k nodes
- [ ] O(k log k) — depends on value of k

**Q3. Which of the following is an advantage of a linked list over a dynamic array?**
- [ ] O(1) random access by index
- [ ] Better cache locality (contiguous memory)
- [x] O(1) insertion and deletion at a known node position without shifting
- [ ] Less memory per element (no pointer overhead)

**Q4. To detect a cycle in a singly linked list in O(n) time and O(1) space, you should use:**
- [ ] A hash set to record visited nodes — O(n) space
- [x] Floyd's two-pointer (slow/fast runner) algorithm
- [ ] Recursive DFS — O(n) stack space
- [ ] Sort the node addresses and check for duplicates

**Q5. A doubly linked list stores an extra pointer per node compared to a singly linked list. What operation does this enable in O(1) that a singly linked list cannot do?**
- [ ] Finding the head node
- [ ] Searching for a value
- [x] Deleting a node given only a pointer to that node (without needing its predecessor)
- [ ] Appending to the tail

**Q6. In the two-pointer "runner technique", what can you find if the fast pointer moves twice as fast as the slow pointer?**
- [ ] The node with the maximum value
- [ ] The node at index n/2 from the tail
- [x] The middle node (slow pointer is at the midpoint when fast pointer reaches the end)
- [ ] Whether the list has an even or odd number of elements

**Q7. You need to reverse a singly linked list in-place. What is the minimum number of pointer variables required (beyond the list nodes themselves)?**
- [ ] 0 — just swap values
- [x] 3 — prev, curr, and next_node
- [ ] n — store all nodes in an array first
- [ ] 2 — only head and tail pointers

**Q8. Inserting 1 million elements at the front of a Python list (`list.insert(0, x)`) is O(n²) total. Which data structure provides O(1) amortised front insertion?**
- [ ] numpy array
- [x] collections.deque
- [ ] set
- [ ] dict
