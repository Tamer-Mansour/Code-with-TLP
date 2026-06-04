# Quiz: SOLID Principles and Design Patterns

Test your understanding of the five SOLID design principles and the Gang of Four design patterns.

---

**Question 1.** Which SOLID principle states that a class should have only one reason to change?

[ ] Open/Closed Principle
[x] Single Responsibility Principle
[ ] Liskov Substitution Principle
[ ] Interface Segregation Principle

---

**Question 2.** You add a new payment method to your system by creating a new class that implements `PaymentGateway` — without modifying any existing payment code. Which principle does this design satisfy?

[x] Open/Closed Principle
[ ] Single Responsibility Principle
[ ] Dependency Inversion Principle
[ ] Liskov Substitution Principle

---

**Question 3.** A `Square` class inherits from `Rectangle` and overrides `set_width()` to also update the height. Code that uses a `Rectangle` behaves incorrectly when a `Square` is passed. Which SOLID principle is violated?

[ ] Single Responsibility Principle
[ ] Interface Segregation Principle
[x] Liskov Substitution Principle
[ ] Open/Closed Principle

---

**Question 4.** Your `IWorker` interface has methods `work()`, `eat()`, and `sleep()`. A `Robot` class that implements `IWorker` must provide empty implementations of `eat()` and `sleep()`. Which principle is violated?

[ ] Open/Closed Principle
[ ] Dependency Inversion Principle
[x] Interface Segregation Principle
[ ] Single Responsibility Principle

---

**Question 5.** An `OrderService` class instantiates a `MySQLOrderRepository` directly in its constructor. Which principle does this violate?

[ ] Single Responsibility Principle
[ ] Liskov Substitution Principle
[x] Dependency Inversion Principle
[ ] Interface Segregation Principle

---

**Question 6.** Which design pattern ensures that a class has only one instance and provides a global access point to it?

[ ] Factory Method
[ ] Prototype
[x] Singleton
[ ] Builder

---

**Question 7.** The Strategy pattern falls into which Gang of Four category?

[ ] Creational
[ ] Structural
[x] Behavioral
[ ] Architectural

---

**Question 8.** You need to make an existing third-party library's interface compatible with your application's expected interface, without modifying the library. Which pattern do you use?

[x] Adapter
[ ] Facade
[ ] Proxy
[ ] Decorator

---

**Question 9.** The Observer pattern is best described as:

[ ] A pattern that lets a class create objects without specifying exact classes
[x] A pattern where an object notifies multiple subscribers automatically when its state changes
[ ] A pattern that composes objects into tree structures
[ ] A pattern that defines a skeleton algorithm in a base class with steps overridden by subclasses

---

**Question 10.** Which principle warns against adding abstraction layers before they are needed — often phrased as "You Ain't Gonna Need It"?

[ ] DRY
[x] YAGNI
[ ] KISS
[ ] SOLID
