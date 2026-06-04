# Quiz: Graphs, Recursion & Divide-and-Conquer

**Q1. BFS and DFS both explore all vertices. Which one guarantees the shortest path in an unweighted graph?**
- [x] BFS — it explores vertices in non-decreasing order of distance from the source
- [ ] DFS — it reaches each vertex faster by going deep
- [ ] Both guarantee shortest paths
- [ ] Neither — you need Dijkstra's algorithm even for unweighted graphs

**Q2. In a directed graph, you run DFS and colour nodes white (unvisited), gray (on the current stack), and black (done). A cycle is detected when:**
- [ ] You encounter a black node
- [x] You encounter a gray node (a back edge to an ancestor on the current DFS path)
- [ ] Two different DFS trees share a vertex
- [ ] The number of edges equals the number of vertices

**Q3. Topological sort is only valid on:**
- [ ] Any directed graph
- [ ] Any undirected graph
- [x] Directed Acyclic Graphs (DAGs) — graphs with no directed cycles
- [ ] Complete graphs

**Q4. An adjacency list uses O(V + E) space. An adjacency matrix uses O(V²) space. When is the matrix preferable?**
- [ ] Always — constant-time edge checks are worth the memory
- [ ] For sparse graphs (E << V²) because memory is cheap
- [x] For dense graphs (E ≈ V²) or when you need O(1) edge existence checks (e.g., Floyd-Warshall)
- [ ] When vertices are labelled with strings rather than integers

**Q5. The Master Theorem applies to recurrences of the form T(n) = a·T(n/b) + f(n). What is the time complexity of merge sort T(n) = 2T(n/2) + O(n)?**
- [ ] O(n²) — two recursive calls times linear work
- [ ] O(n) — the two calls cancel out
- [x] O(n log n) — case 2 of the Master Theorem with a=2, b=2, c=1, f(n)=Θ(n^c)
- [ ] O(2^n) — exponential due to two branches

**Q6. Naive recursive Fibonacci fib(n) = fib(n-1) + fib(n-2) has which time complexity?**
- [ ] O(n) — linear recursion
- [ ] O(n log n) — similar to merge sort
- [x] O(2^n) — the recursion tree has exponential size because sub-problems are recomputed
- [ ] O(n²) — quadratic due to two sub-problems

**Q7. Which technique transforms the O(2^n) Fibonacci recursion to O(n)?**
- [ ] Tail recursion — Python optimises it away
- [ ] Divide-and-conquer — split input in half each time
- [x] Memoization — cache already-computed sub-problem results so each is solved only once
- [ ] Counting sort — non-comparison approach

**Q8. You want to count inversions in an array in O(n log n). The best approach is:**
- [ ] Compare every pair — O(n²) brute force
- [ ] Sort and compare positions — O(n log n) but complex
- [x] Augment merge sort: count cross-inversions during the merge step
- [ ] Use a max-heap to track relative order — O(n log n) but different
