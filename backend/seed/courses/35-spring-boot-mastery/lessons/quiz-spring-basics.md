# Quiz: Spring Boot Basics

Test your understanding of what Spring Boot is, how it relates to the broader Spring ecosystem, and the
fundamentals of scaffolding, configuring, and running your first application.

---

**Q1. Which annotation marks the entry point of a Spring Boot application and combines `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`?**
- [ ] `@SpringApplication`
- [ ] `@EnableSpringBoot`
- [x] `@SpringBootApplication`
- [ ] `@AutoConfiguration`

---

**Q2. What is the primary role of Spring Boot's auto-configuration mechanism?**
- [ ] It generates Java source code for your controllers automatically.
- [ ] It replaces the need for a JDK by bundling its own runtime.
- [ ] It compiles your application ahead of time to a native binary.
- [x] It detects libraries on the classpath and registers sensible default beans so you don't have to configure them manually.

---

**Q3. Spring Initializr (start.spring.io) generates a project with a standard Maven structure. Which file is the root descriptor that declares dependencies and build plugins for a Maven project?**
- [ ] `build.gradle`
- [ ] `application.properties`
- [x] `pom.xml`
- [ ] `settings.xml`

---

**Q4. After generating a Spring Boot project with Maven, what is the correct command to compile and package it into an executable JAR?**

```bash
# Which command produces the runnable JAR in the target/ directory?
```

- [ ] `mvn install:jar`
- [ ] `mvn compile`
- [x] `mvn clean package`
- [ ] `mvn spring-boot:jar`

---

**Q5. Where does Spring Boot look for application configuration properties by default (in order of precedence, highest first)?**

| Priority | Location |
|----------|----------|
| 1 (highest) | Command-line arguments (`--server.port=9090`) |
| 2 | `application.properties` / `application.yml` inside the JAR |
| 3 | `application.properties` / `application.yml` on the classpath root |
| 4 (lowest) | Default values from `@ConfigurationProperties` classes |

Given this table, which `application.properties` entry correctly changes the embedded server port to `9090`?

- [ ] `spring.server.port=9090`
- [x] `server.port=9090`
- [ ] `tomcat.port=9090`
- [ ] `spring.boot.port=9090`

---

**Q6. Which statement about Spring Boot's embedded server is correct?**
- [ ] An embedded server is only available when the `war` packaging type is selected.
- [ ] Spring Boot requires an external Tomcat installation; the embedded option is a paid add-on.
- [x] Spring Boot packages an embedded Tomcat (or Jetty/Undertow) inside the executable JAR, so no separate server installation is needed to run the application.
- [ ] The embedded server listens on port 80 by default and cannot be changed without rebuilding.

---

**Q7. Examine the following `pom.xml` snippet. What does inheriting from `spring-boot-starter-parent` give you?**

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
    <relativePath/>
</parent>
```

- [ ] It automatically generates REST controllers based on your entity classes.
- [ ] It provides a runtime JVM bundled with the Maven build.
- [ ] It replaces Maven with Gradle for faster builds.
- [x] It manages dependency versions (BOM), sets default compiler settings to Java 17, and configures common plugins such as `spring-boot-maven-plugin`.

---

**Q8. What is the default embedded web server port when you start a Spring Boot application without any custom configuration?**
- [ ] 80
- [ ] 443
- [x] 8080
- [ ] 8443

---

**Q9. A developer adds only `spring-boot-starter-web` to their `pom.xml`. Which components does Spring Boot's auto-configuration register automatically as a result?**
- [ ] A datasource bean connected to an in-memory H2 database.
- [ ] A Spring Security filter chain requiring HTTP Basic authentication on every endpoint.
- [x] An embedded Tomcat server, a `DispatcherServlet`, and default MVC configuration including Jackson for JSON serialization.
- [ ] A scheduled task runner and an async executor thread pool.

---

**Q10. Which Spring Boot project structure convention is correct for a class that should be detected by component scanning without any extra configuration?**
- [ ] The main class can be placed in any package; Spring Boot scans the entire classpath regardless.
- [ ] Component classes must live in a package named `components` directly under `src/main/java`.
- [x] Application components (controllers, services, repositories) should be placed in the same package as or sub-packages of the class annotated with `@SpringBootApplication`, because component scanning starts from that package by default.
- [ ] The `@ComponentScan` annotation must be added explicitly to every configuration class for beans to be discovered.
