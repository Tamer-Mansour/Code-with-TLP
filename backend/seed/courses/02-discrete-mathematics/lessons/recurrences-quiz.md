# Quiz: Recurrences and Growth

**Q1. What is the closed-form solution to T(n) = 3·T(n−1) with T(0) = 1?**
- [ ] T(n) = 3n
- [x] T(n) = 3^n
- [ ] T(n) = n·3
- [ ] T(n) = log₃(n)

**Q2. Using the Master Theorem on T(n) = 4·T(n/2) + n, what is the tight bound?**
- [ ] Θ(n)
- [ ] Θ(n log n)
- [x] Θ(n²)
- [ ] Θ(n² log n)

**Q3. Unrolling T(n) = T(n−1) + n with T(0) = 0 gives which closed form?**
- [ ] T(n) = n
- [ ] T(n) = 2^n
- [x] T(n) = n(n+1)/2
- [ ] T(n) = n log n

**Q4. The characteristic equation for F(n) = F(n−1) + F(n−2) is:**
- [ ] r − 1 = 0
- [ ] r^2 + r − 1 = 0
- [x] r^2 − r − 1 = 0
- [ ] r^2 − 2r + 1 = 0

**Q5. Tower of Hanoi satisfies T(n) = 2T(n−1) + 1 with T(0) = 0. What is T(n)?**
- [x] 2^n − 1
- [ ] n²
- [ ] n · 2^(n−1)
- [ ] 2^(n+1)

**Q6. Which of the following orderings from SLOWEST to FASTEST growing is correct?**
- [x] O(log n) < O(n) < O(n log n) < O(n²) < O(2^n)
- [ ] O(n) < O(log n) < O(n²) < O(2^n)
- [ ] O(1) < O(n) < O(log n) < O(n²)
- [ ] O(2^n) < O(n!) < O(n²)
