# Quiz: Design Patterns

**Q1. The Singleton pattern's primary goal is to:**

- [ ] Create a new instance every time it is called
- [x] Ensure only one instance of a class exists and provide a global access point to it
- [ ] Separate the interface from the implementation
- [ ] Allow multiple algorithms to be swapped at runtime

**Q2. In the Factory Method pattern, who decides which concrete class to instantiate?**

- [ ] The caller directly
- [ ] A global registry function with no indirection
- [x] A subclass or factory method, keeping the caller decoupled from concrete classes
- [ ] Python's `__init__` mechanism automatically

**Q3. The Strategy pattern is best described as:**

- [ ] A way to ensure a class has only one instance
- [ ] A way to notify multiple objects of state changes
- [x] Encapsulating interchangeable algorithms behind a shared interface so they can be swapped at runtime
- [ ] A one-to-many dependency notification mechanism

**Q4. In the Observer pattern, what is the "subject"?**

- [ ] The observer that receives notifications
- [x] The object that maintains the list of observers and fires events when its state changes
- [ ] The interface that all observers must implement
- [ ] The data payload passed during notification

**Q5. Which pattern directly supports the Open/Closed Principle by allowing new behaviors to be added via new classes without modifying existing code?**

- [ ] Singleton
- [x] Strategy
- [ ] Template Method (always requires editing the base class to add a new step)
- [ ] Observer (subject must always change when new event types are added)

**Q6. You need to add logging and timing to several existing functions without modifying those functions. Which pattern best describes this approach?**

- [ ] Factory Method
- [ ] Observer
- [x] Decorator
- [ ] Singleton
