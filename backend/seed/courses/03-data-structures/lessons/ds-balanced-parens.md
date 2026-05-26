# Exercise: Balanced Parentheses

Use a stack to check whether every opening bracket is matched by the correct closing bracket in the right order.

## Algorithm

1. Iterate through each character.
2. If it is an opening bracket (`(`, `{`, `[`), push it onto the stack.
3. If it is a closing bracket, check that the stack is non-empty and that the top matches. If not, the string is unbalanced.
4. After processing all characters, the string is balanced only if the stack is empty.

```python
def is_balanced(s: str) -> bool:
    match = {')': '(', '}': '{', ']': '['}
    stack = []
    for ch in s:
        if ch in '({[':
            stack.append(ch)
        elif ch in ')}]':
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
    return len(stack) == 0
```
