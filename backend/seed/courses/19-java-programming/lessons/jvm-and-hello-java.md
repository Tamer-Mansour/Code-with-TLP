# The JVM and Hello, Java

Java is a statically-typed, object-oriented language that compiles to **bytecode** and runs on the **Java Virtual Machine** (JVM). The JVM gives you garbage collection, just-in-time compilation, and "write once, run anywhere."

## Source → bytecode → execution

```
Hello.java   --javac-->   Hello.class   --java JVM-->   running program
```

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java");
    }
}
```

Compile and run:

```bash
javac Hello.java
java Hello
```

Modern JDKs (17+) let you skip the explicit compile step:

```bash
java Hello.java        # runs source directly
```

## JDK, JRE, JVM

- **JDK** — Java Development Kit. Compiler, tools, JVM, libraries. What you install.
- **JRE** — Just the runtime. Legacy; almost no one installs this separately today.
- **JVM** — The runtime that executes bytecode.

Use a current LTS: **Java 21** (or 17). Old Java 8 is everywhere in legacy systems but lacks records, pattern matching, var, switch expressions, modules.

## Distributions

Oracle's Java is one of many. Free, production-grade alternatives:

- **Eclipse Temurin** (formerly AdoptOpenJDK) — community default.
- **Amazon Corretto** — Amazon's distribution.
- **Azul Zulu** — robust, free for most uses.
- **GraalVM** — JVM + native-image (AOT compilation).

`sdkman` is the easiest way to install and switch between them.

## Build tools

- **Maven** — XML config, most common.
- **Gradle** — Groovy/Kotlin DSL, faster builds.
- **Bazel** — used in larger monorepos.

For learning, write a one-file program; for projects, generate a starter with `mvn archetype:generate` or `gradle init`.

## Conventions

- One **public class per `.java` file**, file name = class name.
- Class names PascalCase, methods/fields camelCase, constants ALL_CAPS.
- Packages = directory structure. `com.example.shop` lives in `com/example/shop/*.java`.

## A second example

```java
package com.example;

public class Calc {
    public static int add(int a, int b) { return a + b; }

    public static void main(String[] args) {
        System.out.println(add(2, 3));
    }
}
```

## JShell — Java REPL

Java 9+ ships JShell:

```bash
jshell
jshell> int x = 5
jshell> x * 2
$2 ==> 10
```

Use it like Python's REPL to try API calls.

## What Java is good for

- Backend services (Spring, Micronaut, Quarkus).
- Big Data (Spark, Flink, Hadoop).
- Android (now mostly Kotlin, but the runtime is the JVM).
- Tooling (Maven, Jenkins, ElasticSearch).

What it's not great for: tiny scripts, CLI utilities (start-up time), unstructured data wrangling (Python wins).
