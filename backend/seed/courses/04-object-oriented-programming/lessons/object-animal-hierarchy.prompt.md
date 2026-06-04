# Animal Hierarchy with super()

## Problem Statement

Build a three-level class hierarchy. Each class's `__init__` **must** call `super().__init__()` to correctly chain initialization.

**Class definitions:**

- `Animal(name)` — stores `self.name`. `speak()` returns `"Some sound"`.
- `Dog(Animal)` — `__init__` calls `super().__init__(name)`. `speak()` returns `"Woof"`.
- `GuideDog(Dog)` — `__init__` calls `super().__init__(name)` and stores `self.owner`. `speak()` returns `"Woof woof"`. `__str__` returns `"<name> guides <owner>"`.

**Input format:**

Read lines from stdin until EOF. Each line is one of:

| Command | Action |
|---------|--------|
| `animal <name>` | Create an `Animal`; print `speak()` |
| `dog <name>` | Create a `Dog`; print `speak()` |
| `guidedog <name> <owner>` | Create a `GuideDog`; print `speak()`, then print `str(obj)` |

You may assume names and owners are single words with no spaces.

**Output format:**

- For `animal` and `dog`: print one line (the result of `speak()`).
- For `guidedog`: print two lines — first `speak()`, then `str(obj)`.

## Examples

**Example 1**

Input:
```
animal Cat
dog Rex
guidedog Buddy Alice
```

Output:
```
Some sound
Woof
Woof woof
Buddy guides Alice
```

**Example 2**

Input:
```
dog Lassie
guidedog Halo Bob
animal Parrot
```

Output:
```
Woof
Woof woof
Halo guides Bob
Some sound
```

**Example 3**

Input:
```
guidedog Max Eve
guidedog Luna Sam
```

Output:
```
Woof woof
Max guides Eve
Woof woof
Luna guides Sam
```

## Constraints

- Number of commands: 1 – 100
- Names and owners are non-empty single-word strings
