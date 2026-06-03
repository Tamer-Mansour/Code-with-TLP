# Quiz: Getting Started

Test your understanding of the roadmap structure, the toolchain, and the Git fundamentals covered in this module. Each question has exactly one correct answer.

---

**Q1. Which Java version is the minimum requirement for this roadmap, and what is the key reason to choose an LTS release over a non-LTS one?**
- [ ] Java 11, because it introduced the module system (JPMS)
- [ ] Java 8, because it is the most widely deployed version in production
- [x] Java 17+, because LTS releases receive long-term security and maintenance updates, making them stable for production and learning
- [ ] Java 21, because non-LTS releases are never supported by IDEs

---

**Q2. You run the following command after installing the JDK and setting `JAVA_HOME`:**

```bash
java -version
```

The output shows `openjdk 17.0.11 2024-04-16`. What does this confirm?**
- [ ] The JRE is installed but the compiler (`javac`) is not yet available
- [ ] The JDK was installed but `JAVA_HOME` is still unset
- [x] A Java 17 JDK is installed and accessible on the system PATH
- [ ] Only the runtime is present; you must install the JDK separately to compile code

---

**Q3. Which Git command creates an exact copy of a remote repository in a new local directory, including all branches and commit history?**
- [ ] `git init`
- [ ] `git fetch`
- [ ] `git pull`
- [x] `git clone`

---

**Q4. After editing a file, you want to record your changes with a meaningful message. What is the correct sequence of Git commands?**
- [ ] `git commit -m "message"` then `git add .`
- [x] `git add <file>` then `git commit -m "message"`
- [ ] `git push` then `git commit -m "message"`
- [ ] `git status` then `git push origin main`

---

**Q5. The roadmap is divided into 16 weeks across multiple technology areas. Which is the correct high-level progression order?**
- [ ] HTML/CSS → JavaScript → MySQL → Java → Spring Boot
- [ ] Spring Boot → Java → MySQL → HTML/CSS → JavaScript
- [x] Java → MySQL → HTML/CSS → JavaScript → Spring Boot
- [ ] MySQL → Java → Spring Boot → HTML/CSS → JavaScript

---

**Q6. You want to verify that MySQL 8 is running and accept connections on the default port. Which command checks the default port MySQL listens on?**
- [x] MySQL's default port is 3306; you can verify a running instance with `mysql -u root -p` and a successful login prompt confirms it is accepting connections
- [ ] MySQL's default port is 5432; use `psql -U root` to connect
- [ ] MySQL's default port is 8080; use `curl localhost:8080` to check
- [ ] MySQL's default port is 1521; the client command is `sqlplus`

---

**Q7. Which of the following best describes the role of an IDE (such as IntelliJ IDEA or VS Code with Java extensions) in this roadmap's workflow?**
- [ ] It replaces the JDK, so you do not need to install Java separately
- [ ] It is only needed for Spring Boot development; plain Java uses only the terminal
- [ ] It manages your MySQL schema automatically, removing the need for SQL scripts
- [x] It provides code completion, inline error highlighting, a debugger, and integrated terminal, significantly speeding up development and learning

---

**Q8. A teammate shares this `.gitignore` snippet:**

```
target/
*.class
.idea/
```

What does each line suppress from being tracked by Git?**
- [ ] `target/` ignores source files; `*.class` ignores test results; `.idea/` ignores database dumps
- [ ] All three lines ignore binary files produced by the linker
- [x] `target/` ignores Maven/Gradle build output, `*.class` ignores compiled bytecode, and `.idea/` ignores IntelliJ project-specific settings that should not be shared
- [ ] `target/` ignores the Git remote URL; `*.class` ignores Java source files; `.idea/` ignores shell scripts

---

**Q9. Node.js is listed in the toolchain even though this is a Java backend roadmap. What is its primary purpose here?**
- [ ] Node.js is the runtime used to execute Java programs in the browser
- [ ] Node.js replaces Maven as the build tool for Java projects
- [x] Node.js provides `npm`/`npx` tooling needed for frontend tooling and live-reload servers when building the HTML/CSS/JavaScript modules
- [ ] Node.js is required to run MySQL migrations on Windows

---

**Q10. Which statement about the `git push` command is accurate in the context of this roadmap's GitHub workflow?**
- [ ] `git push` automatically merges your branch into `main` on the remote
- [ ] `git push` is only available after creating a pull request on GitHub
- [ ] You must run `git pull` after every `git push` to keep the local copy in sync
- [x] `git push origin main` uploads your committed local changes to the `main` branch of the linked remote repository on GitHub
