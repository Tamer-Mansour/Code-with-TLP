# Detect Merge Conflicts

## Problem

When Git cannot automatically merge two branches, it inserts conflict markers into the file. Given text that may contain Git conflict marker blocks, count and report how many conflict blocks exist.

A conflict block:
- **Starts** with a line that begins with `<<<<<<<`
- **Ends** with a line that begins with `>>>>>>>`

Print the count as: `Conflicts: N`

## Input

Lines of text (a file possibly containing unresolved conflict markers). Input ends at EOF.

## Output

```
Conflicts: N
```

## Example

**Input:**
```
def greet():
<<<<<<< HEAD
    return 'Hello, world'
=======
    return 'Hi there'
>>>>>>> feature-branch

def farewell():
<<<<<<< HEAD
    return 'Goodbye'
=======
    return 'See you later'
>>>>>>> feature-branch
```

**Output:**
```
Conflicts: 2
```

## Constraints

- A conflict block always starts with `<<<<<<<` (7 angle brackets)
- Count only the opening markers (`<<<<<<<`) — one per conflict block
- Input may have 0 conflict blocks (output `Conflicts: 0`)
- At most 10,000 lines of input
