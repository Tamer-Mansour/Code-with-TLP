# Quiz: Problem Solving & Search

**Q1. Which data structure does Breadth-First Search use for its frontier, and why?**
- [x] A FIFO queue, so that shallower nodes are always explored before deeper ones.
- [ ] A LIFO stack, so that the deepest path is always followed first.
- [ ] A min-heap, so that the lowest-cost node is always explored first.
- [ ] A hash set, so that duplicate states are automatically deduplicated.

**Q2. Why is BFS optimal when all step costs are equal?**
- [ ] It uses less memory than DFS and therefore avoids costly re-expansions.
- [x] It explores all paths of length d before any path of length d+1, so the first goal found has the minimum number of steps.
- [ ] It uses a heuristic to prefer nodes that are closer to the goal.
- [ ] It backtracks immediately whenever it reaches a dead end.

**Q3. An admissible heuristic is one that:**
- [ ] Always finds the goal in O(n) time regardless of the graph structure.
- [ ] Overestimates cost to guarantee safety margins in planning.
- [x] Never overestimates the true cost to reach the goal from the current state.
- [ ] Is consistent but not necessarily accurate enough to improve on BFS.

**Q4. In A* search, f(n) = g(n) + h(n). What do g(n) and h(n) represent?**
- [ ] g(n) is the heuristic estimate; h(n) is the number of nodes expanded so far.
- [ ] g(n) is the branching factor; h(n) is the depth of node n.
- [x] g(n) is the actual cost from the start to node n; h(n) is the estimated cost from n to the goal.
- [ ] g(n) is the goal test result; h(n) is the number of actions remaining.

**Q5. Alpha-beta pruning improves minimax by:**
- [ ] Adding a neural network evaluation function at every internal node.
- [ ] Reducing the game tree to a single best-move path from the start.
- [x] Skipping branches that cannot influence the final decision because a better option already exists for the current player.
- [ ] Converting tree search into graph search to avoid revisiting states.

**Q6. A* finds an optimal path when:**
- [ ] The heuristic is as large as possible, pushing nodes toward the goal aggressively.
- [ ] DFS has already fully explored the search tree to find terminal states.
- [ ] The graph contains no cycles, preventing infinite loops.
- [x] The heuristic is admissible — it never overestimates the true cost to the goal.
