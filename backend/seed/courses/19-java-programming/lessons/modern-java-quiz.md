# Quiz: Modern Java and Tooling

**Q1. Java records (introduced in Java 16) automatically generate:**
- [ ] Only a constructor.
- [ ] Only `equals()` and `hashCode()`.
- [x] A canonical constructor, `equals()`, `hashCode()`, `toString()`, and accessor methods for all components.
- [ ] Getters and setters for each field.

**Q2. Which Java feature lets you write `String greeting = "Hello, " + name + "!"` more cleanly?**
- [ ] Text blocks
- [x] String templates (`STR."Hello, \{name}!"`) introduced as a preview in Java 21
- [ ] `String.concat()`
- [ ] `StringBuilder.append()`

**Q3. What does `Optional.orElseThrow()` do?**
- [ ] Returns the value if present, or null if absent.
- [ ] Returns the value if present, or a default value if absent.
- [x] Returns the value if present, or throws `NoSuchElementException` if absent.
- [ ] It is equivalent to `Optional.get()`.

**Q4. Sealed classes (Java 17) restrict which classes can:**
- [ ] Access private members of the sealed class.
- [ ] Be instantiated directly.
- [x] Extend or implement the sealed class — only `permits`-listed classes are allowed.
- [ ] Override methods of the sealed class.

**Q5. Maven's `pom.xml` and Gradle's `build.gradle` both define:**
- [x] Project dependencies, build plugins, and lifecycle phases/tasks.
- [ ] JVM runtime arguments only.
- [ ] Source file encoding only.
- [ ] The Java version used by the IDE.

**Q6. In JUnit 5, which annotation marks a method as a test?**
- [ ] `@Test` from `org.junit.Test`
- [x] `@Test` from `org.junit.jupiter.api.Test`
- [ ] `@TestMethod`
- [ ] `@RunWith`

**Q7. Pattern matching for `instanceof` (Java 16+) eliminates the need for:**
- [ ] The `@Override` annotation.
- [x] An explicit cast immediately following an `instanceof` check.
- [ ] Null checks before `instanceof`.
- [ ] Abstract class declarations.

**Q8. `var` in Java (local-variable type inference) can be used for:**
- [ ] Method parameters and return types.
- [ ] Instance fields.
- [x] Local variables inside a method or block only.
- [ ] Generic type parameters.
