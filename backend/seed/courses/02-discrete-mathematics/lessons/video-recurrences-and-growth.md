# Video: Recurrences and Asymptotic Growth

This video explains how to express the running time of recursive algorithms as recurrence relations, solve them using telescoping, characteristic roots, and the Master Theorem, and then describe the solution using Big-O, Big-Ω, and Big-Θ notation.

**Key takeaways:**

- A recurrence T(n) = aT(n/b) + f(n) models divide-and-conquer algorithms; the Master Theorem gives closed-form solutions for three cases based on how f(n) compares to n^(log_b a).
- Merge sort satisfies T(n) = 2T(n/2) + O(n) → T(n) = O(n log n) (Master Theorem case 2).
- Binary search satisfies T(n) = T(n/2) + O(1) → T(n) = O(log n) (case 2 with a=1, b=2).
- The Fibonacci recurrence F(n) = F(n-1) + F(n-2) has characteristic roots (1±√5)/2 giving F(n) = Θ(φ^n) where φ ≈ 1.618 (golden ratio).
- Big-O, Big-Ω, and Big-Θ: O is an upper bound, Ω is a lower bound, Θ is a tight bound. O(n log n) does NOT mean Θ(n log n).

The video closes with a hierarchy of common complexity classes — O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2^n) — and guidance on which to prefer for large inputs.
