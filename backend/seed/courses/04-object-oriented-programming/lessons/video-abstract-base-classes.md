# Video: Abstract Base Classes and Interfaces in Python

This video dives into Python's `abc` module — how to define abstract base classes, enforce interface contracts, and leverage the `__subclasshook__` mechanism for virtual subclassing. It also introduces Python's `typing.Protocol` as a modern, structural alternative to classic ABCs.

**Key takeaways:**

- The purpose of abstract base classes: document required behavior and prevent incomplete implementations from being instantiated.
- Defining abstract methods with `@abstractmethod` and abstract properties with `@property` combined with `@abstractmethod`.
- Virtual subclassing with `ABC.register()` — making a third-party class satisfy an ABC without modifying it.
- `typing.Protocol` and structural subtyping: defining interfaces that are satisfied automatically by any class with the right method signatures.
- Choosing between ABCs (explicit registration, runtime checks with `isinstance`) and Protocols (structural, static-analysis-friendly) for different design scenarios.
