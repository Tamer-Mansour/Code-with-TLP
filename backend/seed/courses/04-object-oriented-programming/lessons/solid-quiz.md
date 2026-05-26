# Quiz: SOLID Principles

**Q1. Which SOLID principle says "a class should have only one reason to change"?**

- [x] Single Responsibility Principle
- [ ] Open/Closed Principle
- [ ] Liskov Substitution Principle
- [ ] Dependency Inversion Principle

**Q2. You have a working `PaymentProcessor` class. A new requirement asks you to support crypto payments. According to OCP, what should you do?**

- [ ] Edit `PaymentProcessor` to add an if-branch for crypto
- [ ] Delete `PaymentProcessor` and rewrite it
- [x] Create a new `CryptoPaymentProcessor` subclass or strategy without modifying the existing class
- [ ] Add a `crypto` flag parameter to every existing method

**Q3. A `Bird` class has a `fly()` method. You create a `Penguin` subclass that overrides `fly()` with `raise NotImplementedError`. Which principle does this violate?**

- [ ] Single Responsibility Principle
- [ ] Open/Closed Principle
- [x] Liskov Substitution Principle
- [ ] Interface Segregation Principle

**Q4. Your `Worker` abstract class has methods: `work()`, `eat()`, and `sleep()`. A `RobotWorker` must implement `eat()` and `sleep()` even though robots do neither. Which principle is being violated?**

- [ ] Single Responsibility Principle
- [ ] Liskov Substitution Principle
- [x] Interface Segregation Principle
- [ ] Dependency Inversion Principle

**Q5. In the Dependency Inversion Principle, "high-level modules should depend on abstractions" means:**

- [ ] You should use Python abstract syntax trees
- [ ] High-level classes should import low-level classes directly
- [x] High-level classes should accept interfaces/ABCs, not concrete implementations
- [ ] You should minimise the number of import statements

**Q6. A `Square` class inherits from `Rectangle`. `Square` overrides the width setter so that setting the width also sets the height. Code that sets only width on a `Rectangle` and then checks the height will get a wrong answer when handed a `Square`. This is an example of violating:**

- [ ] Single Responsibility Principle
- [ ] Interface Segregation Principle
- [x] Liskov Substitution Principle
- [ ] Dependency Inversion Principle
