# Adversarial Search and Minimax

In single-agent search, you control all the moves. In **adversarial search**, an opponent is actively trying to defeat you. This changes everything: the quality of a position depends not just on what *you* can do, but on what your opponent will do *next*. Games like chess, Go, checkers, and Othello fit this model.

## The Two-Player Zero-Sum Model

A **zero-sum** game is one where every gain for one player is exactly a loss for the other. Poker chips, chess material, and Go territory all satisfy this. The combined "utility" is always constant.

We model the game as a **tree**:
- **MAX** node: our agent's turn — it wants to *maximize* the score.
- **MIN** node: the opponent's turn — it wants to *minimize* our score.
- **Terminal state**: game over. Has a **utility value** (e.g., +1 win, −1 loss, 0 draw).
- **Ply**: one player's turn. "Depth" in a game tree is measured in plies.

```
         MAX (our turn)
        /              \
      MIN              MIN   (opponent's turn)
     /   \            /   \
   +1    -1          0    +1   (terminal values)
```

From the MAX node, the best we can guarantee is the **maximum** of what MIN will leave us: max(min(+1,−1), min(0,+1)) = max(−1, 0) = **0**.

## The Minimax Algorithm

Minimax recursively evaluates the game tree:

```python
def minimax(state, is_max_turn):
    if terminal(state):
        return utility(state)
    if is_max_turn:
        return max(minimax(s, False) for s in successors(state))
    else:
        return min(minimax(s, True)  for s in successors(state))
```

The agent then picks the action leading to the child with the highest minimax value.

### Worked Numeric Example

A 2-level game tree (MAX moves, then MIN moves):

```
           MAX
         /  |  \
       MIN  MIN  MIN
      / \  / \   / \
     3   5 2  9  1   7
```

- Left MIN: min(3, 5) = 3
- Middle MIN: min(2, 9) = 2
- Right MIN: min(1, 7) = 1

MAX: max(3, 2, 1) = **3**. MAX should choose the left branch, guaranteeing a utility of 3 regardless of the opponent's response.

## Why Minimax Is Expensive

Time complexity: **O(b^m)** where `b` is the branching factor and `m` is the depth.

| Game | Branching factor b | Typical game depth m | b^m |
|---|---|---|---|
| Tic-tac-toe | 5 avg | 9 total | ~9! = 362,880 (feasible) |
| Chess | ~35 | ~100 half-moves | 35^100 ≈ 10^154 (infeasible) |
| Go | ~250 | ~150 moves | 250^150 ≈ 10^359 (infeasible) |

Solving chess by brute force is impossible. Two practical solutions exist.

## Alpha-Beta Pruning

Alpha-beta pruning cuts branches that **cannot affect the final decision**. It maintains two values:

- **α (alpha)**: the best value MAX has found so far (on any path to the root). MAX will never accept less than α.
- **β (beta)**: the best value MIN has found so far. MIN will never accept more than β.

**Prune condition**: if, at any node, α ≥ β, the current branch cannot influence the result and can be skipped.

### Step-by-Step Trace

```
           MAX
         /     \
       MIN       MIN
      /   \     /   \
     3     5   2     ?
```

- MAX starts: α = −∞, β = +∞.
- Explore left MIN (α=−∞, β=+∞):
  - See 3: β is updated to min(+∞, 3) = 3.
  - See 5: β remains 3 (5 > 3, MIN ignores it).
  - Left MIN returns 3.
- MAX sees 3: α = max(−∞, 3) = 3.
- Explore right MIN (α=3, β=+∞):
  - See 2: β = min(+∞, 2) = 2.
  - Now α=3 ≥ β=2 — **prune!** Skip the `?` node.
  - Right MIN would return at most 2, which MAX (α=3) would never prefer.

**Result**: α-β correctly returns 3 without evaluating the `?` node.

**Best-case improvement**: with perfect move ordering, alpha-beta reduces the effective branching factor from `b` to `√b`. For chess (b≈35): effective branching factor drops to ≈6, allowing roughly double the search depth for the same compute budget.

## Depth-Limited Search and Evaluation Functions

For complex games, even alpha-beta cannot search to terminal states. The solution:

1. Set a maximum search **depth** `d`.
2. Apply an **evaluation function** `eval(state)` at leaf nodes instead of the true utility.

Chess evaluation functions historically used:
- **Material count**: each piece has a point value (Queen=9, Rook=5, Bishop=3, Knight=3, Pawn=1). A simple sum is a rough proxy.
- **Mobility**: number of legal moves available (more moves = more flexibility).
- **King safety**: whether the king is behind a pawn shield, exposed, etc.
- **Pawn structure**: connected vs. isolated pawns, passed pawns.

Modern engines like Stockfish use **handcrafted evaluation + NNUE** (Efficiently Updatable Neural Networks) for a far stronger eval without full neural network inference cost.

## Monte Carlo Tree Search (MCTS)

MCTS, used by AlphaGo (2016), does not require an evaluation function. It estimates position value statistically through random *rollouts*:

**1. Select**: Starting from the root, follow the tree using a **UCB1 policy**:
```
UCB1(node) = Q(node)/N(node) + C * sqrt(ln(N(parent)) / N(node))
```
where Q = total reward, N = visit count, C = exploration constant (~√2). This balances exploitation (nodes with high win rate) against exploration (nodes visited few times).

**2. Expand**: When a non-fully-expanded node is reached, add one new child.

**3. Simulate (rollout)**: From the new node, play out a random game to a terminal state.

**4. Backpropagate**: Update Q and N counts for all nodes on the path to the root.

After many iterations (thousands to millions), the most-visited child of the root is the recommended move.

### Why MCTS Works

The random rollouts provide unbiased estimates of position value — if position X leads to a win 70% of the time in random play, it probably is a good position. The UCB1 formula ensures the algorithm explores promising regions more thoroughly.

**AlphaZero's improvement**: replace random rollouts with a neural network that *evaluates positions* and *suggests moves*. This makes the rollouts far more accurate. The network is trained from scratch using self-play, with no human domain knowledge.

## Key Takeaways

- Minimax is the foundational algorithm: MAX maximizes, MIN minimizes, alternating down the tree.
- **Worked numeric verification**: max(min(3,5), min(2,9), min(1,7)) = max(3,2,1) = 3.
- Alpha-beta pruning maintains α and β bounds and skips branches where α ≥ β, potentially halving the effective search depth cost.
- Real game engines use depth-limited search + evaluation functions because searching to terminal states is infeasible.
- MCTS + neural networks (AlphaZero, AlphaGo) replaced hand-crafted evaluation functions and achieved superhuman performance on Go, chess, and shogi.
