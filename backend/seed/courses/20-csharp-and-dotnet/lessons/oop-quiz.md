# Quiz: OOP in C#

**Q1. Which keyword marks a method as overridable in a base class?**
- [ ] `abstract`
- [x] `virtual`
- [ ] `override`
- [ ] `new`

**Q2. A class marked `sealed` can:**
- [ ] Be subclassed but not instantiated
- [ ] Have its methods overridden by derived classes
- [x] Not be subclassed at all
- [ ] Only be used as an interface

**Q3. What is the correct way to call the base class constructor from a derived class?**
- [ ] `super(args)`
- [ ] `base.Constructor(args)`
- [x] `: base(args)` in the derived constructor signature
- [ ] `Parent(args)` inside the constructor body

**Q4. Which of the following CAN an interface contain in C# 8+?**
- [ ] Instance fields
- [x] Default method implementations
- [ ] Constructors
- [ ] Static fields (with state)

**Q5. What does the `is` pattern matching expression do?**
- [ ] Calls a type's `Equals` method
- [ ] Converts an object without type checking
- [x] Tests the runtime type and, if matching, binds the variable
- [ ] Works only on value types

**Q6. You have `IEnumerable<Dog> dogs`. Which assignment is valid if `Dog : IAnimal`?**
- [x] `IEnumerable<IAnimal> animals = dogs;`
- [ ] `IList<IAnimal> animals = dogs;`
- [ ] `List<IAnimal> animals = dogs;`
- [ ] None — generics are never covariant

**Q7. An `abstract` class differs from an `interface` in that:**
- [ ] Abstract classes support multiple inheritance
- [x] Abstract classes can have instance fields and a constructor
- [ ] Interfaces cannot have any method implementations
- [ ] Abstract classes cannot have abstract methods
