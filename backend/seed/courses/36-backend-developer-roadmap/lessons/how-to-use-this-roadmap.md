# How to Use This Roadmap

This course is a structured 16-week program that takes you from zero experience to a job-ready backend developer using **Java 17+**, **MySQL 8**, **HTML5**, **CSS3**, **JavaScript (ES6+)**, **Git**, and ultimately **Spring Boot**. Before you write a single line of code, spend ten minutes here to understand how everything fits together.

## What This Roadmap Gives You

Most self-taught developers bounce between random tutorials and end up with gaps. This roadmap solves that by giving you:

- A fixed learning sequence — each module builds on the last.
- Real projects at the end of each module (no toy "hello world" forever).
- Coding challenges graded automatically so you get instant feedback.
- Quizzes to consolidate what you learned before moving forward.

## The Seven Modules at a Glance

| # | Module | Key Deliverable |
|---|--------|----------------|
| 1 | Start Here: Roadmap & Setup | Toolchain installed and working |
| 2 | Java Foundations | Finance Tracker + Student Management System |
| 3 | Databases with MySQL | Employee Database project |
| 4 | Web Basics: HTML & CSS | Personal Portfolio website |
| 5 | JavaScript Essentials | Weather Dashboard |
| 6 | Your First Backend & Full-Stack | Full-Stack Contact Manager |
| 7 | Capstone & Career Readiness | Capstone project + portfolio |

Complete them in order. Module 6 assumes you can write a Java class, query a database, and manipulate the DOM — because you will have done all three in the earlier modules.

## How Lessons Work

Each lesson is one of four types:

- **Reading** — the primary teaching format. Read it, run the code samples, take notes.
- **Video** — a curated YouTube lecture that reinforces the reading. Watch it at 1.25× speed if the material feels familiar.
- **Quiz** — a short multiple-choice check. If you score below 80%, re-read the relevant lessons before continuing.
- **Exercise** — a coding challenge with automated test cases. Your solution is judged on standard input/output.

## How Coding Challenges Work

Challenges use a simple stdin/stdout format. The grader pipes input to your program and compares trimmed output to the expected answer. There is no GUI, no network, and no third-party library — just the Java standard library.

A typical challenge looks like this:

```
Input:  3 + 4
Output: 7
```

Your Java solution reads one line, parses it, and prints the result:

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String[] parts = sc.nextLine().trim().split("\\s+");
        long a = Long.parseLong(parts[0]);
        String op = parts[1];
        long b = Long.parseLong(parts[2]);

        long result = switch (op) {
            case "+" -> a + b;
            case "-" -> a - b;
            case "*" -> a * b;
            case "/" -> a / b;
            default  -> throw new IllegalArgumentException("Unknown op: " + op);
        };

        System.out.println(result);
    }
}
```

Notice: one class named `Main`, one `main` method, output via `System.out.println`. Keep it simple — the grader runs exactly `javac Main.java && java Main`.

## Recommended Weekly Pace

Treat this like a part-time bootcamp: **1–2 hours per weekday, 3–4 hours on one weekend day**. That equals roughly 12–15 hours per week, which covers the 60-hour course in about five weeks of focused work — or a relaxed 16 weeks at around 4 hours per week.

Do not skip project lessons. Reading without building produces passive knowledge that evaporates within days.

## Common Mistakes to Avoid

- **Skipping the setup module.** Trying to code with a broken JDK path or a misconfigured `PATH` wastes hours. Follow the installation lesson exactly and verify every tool before proceeding.
- **Copy-pasting code without reading it.** Type examples by hand at least once. Muscle memory and reading comprehension work together.
- **Moving on after a failed quiz.** A quiz failure means a knowledge gap. Fill it now — the gap will compound.
- **Treating projects as optional.** Projects are where skills become permanent. The graded exercises test isolated concepts; the projects test your ability to combine them.

## When You Finish This Roadmap

Once you complete the Capstone module you will have five shipped projects, a working Git history, a portfolio site, and the full-stack fundamentals needed to start **Spring Boot Mastery** (Course 35 in this platform) with confidence.

Start with the next lesson: **The 16-Week Plan at a Glance** — it shows exactly which topics fall in which week so you can plan your schedule before you write any code.
