# Exercise: BST Insert and In-Order Traversal

Insert values into a BST and perform an in-order traversal to produce sorted output.

## Key Insight

In-order traversal (Left, Root, Right) of a valid BST always yields values in ascending order. This makes BST in-order traversal equivalent to a comparison-based sort.

## Iterative In-Order (bonus approach)

```python
def inorder_iterative(root):
    result, stack, cur = [], [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        result.append(cur.val)
        cur = cur.right
    return result
```
