# Contracts, Protocols, and Interface Design

Good interface design answers a simple question: *What does the caller need to know, and what can stay hidden?* This lesson looks at design principles for building clean, stable interfaces, and at the formal notion of "contracts" between a class and its callers.

## What is an Interface?

An interface is the public-facing portion of a class: the methods and properties that callers use. The implementation — internal data structures, algorithms, caching — is hidden behind the interface.

A well-designed interface has three properties:

1. **Minimal** — it exposes only what callers need.
2. **Stable** — its names and signatures change as rarely as possible.
3. **Self-describing** — names, types, and docstrings communicate intent without requiring callers to read the implementation.

## Design by Contract

A **contract** formalises the agreement between a method and its callers using three concepts:

| Part | Description | Python mechanism |
|------|-------------|-----------------|
| **Precondition** | What must be true when the method is called | Validate in the method body; raise `ValueError`/`TypeError` |
| **Postcondition** | What will be true when the method returns | Document; add `assert` in debug mode |
| **Invariant** | What must always be true about the object | Enforce in setters / properties |

```python
class Queue:
    """
    A FIFO queue.
    Invariant: size >= 0 at all times.
    """

    def __init__(self, max_size: int = None):
        if max_size is not None and max_size <= 0:
            raise ValueError("max_size must be positive or None")
        self._items: list = []
        self._max  = max_size

    def enqueue(self, item) -> None:
        """
        Precondition:  item is not None; queue is not full (if bounded).
        Postcondition: size increases by 1; item is at the back of the queue.
        """
        if item is None:
            raise TypeError("Cannot enqueue None")
        if self._max is not None and len(self._items) >= self._max:
            raise OverflowError(f"Queue is full (max {self._max})")
        self._items.append(item)

    def dequeue(self):
        """
        Precondition:  queue is not empty.
        Postcondition: oldest item removed; size decreases by 1.
        Raises: IndexError if queue is empty.
        """
        if not self._items:
            raise IndexError("dequeue from empty Queue")
        return self._items.pop(0)

    def peek(self):
        """Return the front item without removing it. Raises IndexError if empty."""
        if not self._items:
            raise IndexError("peek at empty Queue")
        return self._items[0]

    @property
    def size(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __repr__(self) -> str:
        return f"Queue({self._items!r})"
```

```python
q = Queue(max_size=3)
q.enqueue("a")
q.enqueue("b")
q.enqueue("c")
print(q.peek())       # a
print(q.dequeue())    # a
print(q.size)         # 2
q.enqueue("d")
q.enqueue("e")        # OverflowError: Queue is full (max 3)
```

## The Interface Segregation Principle (Preview)

Fat interfaces — those with too many unrelated methods — force implementers to define methods they don't actually need. Prefer small, focused interfaces:

```python
from abc import ABC, abstractmethod

# Too fat — not every reader is also a writer
class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> str: ...
    @abstractmethod
    def write(self, key: str, value: str) -> None: ...
    @abstractmethod
    def delete(self, key: str) -> None: ...

# Better — segregated by capability
class Readable(ABC):
    @abstractmethod
    def read(self, key: str) -> str: ...

class Writable(ABC):
    @abstractmethod
    def write(self, key: str, value: str) -> None: ...
    @abstractmethod
    def delete(self, key: str) -> None: ...

class ReadWriteStorage(Readable, Writable):
    """Composes both capabilities; assign only when both are needed."""
    pass
```

A read-only cache can now implement just `Readable` without being forced to implement `write` and `delete`.

## Stable vs Unstable Interfaces

An interface should be **stable** — callers rely on it and shouldn't have to change when you refactor internals. Rules for stability:

1. **Name methods after what they do** (verb phrases), not how they are implemented.
2. **Accept the most general type** your method actually needs (e.g., accept `Iterable` not `list` if you only iterate).
3. **Return the most specific type** you can promise.
4. **Raise named exceptions**, not cryptic status codes or raw integers.
5. **Return copies, not internal objects** — callers should not be able to accidentally mutate your internals.

```python
class Inventory:
    def __init__(self):
        self._items: list = []

    # Unstable: exposes internal list — caller can mutate it
    def get_items_bad(self) -> list:
        return self._items         # caller can do: inv.get_items_bad().clear()

    # Stable: returns a snapshot copy
    def items(self) -> list:
        return list(self._items)   # safe copy, clear name

    def add(self, item: str) -> None:
        if not item:
            raise ValueError("Item name must be non-empty")
        self._items.append(item)

    def remove(self, item: str) -> None:
        try:
            self._items.remove(item)
        except ValueError:
            raise KeyError(f"Item {item!r} not found in inventory")
```

## Writing Effective Docstrings as Part of the Contract

A docstring is part of the interface — it is the first thing a caller reads. A good method docstring covers:

- What the method does (one sentence)
- Key parameters (type and meaning)
- Return value
- Exceptions raised and under what conditions

```python
class PriorityQueue:
    def push(self, item, priority: int) -> None:
        """
        Add item to the queue with the given priority.

        Args:
            item: Any value. Does not need to be comparable.
            priority: Integer priority; **lower numbers dequeue first**.
                      Must be a non-negative integer.

        Raises:
            TypeError:  if priority is not an int.
            ValueError: if priority is negative.
        """
        if not isinstance(priority, int):
            raise TypeError(f"priority must be int, got {type(priority).__name__!r}")
        if priority < 0:
            raise ValueError(f"priority must be >= 0, got {priority}")
        self._heap_push(item, priority)

    def pop(self):
        """
        Remove and return the item with the lowest priority number.

        Returns:
            The item with the lowest priority.

        Raises:
            IndexError: if the queue is empty.
        """
        if not self._data:
            raise IndexError("pop from empty PriorityQueue")
        return self._heap_pop()
```

## Typing Annotations as Machine-Readable Contracts

Type annotations (PEP 484) are another form of contract — they are checked statically by tools like `mypy` and `pyright`:

```python
from typing import Optional, List, Callable

class EventBus:
    def subscribe(self, event: str, callback: Callable[[str], None]) -> None: ...
    def fire(self, event: str, data: str) -> None: ...
    def subscriber_count(self, event: str) -> int: ...
```

Annotated signatures communicate the interface clearly. Running `mypy` on code that uses `EventBus` will catch type mismatches before the program ever runs.

## Comparing Interface Approaches

```
                Interface Approach Comparison
┌─────────────────┬───────────────┬──────────────────────────────┐
│ Approach        │ Enforcement   │ Best for                     │
├─────────────────┼───────────────┼──────────────────────────────┤
│ ABC             │ Runtime       │ Framework base classes        │
│ typing.Protocol │ Static/Runtime│ Duck-typed third-party code  │
│ Docstrings      │ Human         │ Communicating intent         │
│ Type annotations│ Static        │ Machine-checked contracts    │
│ Raise exceptions│ Runtime       │ Precondition/postcondition   │
└─────────────────┴───────────────┴──────────────────────────────┘
```

Real-world code uses all of these together: an ABC for the structural contract, type annotations for static analysis, and clear docstrings and exceptions for runtime safety.

## Key Takeaways

- Keep interfaces small and focused — avoid forcing implementers to define unused methods.
- State preconditions, postconditions, and invariants clearly and enforce them in code.
- Make interfaces stable: name operations by intent, accept general input types, return specific output types, return copies not internal objects.
- A clear docstring is part of the contract — future implementers rely on it.
- Type annotations turn the interface into a machine-readable contract for static analysis.
