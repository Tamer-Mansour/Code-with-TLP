# Video: Java Full Course for Beginners

This video provides a comprehensive introduction to Java programming — from installing the JDK and writing your first `Hello, World!` program through object-oriented principles, collections, and basic I/O.

## What you'll learn

- Setting up the JDK 17+ and compiling/running `.java` files from the command line
- Java syntax fundamentals: variables, data types, operators, and control flow (`if`, `for`, `while`, `switch`)
- Defining classes, constructors, and methods; understanding `static` vs instance members
- Core OOP concepts: encapsulation, inheritance, polymorphism, and interfaces
- Working with the Java Collections Framework (`ArrayList`, `HashMap`)
- Reading input with `Scanner` and handling checked exceptions with `try-catch`

## Key takeaways

- The JVM compiles source to bytecode, making Java platform-independent
- `public static void main(String[] args)` is the mandatory entry point for every standalone program
- Strong static typing catches many bugs at compile time rather than at runtime
- Interfaces and abstract classes are the foundation of every Spring Boot abstraction you will encounter later in this roadmap

## Follow-along checklist

```bash
# Verify your setup before watching
java -version        # should print 17.x or higher
javac -version       # compiler must match the JDK version
mkdir java-basics && cd java-basics
```

```java
// HelloWorld.java — compile with: javac HelloWorld.java && java HelloWorld
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
    }
}
```

- [ ] JDK 17+ installed and `JAVA_HOME` set
- [ ] `javac HelloWorld.java` compiles without errors
- [ ] `java HelloWorld` prints `Hello, Java!`
- [ ] IDE (IntelliJ IDEA Community or VS Code + Extension Pack for Java) configured

The link in this lesson opens a curated YouTube search surfacing free, full-length Java courses from trusted channels such as freeCodeCamp so you can pick the video that best matches your current level.
