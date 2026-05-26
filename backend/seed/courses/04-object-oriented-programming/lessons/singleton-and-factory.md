# Design Patterns: Singleton and Factory

Design patterns are reusable solutions to recurring design problems. They are not code libraries — they are *templates* for solving a class of problems, refined by decades of industry practice. This lesson covers two **Creational** patterns: patterns that control how objects are created.

## The Singleton Pattern

**Intent:** Ensure a class has only one instance and provide a global access point to it.

**When to use:** Configuration managers, logging, database connection pools, thread pools — scenarios where exactly one shared object must exist.

### Implementation via `__new__`

```python
class AppConfig:
    """Application-wide configuration — only one instance ever exists."""

    _instance = None           # class-level holder for the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = {}   # initialise only once
            cls._instance._locked   = False
        return cls._instance

    def set(self, key: str, value) -> None:
        if self._locked:
            raise RuntimeError("Configuration is locked — cannot modify after startup")
        self._settings[key] = value

    def get(self, key: str, default=None):
        return self._settings.get(key, default)

    def lock(self) -> None:
        """Prevent further modifications."""
        self._locked = True

    def __repr__(self) -> str:
        return f"AppConfig({self._settings!r})"
```

```python
cfg1 = AppConfig()
cfg2 = AppConfig()

cfg1.set("debug", True)
cfg1.set("max_workers", 8)

print(cfg2.get("debug"))      # True — same object
print(cfg1 is cfg2)           # True

cfg1.lock()
cfg1.set("timeout", 30)       # RuntimeError: Configuration is locked
```

`__new__` is called before `__init__`. By controlling `__new__`, we guarantee only one object is ever allocated.

### Thread-Safe Singleton

In multi-threaded code, two threads can race to create the first instance. A simple lock prevents this:

```python
import threading

class SafeSingleton:
    _instance = None
    _lock     = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:   # double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance
```

The inner `if` check is needed because two threads could both pass the outer `if` before either acquires the lock.

### Singleton via Module

Python's module system is itself a natural Singleton: a module is imported once and cached. Prefer module-level singletons for simplicity:

```python
# config.py  (module is the singleton)
_settings = {}

def set(key: str, value) -> None:
    _settings[key] = value

def get(key: str, default=None):
    return _settings.get(key, default)
```

```python
import config
config.set("debug", True)
# Any other module that imports config gets the same dict
```

**Caution:** Singletons introduce global state, which makes testing harder. Use them sparingly and prefer dependency injection when possible.

## The Factory Method Pattern

**Intent:** Define an interface for creating an object, but let subclasses or a factory function decide which class to instantiate.

**When to use:** When object creation involves a decision based on context, and you want to decouple callers from concrete classes.

### Simple Factory Function

```python
def create_logger(output: str):
    """Create a logger based on the output destination."""
    if output == "console":
        return ConsoleLogger()
    elif output == "file":
        return FileLogger()
    elif output == "null":
        return NullLogger()
    raise ValueError(f"Unknown logger type: {output!r}")
```

This works but violates OCP — adding a new logger type requires editing the function.

### Registry-Based Factory (extensible)

```python
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None: ...

class ConsoleLogger(Logger):
    def log(self, message: str) -> None:
        print(f"[CONSOLE] {message}")

class FileLogger(Logger):
    def __init__(self, path: str = "app.log"):
        self.path = path
    def log(self, message: str) -> None:
        print(f"[FILE:{self.path}] {message}")

class NullLogger(Logger):
    def log(self, message: str) -> None:
        pass   # discard — useful in tests

class LoggerFactory:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str, logger_cls) -> None:
        cls._registry[name] = logger_cls

    @classmethod
    def create(cls, name: str, **kwargs) -> Logger:
        if name not in cls._registry:
            raise ValueError(f"Unknown logger: {name!r}. "
                             f"Known: {list(cls._registry.keys())}")
        return cls._registry[name](**kwargs)

# Registration happens at module level
LoggerFactory.register("console", ConsoleLogger)
LoggerFactory.register("file",    FileLogger)
LoggerFactory.register("null",    NullLogger)
```

```python
logger = LoggerFactory.create("console")
logger.log("Application started")        # [CONSOLE] Application started

flogger = LoggerFactory.create("file", path="errors.log")
flogger.log("Disk almost full")          # [FILE:errors.log] Disk almost full
```

Adding a new logger type is purely additive — create a class, register it, done.

### Abstract Factory

An **Abstract Factory** groups related factory methods so that a whole *family* of related objects can be swapped together:

```python
from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class Dialog(ABC):
    @abstractmethod
    def render(self) -> str: ...

class WindowsButton(Button):
    def render(self) -> str: return "[Windows Button]"

class WindowsDialog(Dialog):
    def render(self) -> str: return "(Windows Dialog)"

class MacButton(Button):
    def render(self) -> str: return "[Mac Button]"

class MacDialog(Dialog):
    def render(self) -> str: return "(Mac Dialog)"

class UIFactory(ABC):
    """Abstract factory: produces a matched set of UI widgets."""
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_dialog(self) -> Dialog: ...

class WindowsUIFactory(UIFactory):
    def create_button(self) -> Button: return WindowsButton()
    def create_dialog(self) -> Dialog: return WindowsDialog()

class MacUIFactory(UIFactory):
    def create_button(self) -> Button: return MacButton()
    def create_dialog(self) -> Dialog: return MacDialog()

def render_app(factory: UIFactory) -> None:
    """High-level code — never names a concrete class."""
    btn = factory.create_button()
    dlg = factory.create_dialog()
    print(btn.render(), dlg.render())
```

```python
render_app(WindowsUIFactory())  # [Windows Button] (Windows Dialog)
render_app(MacUIFactory())      # [Mac Button] (Mac Dialog)
```

The caller can switch between an entire UI theme by swapping one factory object.

## Pattern Comparison

| Pattern | Creates | Key benefit |
|---------|---------|-------------|
| Singleton | One shared instance | Global access, one object |
| Simple Factory | One object, chosen by input | Centralises creation logic |
| Factory Method | One object, chosen by subclass | Decouples caller from concrete class |
| Abstract Factory | Families of related objects | Swappable product families |

## Anti-Pattern: Abuse of Singleton

A Singleton that carries a large amount of mutable state becomes a hidden global variable:

```python
# Anti-pattern: Singleton as a mutable god-object
class AppState:
    _instance = None
    def __new__(cls): ...   # singleton machinery

    def __init__(self):
        self.current_user = None
        self.shopping_cart = []
        self.active_session = {}
        # ... dozens more fields
```

This makes testing nearly impossible because test isolation requires resetting the Singleton between tests. Prefer small, well-scoped singletons (like configuration) and inject everything else.

## Key Takeaways

- **Singleton**: use `__new__` to guard a single instance; consider thread-safety in concurrent apps; prefer module-level singletons for simplicity.
- **Factory Method**: decouple callers from concrete classes via a creation interface; use a registry to make it OCP-compliant.
- **Abstract Factory**: produce families of related objects and make the entire family swappable by injecting a different factory.
- Be cautious with Singletons — global mutable state is a testing and maintenance liability.
