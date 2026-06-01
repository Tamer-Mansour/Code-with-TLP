# Type Hints

Python is dynamically typed, but **type hints** let you annotate the shapes of values. Tools like mypy, pyright, and Pylance check them statically; the runtime ignores them. Done well, type hints turn whole classes of bugs into red squiggles before you run the code.

## Basics

```python
name: str = "Alice"
age: int = 30
scores: list[int] = []
config: dict[str, str] = {}

def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}"
```

## Union and Optional

```python
def get_user(uid: int) -> User | None:    # 3.10+
    ...

# pre-3.10:
from typing import Optional, Union
def get_user(uid: int) -> Optional[User]:
    ...
```

`Optional[X]` is `X | None`.

## Common typing imports

```python
from typing import Any, Callable, Iterable, Iterator, Generator, TypeVar, Protocol, Literal, TypedDict, Final, ClassVar
```

A few you'll meet often:

```python
Callable[[int, str], bool]               # function (int, str) -> bool
Iterable[User]                           # anything you can `for` over
Iterator[int]                            # has __next__
Literal["red", "green", "blue"]          # one of these strings
Final[int]                               # cannot be reassigned
ClassVar[dict[str, int]]                 # class-level, not instance
```

## Generics with TypeVar

```python
from typing import TypeVar

T = TypeVar("T")

def first(xs: list[T]) -> T:
    return xs[0]
```

`first([1, 2, 3])` returns `int`; `first(["a"])` returns `str`. The checker infers.

## TypedDict — typed dictionaries

```python
from typing import TypedDict

class Order(TypedDict):
    id: int
    total: float
    status: Literal["paid", "pending"]

def process(o: Order) -> None:
    print(o["id"])
```

Useful when you can't (or won't) convert to a dataclass.

## Protocols — structural typing

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

def show(x: Renderable) -> None:
    print(x.render())
```

Any class with a `render` method matches — no inheritance needed. The Pythonic equivalent of Go interfaces.

## Type aliases

```python
UserId = int

def fetch(uid: UserId) -> User:
    ...
```

3.12+ has `type` statement:

```python
type UserId = int
type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
```

## Type-checking tools

```bash
pip install mypy
mypy myproject/

pip install pyright
pyright myproject/
```

Editors with Pylance or pyright-lsp surface errors as you type. Adopt incrementally — most teams start with strictness `--ignore-missing-imports` and dial up.

## When hints are worth their weight

- Public APIs (libraries, framework boundaries).
- Anything more than a few hundred lines.
- Anywhere unit tests don't cover every path.

Tiny scripts? Don't bother. Notebooks? Sometimes. Real applications? Yes, always.

## Hints don't change runtime

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")    # works! returns "helloworld"
```

If you want runtime enforcement, use `pydantic`, `attrs`, or `typeguard`.
