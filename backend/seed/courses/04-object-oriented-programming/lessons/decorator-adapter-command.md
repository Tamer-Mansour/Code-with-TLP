# Design Patterns: Decorator, Adapter, and Command

This lesson covers three more classic patterns. **Decorator** and **Adapter** are **Structural** patterns — they change how classes are connected. **Command** is a **Behavioral** pattern that turns requests into first-class objects.

## The Decorator Pattern

**Intent:** Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

**When to use:** When you need to add behaviour to individual objects at runtime, or when subclassing would create a combinatorial explosion of classes (e.g., `LoggedCachedEncryptedWriter` is not a sustainable approach).

### Structural Example: Text Formatters

```python
from abc import ABC, abstractmethod

class TextComponent(ABC):
    """The base interface for plain text and decorated text."""
    @abstractmethod
    def render(self) -> str: ...

class PlainText(TextComponent):
    """The core component — the thing being decorated."""
    def __init__(self, text: str):
        self._text = text
    def render(self) -> str:
        return self._text

class TextDecorator(TextComponent):
    """Base decorator — wraps another TextComponent."""
    def __init__(self, component: TextComponent):
        self._component = component
    def render(self) -> str:
        return self._component.render()   # delegate by default

class BoldDecorator(TextDecorator):
    def render(self) -> str:
        return f"**{self._component.render()}**"

class ItalicDecorator(TextDecorator):
    def render(self) -> str:
        return f"_{self._component.render()}_"

class UpperCaseDecorator(TextDecorator):
    def render(self) -> str:
        return self._component.render().upper()
```

```python
text = PlainText("hello world")
print(text.render())                                   # hello world

bold = BoldDecorator(text)
print(bold.render())                                   # **hello world**

bold_italic = ItalicDecorator(BoldDecorator(text))
print(bold_italic.render())                            # _**hello world**_

loud_bold = UpperCaseDecorator(BoldDecorator(text))
print(loud_bold.render())                              # **HELLO WORLD**
```

Any combination of decorators works without adding new subclasses of `PlainText`. The number of combinations is n² with 3 decorators but only 3 classes.

### Python's Built-in Decorator Syntax

Python's `@decorator` syntax is the same concept applied to functions:

```python
import time
import functools

def timed(func):
    """Decorator that measures execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        print(f"{func.__name__} took {(end - start)*1000:.2f} ms")
        return result
    return wrapper

def retry(max_attempts: int = 3):
    """Decorator factory: retries the function on exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"Attempt {attempt} failed: {e}")
            raise last_error
        return wrapper
    return decorator

@timed
@retry(max_attempts=2)
def fetch_data(url: str) -> str:
    # Simulated: raises on first call
    raise ConnectionError("Timeout")
```

Stacking `@timed` on top of `@retry` is exactly like: `fetch_data = timed(retry(2)(fetch_data))`.

## The Adapter Pattern

**Intent:** Convert the interface of a class into another interface that clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

**When to use:** Integrating a third-party library or legacy class whose interface doesn't match what your code expects.

### Class Diagram

```
+--------------------+         +---------------------+
| Target (expected)  |         | Adaptee (existing)  |
|--------------------|         |---------------------|
| + request() : str  |    +--> | + specific_request()|
+--------------------+    |   +---------------------+
         ^                |
         |                |
+--------------------+    |
|     Adapter        |----+
|--------------------|
| + request() : str  |   (wraps Adaptee, translates call)
+--------------------+
```

### Example: Legacy Logger Adapter

```python
# The interface your new code expects
class Logger(ABC):
    @abstractmethod
    def log(self, level: str, message: str) -> None: ...

# A legacy class you cannot modify
class OldLogger:
    def write_entry(self, severity: int, text: str) -> None:
        levels = {1: "INFO", 2: "WARN", 3: "ERROR"}
        label  = levels.get(severity, "UNKNOWN")
        print(f"[OLD:{label}] {text}")

# The adapter: makes OldLogger look like Logger
class OldLoggerAdapter(Logger):
    _LEVEL_MAP = {"info": 1, "warning": 2, "error": 3}

    def __init__(self, old_logger: OldLogger):
        self._old = old_logger

    def log(self, level: str, message: str) -> None:
        severity = self._LEVEL_MAP.get(level.lower(), 1)
        self._old.write_entry(severity, message)
```

```python
# New code only knows about Logger — it doesn't know about OldLogger
def send_audit(logger: Logger, action: str) -> None:
    logger.log("info", f"Action performed: {action}")

legacy  = OldLogger()
adapted = OldLoggerAdapter(legacy)

send_audit(adapted, "user_login")   # [OLD:INFO] Action performed: user_login
```

### Adapter for Multiple Incompatible APIs

