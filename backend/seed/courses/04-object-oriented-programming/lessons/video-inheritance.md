# Video: Inheritance and the super() Function

This video covers Python's inheritance model — how a subclass extends or specializes a parent class, how `super()` chains constructors and method calls correctly, and when to prefer composition over inheritance. Real class hierarchies (shapes, employees, vehicles) are built step by step to show both the power and the pitfalls of deep inheritance chains.

**Key takeaways:**

- Syntax for defining a subclass and understanding the method resolution order (MRO).
- Calling the parent constructor with `super().__init__()` to avoid duplicating initialization logic.
- Overriding methods to specialize behavior while preserving the parent's contract.
- Multiple inheritance in Python and how the MRO (C3 linearization) determines which method wins.
- The "favor composition over inheritance" rule and concrete cases where composition is the better choice.
