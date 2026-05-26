# Entropy and Information Gain

A decision tree split divides `n` training examples (of which `n_pos` are positive) into two child nodes. The left child has `n_left` examples, of which `n_left_pos` are positive.

**Input** (one line, four space-separated integers):
```
n n_pos n_left n_left_pos
```

**Output** (five lines, each a decimal rounded to exactly 4 decimal places):
```
parent_entropy
left_entropy
right_entropy
weighted_child_entropy
information_gain
```

Where:
- `parent_entropy = H(n_pos, n - n_pos)`
- `left_entropy = H(n_left_pos, n_left - n_left_pos)`
- `right_entropy = H(n_right_pos, n_right - n_right_pos)` where `n_right = n - n_left`, `n_right_pos = n_pos - n_left_pos`
- `weighted_child_entropy = (n_left/n)*left_entropy + (n_right/n)*right_entropy`
- `information_gain = parent_entropy - weighted_child_entropy`
- Binary entropy: `H(pos, neg) = -(pos/total)*log2(pos/total) - (neg/total)*log2(neg/total)` where `total = pos + neg`. Return 0.0 if either count is 0 (pure node).

Use `math.log2` from the standard library.

**Example**

Input:
```
10 5 5 5
```

Output:
```
1.0000
0.0000
0.0000
0.0000
1.0000
```

Explanation: 10 examples, 5 positive. Left child gets all 5 positive (pure), right child gets all 5 negative (pure). Parent entropy = 1.0. Both children are pure (entropy = 0). Information gain = 1.0 (maximum).
