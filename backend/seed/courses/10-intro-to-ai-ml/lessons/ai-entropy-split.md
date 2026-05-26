# Exercise: Entropy and Information Gain

Understanding how decision trees choose splits requires computing entropy and information gain by hand. In this exercise you will implement these calculations from scratch using only the Python standard library.

## Background

**Entropy** measures the impurity (disorder) of a set. For a binary classification problem:

```
H(S) = -p_pos * log2(p_pos) - p_neg * log2(p_neg)
```

H = 0 for a perfectly pure set (all one class). H = 1 for a perfectly mixed set (50/50 split).

**Information gain** of a split is the reduction in entropy:

```
IG = H(parent) - (n_left/n)*H(left) - (n_right/n)*H(right)
```

where `n` = total examples, `n_left` and `n_right` = examples in each child.

## Task

Read a description of one binary split, compute the five values listed below, and print each on its own line rounded to **4 decimal places**.
