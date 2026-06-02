# Quiz: Object-Oriented Programming in Java

**Q1. Which keyword is used to call a parent class constructor from a subclass?**
- [ ] `this()`
- [x] `super()`
- [ ] `parent()`
- [ ] `base()`

**Q2. What does the `final` keyword do when applied to a class?**
- [ ] Makes all fields immutable
- [ ] Prevents field reassignment
- [x] Prevents the class from being subclassed
- [ ] Makes all methods static

**Q3. An interface in Java 8+ can contain:**
- [ ] Only abstract method declarations
- [ ] Abstract methods and fields only
- [x] Abstract methods, default methods, and static methods
- [ ] Concrete method implementations only

**Q4. Which of the following best describes polymorphism?**
- [ ] Hiding implementation details behind an interface
- [ ] Inheriting behavior from a parent class
- [x] A subclass object being treated as an instance of its superclass
- [ ] Overloading a method with different parameter types

**Q5. What is the output of the following code?**

```java
class Animal {
    String speak() { return "..."; }
}
class Dog extends Animal {
    @Override
    String speak() { return "Woof"; }
}
Animal a = new Dog();
System.out.println(a.speak());
```

- [ ] `...`
- [x] `Woof`
- [ ] Compilation error
- [ ] `null`

**Q6. Which access modifier makes a member accessible only within the same package and to subclasses?**
- [ ] `private`
- [ ] `public`
- [ ] `default` (package-private)
- [x] `protected`

**Q7. Records in Java (Java 16+) automatically generate:**
- [ ] `toString()` only
- [x] Constructor, getters, `equals()`, `hashCode()`, and `toString()`
- [ ] Only `equals()` and `hashCode()`
- [ ] A builder pattern

**Q8. What is the difference between method overloading and method overriding?**
- [ ] Overloading occurs at runtime; overriding at compile-time
- [x] Overloading uses the same name with different parameters in the same class; overriding redefines a superclass method in a subclass
- [ ] They are the same concept
- [ ] Overriding requires the `static` keyword