```python
# Two third-party payment APIs with completely different interfaces
class StripeAPI:
    def charge(self, amount_cents: int, currency: str, token: str) -> dict:
        return {"status": "ok", "charge_id": "ch_stripe_123"}

class PayPalAPI:
    def create_payment(self, usd_amount: float, buyer_email: str) -> str:
        return "PP-PAY-456"

# Unified interface your e-commerce code expects
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount_usd: float, customer_ref: str) -> str: ...

class StripeAdapter(PaymentGateway):
    def __init__(self, api: StripeAPI):
        self._api = api
    def pay(self, amount_usd: float, customer_ref: str) -> str:
        result = self._api.charge(int(amount_usd * 100), "usd", customer_ref)
        return result["charge_id"]

class PayPalAdapter(PaymentGateway):
    def __init__(self, api: PayPalAPI):
        self._api = api
    def pay(self, amount_usd: float, customer_ref: str) -> str:
        return self._api.create_payment(amount_usd, customer_ref)
```

```python
def process_checkout(gateway: PaymentGateway, amount: float, ref: str) -> None:
    charge_id = gateway.pay(amount, ref)
    print(f"Payment successful: {charge_id}")

stripe  = StripeAdapter(StripeAPI())
paypal  = PayPalAdapter(PayPalAPI())

process_checkout(stripe, 29.99, "tok_abc")   # Payment successful: ch_stripe_123
process_checkout(paypal, 29.99, "user@example.com")   # Payment successful: PP-PAY-456
```

`process_checkout` is entirely independent of the payment provider.

## The Command Pattern

**Intent:** Encapsulate a request as an object, thereby letting you parameterise clients with different requests, queue or log requests, and support undoable operations.

**When to use:** Undo/redo systems, task queues, macro recording, menu systems, transaction processing.

### Core Structure

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...
```

### Example: Text Editor with Undo/Redo

```python
class TextEditor:
    def __init__(self):
        self._text = ""

    def insert(self, pos: int, text: str) -> None:
        self._text = self._text[:pos] + text + self._text[pos:]

    def delete(self, pos: int, length: int) -> None:
        self._text = self._text[:pos] + self._text[pos + length:]

    def get_text(self) -> str:
        return self._text


class InsertCommand(Command):
    def __init__(self, editor: TextEditor, pos: int, text: str):
        self._editor = editor
        self._pos    = pos
        self._text   = text

    def execute(self) -> None:
        self._editor.insert(self._pos, self._text)

    def undo(self) -> None:
        self._editor.delete(self._pos, len(self._text))


class DeleteCommand(Command):
    def __init__(self, editor: TextEditor, pos: int, length: int):
        self._editor  = editor
        self._pos     = pos
        self._length  = length
        self._deleted = ""    # saved for undo

    def execute(self) -> None:
        text  = self._editor.get_text()
        self._deleted = text[self._pos:self._pos + self._length]
        self._editor.delete(self._pos, self._length)

    def undo(self) -> None:
        self._editor.insert(self._pos, self._deleted)


class CommandHistory:
    def __init__(self):
        self._history: list = []
        self._undone: list  = []

    def execute(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd)
        self._undone.clear()   # redo stack is cleared on new action

    def undo(self) -> bool:
        if not self._history:
            return False
        cmd = self._history.pop()
        cmd.undo()
        self._undone.append(cmd)
        return True

    def redo(self) -> bool:
        if not self._undone:
            return False
        cmd = self._undone.pop()
        cmd.execute()
        self._history.append(cmd)
        return True
```

```python
editor  = TextEditor()
history = CommandHistory()

history.execute(InsertCommand(editor, 0, "Hello"))
history.execute(InsertCommand(editor, 5, " World"))
print(editor.get_text())   # Hello World

history.execute(DeleteCommand(editor, 5, 6))
print(editor.get_text())   # Hello

history.undo()
print(editor.get_text())   # Hello World

history.undo()
print(editor.get_text())   # Hello

history.redo()
print(editor.get_text())   # Hello World
```

Every action is a first-class object that knows how to execute and reverse itself. `CommandHistory` is reusable and knows nothing about text editing.

## Pattern Summary

| Pattern | Category | Key idea |
|---------|----------|---------|
| Decorator | Structural | Wrap an object to add behaviour; stack multiple decorators |
| Adapter | Structural | Translate one interface into another to enable compatibility |
| Command | Behavioral | Turn requests into objects; enables undo, queuing, logging |

## Key Takeaways

- **Decorator**: add responsibilities to objects by wrapping them; avoids subclass explosion.
- **Adapter**: bridge between incompatible interfaces without modifying the existing classes.
- **Command**: encapsulate requests as objects to gain undo/redo, queueing, and auditability.
- All three patterns favour composition over inheritance and keep classes focused on a single job.
