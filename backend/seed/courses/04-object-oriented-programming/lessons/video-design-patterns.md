# Video: Design Patterns in Python — Creational, Structural, and Behavioral

This video surveys the most widely used Gang of Four design patterns implemented in Python, emphasizing where each pattern fits in a real codebase. The presenter covers Singleton, Factory, Strategy, Observer, Decorator, Adapter, and Command with runnable Python examples and discusses the trade-offs of each.

**Key takeaways:**

- **Creational** (Singleton, Factory): how objects are created and how to decouple callers from concrete classes.
- **Structural** (Decorator, Adapter): wrapping objects to add behavior or translate interfaces without modifying source classes.
- **Behavioral** (Strategy, Observer, Command): how objects collaborate — pluggable algorithms, event-driven notifications, and undo/redo command queues.
- Python-specific idioms: using first-class functions as lightweight strategies, decorators (`@`) as the Decorator pattern, and `__call__` for command objects.
- When NOT to use a pattern — recognizing over-engineering and preferring the simplest design that satisfies current requirements.
