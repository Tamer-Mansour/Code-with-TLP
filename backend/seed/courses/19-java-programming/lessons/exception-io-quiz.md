# Quiz: Exception Handling and I/O

**Q1. Which exception is thrown when `Integer.parseInt("abc")` is called?**
- [ ] `IOException`
- [ ] `IllegalArgumentException`
- [x] `NumberFormatException`
- [ ] `ClassCastException`

**Q2. A checked exception must be:**
- [x] Either caught with `try-catch` or declared in the method signature with `throws`.
- [ ] Always caught immediately.
- [ ] A subclass of `RuntimeException`.
- [ ] Logged before rethrowing.

**Q3. What is the main benefit of `try-with-resources`?**
- [ ] It allows catching multiple exception types in one block.
- [ ] It prevents `NullPointerException` inside the block.
- [x] Resources implementing `AutoCloseable` are automatically closed when the block exits, even if an exception is thrown.
- [ ] It makes the block run in a separate thread.

**Q4. In Java, `String == String` tests:**
- [x] Reference equality — whether both variables point to the same object in memory.
- [ ] Content equality — whether both strings contain the same characters.
- [ ] Whether either string is null.
- [ ] Lexicographic order.

**Q5. Which statement about Java's garbage collector is accurate?**
- [ ] The GC eliminates all memory leaks.
- [x] The GC collects objects with no reachable references, but static collections, unclosed streams, and unremoved listeners can still cause memory leaks.
- [ ] The GC runs synchronously after each object allocation.
- [ ] Calling `System.gc()` guarantees immediate collection.

**Q6. The `finally` block in a try-catch-finally runs:**
- [ ] Only if no exception is thrown.
- [ ] Only if an exception is thrown and caught.
- [ ] Only if an exception is thrown but not caught.
- [x] Always, whether or not an exception was thrown, unless the JVM itself exits (e.g. `System.exit()`).

**Q7. `BufferedReader` wraps `FileReader` mainly to:**
- [ ] Handle character encoding conversion.
- [x] Add buffering so that reads are batched, reducing expensive OS-level file system calls.
- [ ] Provide try-with-resources support.
- [ ] Enable binary mode reading.

**Q8. Which exception is unchecked?**
- [ ] `IOException`
- [ ] `SQLException`
- [ ] `ClassNotFoundException`
- [x] `ArrayIndexOutOfBoundsException`
