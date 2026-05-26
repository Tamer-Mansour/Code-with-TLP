# Exercise: Animal Sounds via Polymorphism

Build an animal hierarchy and use polymorphism to dispatch the correct `speak()` method at runtime.

Define a base `Animal` class and subclasses `Dog`, `Cat`, `Cow`, and `Duck`. Each subclass overrides a `speak()` method that returns its sound. A command loop creates animals and invokes speak/type queries.

This exercise reinforces:

- Defining a class hierarchy with a shared interface.
- Overriding methods in subclasses to provide type-specific behavior.
- Using a dictionary to track live object instances by name.

See the problem statement for the exact command format and expected output.
