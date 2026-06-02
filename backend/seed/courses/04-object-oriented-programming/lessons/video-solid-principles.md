# Video: The SOLID Principles Explained

This video walks through all five SOLID principles with clear before-and-after code examples in Python. Each principle is introduced with a concrete anti-pattern, followed by a refactored design that satisfies the principle, so you can see exactly what changes and why it matters.

**Key takeaways:**

- **S — Single Responsibility Principle**: a class should have only one reason to change; how to spot and split "god classes."
- **O — Open/Closed Principle**: extend behavior by adding new code, not by modifying existing classes; strategy and template-method patterns as tools.
- **L — Liskov Substitution Principle**: subclasses must be usable wherever the parent is expected without breaking callers; common violations (square/rectangle trap).
- **I — Interface Segregation Principle**: prefer small, focused interfaces over fat ones; how to split a bloated ABC into targeted protocols.
- **D — Dependency Inversion Principle**: high-level modules depend on abstractions, not concretions; constructor injection as the primary tool.
