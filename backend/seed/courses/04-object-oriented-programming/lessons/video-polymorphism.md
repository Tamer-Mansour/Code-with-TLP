# Video: Polymorphism and Duck Typing in Python

This video unpacks how Python achieves polymorphism through dynamic dispatch, method overriding, and duck typing. It contrasts Python's structural ("if it quacks like a duck") approach with the nominal interface systems of statically typed languages, and shows how `abc.ABC` and `@abstractmethod` can add optional compile-time safety to duck-typed code.

**Key takeaways:**

- How Python dispatches a method call at runtime based on the object's actual class, not a declared variable type.
- Duck typing: writing functions that accept any object with the right interface without an explicit `isinstance` check.
- Using `abc.ABC` and `@abstractmethod` to declare a required interface and prevent direct instantiation of abstract classes.
- Practical polymorphism examples: a list of mixed shape objects all responding to `.area()`, a plugin system loading different handlers dynamically.
- When `isinstance()` checks are appropriate and when they are a code smell indicating a missing polymorphic dispatch.
