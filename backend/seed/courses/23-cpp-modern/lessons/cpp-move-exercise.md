# Exercise: Simulating Move Semantics — String Pool

In this exercise you will simulate the behavior of a simple **string pool** that tracks how many copies versus moves are made when building a collection of strings. This tests your understanding of when copies happen versus when moves happen.

You are given N strings on stdin. For each string:
- If the string starts with `MOVE:` prefix, count it as a move operation and store the rest.
- If the string starts with `COPY:` prefix, count it as a copy operation and store the rest.

Print the total number of moves, total number of copies, and the stored strings joined by spaces on one line, in the order received.
