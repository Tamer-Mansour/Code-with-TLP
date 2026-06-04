# Quiz: Recursion and Problem Solving

---

**Question 1.** What is the base case in recursion?

- [ ] The most complex input the function handles
- [x] A condition where the function returns without calling itself again
- [ ] The first line of the function
- [ ] The case where the input is 0

---

**Question 2.** What happens if you write a recursive function with no base case?

- [ ] It returns None automatically
- [ ] Python optimises it into a loop
- [x] It recurses until Python raises RecursionError (stack overflow)
- [ ] It returns 0

---

**Question 3.** What is the time complexity of the naive recursive Fibonacci implementation `fib(n) = fib(n-1) + fib(n-2)`?

- [ ] O(n)
- [ ] O(n log n)
- [ ] O(n²)
- [x] O(2^n)

---

**Question 4.** Which strategy does merge sort use?

- [ ] Greedy
- [ ] Dynamic programming
- [x] Divide and conquer
- [ ] Backtracking

---

**Question 5.** What is a call stack?

- [ ] A list of all variables in a program
- [x] A record of all active function calls, tracking where each function should return to
- [ ] The memory used to store the source code
- [ ] A queue of pending I/O operations

---

**Question 6.** Python's default recursion limit is approximately:

- [ ] 100
- [x] 1000
- [ ] 10000
- [ ] Unlimited

---

**Question 7.** The iterative Fibonacci runs in O(n) time. The naive recursive version runs in O(2^n). For n = 50, approximately how many more operations does the recursive version perform?

- [ ] 50 times more
- [ ] 2500 times more
- [x] Over 1 quadrillion times more (2^50 ≈ 10^15 vs 50)
- [ ] They are the same after Python optimises them

---

**Question 8.** When is recursion typically the BETTER choice over iteration?

- [ ] When memory is limited
- [ ] When the recursion depth can exceed 1000
- [x] When the problem has a naturally recursive structure, like traversing a tree
- [ ] When you need the fastest possible runtime
