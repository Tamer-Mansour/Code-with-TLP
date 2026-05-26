# SOLID: Single Responsibility and Open/Closed Principles

**SOLID** is a set of five design principles that guide you toward code that is easy to maintain, extend, and test. Each letter is a principle. This lesson covers the first two — the ones you will apply every time you design a class.

## S — Single Responsibility Principle (SRP)

> A class should have only one reason to change.

Robert C. Martin coined "reason to change" to mean: the class is only responsible for one *actor's* concerns. If you can describe what a class does and the description requires the word "and", it likely violates SRP.

### Violation

```python
class Report:
    def __init__(self, title: str, rows: list):
        self.title = title
        self.rows  = rows

    # Responsibility 1: data assembly / business logic
    def generate(self) -> dict:
        return {"title": self.title, "row_count": len(self.rows), "rows": self.rows}

    # Responsibility 2: formatting
    def to_html(self) -> str:
        html = f"<h1>{self.title}</h1><ul>"
        for row in self.rows:
            html += f"<li>{row}</li>"
        return html + "</ul>"

    # Responsibility 3: persistence / I/O
    def save_to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_html())
```

Three reasons to change: the data model changes, the HTML template changes, or the file-saving mechanism changes. Any one of those changes could accidentally break the others.

### Fixed

```python
class Report:
    """Only knows about the report's data."""
    def __init__(self, title: str, rows: list):
        self.title = title
        self.rows  = rows

    def summary(self) -> dict:
        return {"title": self.title, "row_count": len(self.rows)}


class HtmlFormatter:
    """Only knows how to format data as HTML."""
    def format(self, report: Report) -> str:
        html = f"<h1>{report.title}</h1><ul>"
        for row in report.rows:
            html += f"<li>{row}</li>"
        return html + "</ul>"


class MarkdownFormatter:
    """Another formatter — added without touching Report or HtmlFormatter."""
    def format(self, report: Report) -> str:
        lines = [f"# {report.title}", ""]
        for row in report.rows:
            lines.append(f"- {row}")
        return "\n".join(lines)


class FileSaver:
    """Only knows how to save text to a file."""
    def save(self, content: str, path: str) -> None:
        with open(path, "w") as f:
            f.write(content)
```

```python
report = Report("Q3 Sales", ["Alice: 120", "Bob: 95", "Carol: 140"])
html   = HtmlFormatter().format(report)
md     = MarkdownFormatter().format(report)
# FileSaver().save(html, "report.html")  # works in a real environment
```

Each class now has exactly one reason to change. Adding PDF output means adding a `PdfFormatter` — no existing class is modified.

### Identifying SRP Violations

Ask yourself: *If the [business rules / format / storage mechanism / email content] changes, does this class need to be edited?* If yes for more than one category, you have an SRP violation.

## O — Open/Closed Principle (OCP)

> Software entities should be open for extension but closed for modification.

Once a class is working and tested, you should be able to *add* new behaviour without *editing* existing code. Extension happens by adding new classes, not by modifying old ones.

### Violation

```python
class ShippingCalculator:
    def calculate(self, weight: float, method: str) -> float:
        if method == "standard":
            return weight * 2.5
        elif method == "express":
            return weight * 5.0
        elif method == "overnight":
            return weight * 8.0
        # Adding "drone" delivery requires editing this method — OCP violated
        raise ValueError(f"Unknown method: {method}")
```

Every new shipping method requires editing a working, tested function. Each edit is a regression risk.

### Fixed

```python
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, weight: float) -> float: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class StandardShipping(ShippingStrategy):
    @property
    def name(self) -> str: return "standard"
    def calculate(self, weight: float) -> float: return weight * 2.5


class ExpressShipping(ShippingStrategy):
    @property
    def name(self) -> str: return "express"
    def calculate(self, weight: float) -> float: return weight * 5.0


class OvernightShipping(ShippingStrategy):
    @property
    def name(self) -> str: return "overnight"
    def calculate(self, weight: float) -> float: return weight * 8.0


class DroneShipping(ShippingStrategy):     # NEW — zero existing classes modified
    @property
    def name(self) -> str: return "drone"
    def calculate(self, weight: float) -> float:
        return max(4.0, weight * 3.0)      # flat minimum $4


class ShippingCalculator:
    def __init__(self):
        self._strategies: dict = {}

    def register(self, strategy: ShippingStrategy) -> None:
        self._strategies[strategy.name] = strategy

    def calculate(self, weight: float, method: str) -> float:
        if method not in self._strategies:
            raise ValueError(f"Unknown shipping method: {method!r}")
        return self._strategies[method].calculate(weight)
```

```python
calc = ShippingCalculator()
for s in [StandardShipping(), ExpressShipping(), OvernightShipping(), DroneShipping()]:
    calc.register(s)

print(calc.calculate(10, "standard"))   # 25.0
print(calc.calculate(10, "express"))    # 50.0
print(calc.calculate(10, "drone"))      # 30.0
print(calc.calculate(1,  "drone"))      # 4.0  (minimum applies)
```

Adding drone shipping required zero modifications to existing code. `ShippingCalculator` is truly "closed for modification".

### OCP with Decorators (Python-specific)

Python's function decorators are a natural implementation of OCP — you extend a function's behaviour by wrapping it, not editing it:

```python
def logged(func):
    """Decorator that extends any function with logging — no edits to the function."""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@logged
def add(x, y):
    return x + y

add(3, 4)
# Calling add
# add returned 7
```

`add` is not modified — a new `wrapper` extends it.

## SRP and OCP Together

These two principles reinforce each other:

| Principle | Question to ask yourself |
|-----------|--------------------------|
| SRP | Does my class have more than one reason to change? |
| OCP | Would adding a new feature require editing an existing class? |

When SRP is followed (small, focused classes), OCP becomes easier: there is less code to "lock down" and more clear extension points. A class with a single, well-defined purpose is far easier to make "closed for modification".

### Before/After at a Glance

```
BEFORE (violates both):
┌─────────────────────────────────┐
│ UserManager                     │
│ + create_user()                 │  <- domain logic
│ + save_to_db()                  │  <- persistence
│ + send_welcome_email()          │  <- messaging
│ + format_user_report()          │  <- formatting
└─────────────────────────────────┘

AFTER (respects both):
┌──────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│  User    │  │ UserRepository │  │ EmailService │  │ ReportService│
│ (data)   │  │ save()         │  │ send()       │  │ format()     │
└──────────┘  └────────────────┘  └──────────────┘  └──────────────┘
```

Each box has one reason to change. Adding a new email provider means replacing `EmailService`, touching nothing else.

## Key Takeaways

- **SRP**: one class = one responsibility = one reason to change.
- **OCP**: extend behaviour by adding new code, not editing existing code.
- Use abstract base classes and polymorphism to make extensions purely additive.
- Both principles push you toward small, focused classes connected at well-defined seams.
- A failing smell: "I need to edit this class every time we get a new requirement" — that is either an SRP or OCP violation.
