# State Spaces and the Language of Search

Many AI problems — route planning, puzzle solving, game playing, robot motion — can be described as searching through a **state space**. Mastering this framework gives you a unified vocabulary for an enormous family of algorithms, from classic BFS to modern planning systems.

## Core Definitions

| Term | Meaning | Example (8-puzzle) |
|---|---|---|
| **State** | A complete description of the world at one moment | Current tile arrangement |
| **Initial state** | Where the agent starts | Scrambled puzzle |
| **Goal test** | Returns true when the goal is reached | Tiles in order 1–8 |
| **Actions** | The moves available from a given state | Slide a tile into the blank |
| **Transition model** | New state produced by applying an action | Tile slides left |
| **Step cost** | Cost of a single action | 1 (each slide costs 1 move) |
| **Path cost** | Accumulated cost of a sequence of actions | Total number of slides |

Together, these six pieces define a **search problem**. The *solution* is a **path** — a sequence of actions — from the initial state to a goal state. An **optimal solution** has the lowest path cost.

## A Concrete Example: The 8-Puzzle

The 8-puzzle has tiles numbered 1–8 and one blank on a 3×3 grid. A move slides an adjacent tile into the blank.

```
Initial:        Goal:
2 8 3           1 2 3
1 6 4     →     4 5 6
7 _ 5           7 8 _
```

- **State space size**: 9! / 2 = 181,440 reachable configurations (exactly half the 9! = 362,880 permutations are reachable from any starting position, due to parity constraints).
- **Branching factor**: 2–4 (blank can slide in 2–4 directions depending on position).
- **Solution depth**: typically 20–30 moves for a random start.

Even this tiny toy problem illustrates why naive search fails: a 30-move solution means the search tree has up to 4^30 ≈ 10^18 nodes at the deepest level. We need smarter strategies.

## A Second Example: Route Planning

Represent cities as **nodes** and roads as **edges** with distances as step costs.

```
         A
        / \
      5/   \3
      /     \
     B       C
      \     /
      2\   /4
        \ /
         D
```

- **States**: each city (A, B, C, D).
- **Initial state**: city A.
- **Goal test**: have we reached city D?
- **Actions**: travel along any road from the current city.
- **Step cost**: road distance.

The optimal path from A to D is A→C→D with total cost 3+4=7, versus A→B→D with cost 5+2=7 (a tie here). On a real road map with millions of cities, finding this efficiently is exactly what GPS navigation does.

## Graph vs. Tree Search

When you expand states by applying actions, you build a **search tree** rooted at the initial state. The same *state* can appear as multiple *nodes* on different branches — for example, in route planning, you might reach city C via A→C and also via A→B→...→C.

- **Tree search**: expands every node without checking if it was seen before. Can loop infinitely in cyclic graphs.
- **Graph search**: maintains a **visited/explored set** to avoid re-expanding states. Essential for most real problems.

The explored set adds memory cost but prevents exponential blowup from repeated states.

## The State Space Graph

The full state space is a **directed graph** where:
- Nodes = states
- Edges = actions (with costs as edge weights)
- Search = finding a path from the start node to any goal node

For the 8-puzzle this graph has 181,440 nodes. For Go, it has approximately 10^170 nodes — completely infeasible to store. For real-world robotics, the state is a continuous configuration space with infinitely many points.

This is why the choice of search *algorithm* matters enormously.

## Uninformed vs. Informed Search

**Uninformed (blind) search** — no knowledge about how close a state is to the goal. The algorithm treats all unexplored states equally. Examples: BFS, DFS, Uniform-Cost Search.

**Informed (heuristic) search** — uses problem-specific knowledge to prefer promising states. A **heuristic function** `h(n)` estimates the cost from state `n` to the nearest goal. Examples: Greedy best-first, A*.

## Measuring Algorithm Quality

Four properties matter:

| Property | Meaning |
|---|---|
| **Complete** | Guaranteed to find a solution if one exists |
| **Optimal** | Guaranteed to find the least-cost solution |
| **Time complexity** | How many nodes are expanded (function of `b` and `d`) |
| **Space complexity** | How many nodes are stored simultaneously |

Where `b` = branching factor (average children per node) and `d` = depth of shallowest goal.

These properties trade off against each other. BFS is complete and optimal (for unit costs) but uses exponential memory. DFS uses linear memory but is neither complete nor optimal.

## Path Cost and Optimality: A Worked Example

Consider the route graph above. Starting at A, two paths reach D:
- A → C → D: cost 3 + 4 = **7**
- A → B → D: cost 5 + 2 = **7**

Both are optimal. If we instead have costs: A→C = 3, C→D = 6, A→B = 2, B→D = 3, then:
- A → C → D: cost 9
- A → B → D: cost 5 ← optimal

An algorithm that only measures *path length* (number of edges) would say both 2-edge paths are equal and might return the non-optimal solution. An algorithm that tracks *path cost* (sum of edge weights) correctly identifies A→B→D.

## Why Search Matters for Modern AI

Classical search is not just historical — it underlies:
- **GPS navigation**: Dijkstra/A* on road graphs with millions of edges.
- **Game AI**: minimax + alpha-beta search for chess, checkers, shogi.
- **Robot motion planning**: rapidly-exploring random trees (RRT) in configuration space.
- **Automated theorem proving**: proof search in formal logic.
- **AI planning systems**: used in logistics, scheduling, and space mission design.
- **AlphaGo/AlphaZero**: Monte Carlo Tree Search + neural network evaluation.

Modern ML has automated parts of these (learning heuristics from data, learning evaluation functions), but the underlying framework — states, transitions, costs — persists. Understanding it makes every advanced technique clearer.
