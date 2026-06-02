# Video: Encapsulation in Python

This video explains how Python implements encapsulation through naming conventions, property decorators, and controlled access to internal state. It demonstrates the single-underscore and double-underscore naming conventions, and shows how `@property`, `@setter`, and `@deleter` turn plain attributes into guarded, validated access points.

**Key takeaways:**

- Why raw public attributes break the open/closed principle and invite invariant violations.
- The `_name` convention (protected by agreement) vs `__name` name mangling (enforced by the interpreter).
- Building read-only properties and write-validated setters with `@property`.
- How invariants — rules that must always hold true — are enforced inside the class boundary.
- Side-by-side comparison of a fragile attribute-based design vs a robust property-based design.
