# Quiz: RAII, Smart Pointers, and Move Semantics

**Q1. What does RAII stand for?**
- [ ] Resource Allocation Is Immediate
- [x] Resource Acquisition Is Initialization
- [ ] Runtime Allocation Is Invalid
- [ ] Reference Alias Is Implicit

**Q2. When does a `std::unique_ptr` release its managed object?**
- [ ] When you call `release()`
- [ ] When you call `reset()`
- [ ] When you call `delete` on it
- [x] When the `unique_ptr` goes out of scope or is reset

**Q3. Which of the following correctly transfers ownership of a `unique_ptr`?**
- [ ] `auto p2 = p1;`
- [x] `auto p2 = std::move(p1);`
- [ ] `auto p2 = *p1;`
- [ ] `auto p2 = p1.get();`

**Q4. `std::shared_ptr` uses which mechanism to decide when to delete the managed object?**
- [ ] A garbage collector
- [ ] A destructor chain
- [x] Reference counting
- [ ] Scope tracking

**Q5. What is `std::weak_ptr` primarily used for?**
- [ ] As a faster version of `shared_ptr`
- [ ] To hold sole ownership of a resource
- [x] To break reference cycles in `shared_ptr` graphs
- [ ] To replace raw pointers in C APIs

**Q6. After `std::move(obj)` is called, what is the state of `obj`?**
- [ ] Destroyed immediately
- [ ] Unchanged
- [x] Valid but unspecified — safe to reassign or destroy, not to read
- [ ] Set to `nullptr`

**Q7. The Rule of Five says: if you define a destructor, you should also define:**
- [ ] Only the copy constructor
- [ ] The copy constructor and copy assignment operator
- [x] Copy constructor, copy assignment, move constructor, and move assignment
- [ ] Nothing — the compiler handles the rest

**Q8. Which lock wrapper is best for locking two mutexes simultaneously without risk of deadlock?**
- [ ] `std::lock_guard`
- [ ] `std::unique_lock`
- [x] `std::scoped_lock`
- [ ] `std::shared_lock`
