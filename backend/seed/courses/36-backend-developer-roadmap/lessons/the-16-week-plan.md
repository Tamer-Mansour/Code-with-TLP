# The 16-Week Plan at a Glance

This roadmap spans 16 weeks and is organized into seven modules. Each module builds directly on the previous one, so resist the urge to skip ahead. By the end you will have written real Java code, designed a relational database, built web pages from scratch, consumed a public API with JavaScript, and shipped your first full-stack Spring Boot application.

## How the Weeks Map to Modules

| Weeks | Module | Core Focus | Capstone Deliverable |
|-------|--------|------------|----------------------|
| 1 | Start Here: Roadmap & Setup | Toolchain, Git, orientation | Dev environment ready |
| 2–5 | Java Foundations | Syntax, OOP, Collections, Exceptions | Finance Tracker (console) |
| 6–8 | Databases with MySQL | Relational model, SQL, schema design | Employee Database |
| 9–10 | Web Basics: HTML & CSS | Document structure, layout, responsive | Portfolio Website |
| 11–13 | JavaScript Essentials | DOM, fetch, async/await, ES6+ | Weather Dashboard |
| 14–15 | Your First Backend & Full-Stack | REST, Spring Boot, JWT, CORS | Full-Stack Contact Manager |
| 16 | Capstone & Career Readiness | Portfolio polish, Git collaboration, job prep | Capstone project + resume |

## What You Build Along the Way

Five hands-on projects thread through the roadmap so you always have something concrete to show:

- **Personal Finance Tracker** — a console Java application that reads income and expense entries, calculates a running balance, and writes a summary report to a file using `BufferedWriter`.
- **Employee Database** — a MySQL schema with `employees`, `departments`, and `salaries` tables; populated with seed data and queried with multi-table JOINs.
- **Portfolio Website** — a fully responsive static site (HTML5 + CSS3 Grid/Flexbox) that works on mobile and passes Lighthouse accessibility checks.
- **Weather Dashboard** — a pure JavaScript page that calls the Open-Meteo API with `fetch` and renders a 7-day forecast in the DOM without any framework.
- **Full-Stack Contact Manager** — a Spring Boot REST backend (`/api/contacts`) paired with a vanilla-JS frontend; secured with a stateless JWT token.

## A Concrete Milestone: End of Week 5

After finishing Module 2 (Java Foundations) you should be able to write and run a program like this without help:

```java
import java.util.ArrayList;
import java.util.List;

public class FinanceTracker {

    record Entry(String description, double amount) {}

    public static void main(String[] args) {
        List<Entry> ledger = new ArrayList<>();
        ledger.add(new Entry("Salary",    3_500.00));
        ledger.add(new Entry("Rent",     -1_200.00));
        ledger.add(new Entry("Groceries",  -320.50));
        ledger.add(new Entry("Freelance",   800.00));

        double balance = ledger.stream()
                               .mapToDouble(Entry::amount)
                               .sum();

        ledger.forEach(e ->
            System.out.printf("%-15s %+.2f%n", e.description(), e.amount()));
        System.out.printf("%n%-15s %+.2f%n", "Balance", balance));
    }
}
```

If this snippet looks foreign today, do not worry — every piece of it (records, streams, lambdas, printf formatting) is covered step-by-step in Module 2.

## A Concrete Milestone: End of Week 8

After MySQL you should be comfortable creating a normalized schema and querying it:

```sql
CREATE TABLE departments (
    id   INT          PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE employees (
    id            INT          PRIMARY KEY AUTO_INCREMENT,
    full_name     VARCHAR(150) NOT NULL,
    department_id INT          NOT NULL,
    hire_date     DATE         NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Who was hired in 2024, with their department name?
SELECT e.full_name, d.name AS department, e.hire_date
FROM   employees e
JOIN   departments d ON d.id = e.department_id
WHERE  YEAR(e.hire_date) = 2024
ORDER  BY e.hire_date;
```

## Common Mistakes at This Stage

- **Skipping the setup week.** A misconfigured JDK or wrong `JAVA_HOME` will waste hours later. Invest the time in Week 1.
- **Treating SQL as an afterthought.** Indexes, foreign keys, and `JOIN` logic matter even in simple projects. Learn them properly in Weeks 6–8.
- **Jumping to Spring Boot too early.** Spring Boot abstracts away Java fundamentals. Finish Modules 2–5 before touching the framework.
- **Committing directly to `main`.** From Week 1, use feature branches and pull requests — the capstone module assumes you already have this habit.

## Best Practices to Apply From Day One

- Commit small, working increments with descriptive messages (`git commit -m "feat: add balance calculation to FinanceTracker"`).
- Keep one Git repository per project; link each to a public GitHub repo so your portfolio grows automatically.
- Run your code after every significant change. Waiting to test a 200-line diff makes debugging miserable.

## Where This Roadmap Ends

Week 16 closes with a capstone project and a career-readiness session (resume, GitHub profile, interview prep). The roadmap does **not** cover Spring Boot Data JPA, Spring Security, Docker, or microservices — those are the first chapters of the **Spring Boot Mastery** course, which is the recommended next step.

Think of this roadmap as building the foundation; Spring Boot Mastery is where you raise the walls.
