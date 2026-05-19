"""
Seed for "SQL Fundamentals" course under the Databases subject.
8 modules · 24 lessons · 10 exercises · 45+ test cases.

Run from the backend/ directory:
    python seed/sql_fundamentals_seed.py
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, Course, Difficulty, Exercise, Lesson, LessonType, Module, Subject, Tag, TestCase

LANGS = ["python"]

# ─────────────────────────────────────────────
# Idempotent helpers
# ─────────────────────────────────────────────

def _subject(db, slug): return db.scalar(select(Subject).where(Subject.slug == slug))
def _course(db, slug): return db.scalar(select(Course).where(Course.slug == slug))

def _module(db, course, title, order_index, summary=""):
    m = db.scalar(select(Module).where(Module.course_id == course.id, Module.title == title))
    if m: return m
    m = Module(course_id=course.id, title=title, order_index=order_index, summary=summary)
    db.add(m); db.flush(); return m

def _lesson(db, module, slug, **kwargs):
    l = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.slug == slug))
    if l: return l
    l = Lesson(module_id=module.id, slug=slug, **kwargs)
    db.add(l); db.flush(); return l

def _exercise(db, lesson, slug, **kwargs):
    e = db.scalar(select(Exercise).where(Exercise.slug == slug))
    if e: return e
    e = Exercise(lesson_id=lesson.id, slug=slug, **kwargs)
    db.add(e); db.flush(); return e

def _cases(db, exercise, cases):
    if exercise.test_cases: return
    for i, (stdin, expected, hidden) in enumerate(cases):
        db.add(TestCase(exercise_id=exercise.id, name=f"case-{i+1}", stdin=stdin, expected_stdout=expected, is_hidden=hidden, weight=1, order_index=i))


# ════════════════════════════════════════════════════════════════
# MODULE 1 — Introduction to Relational Databases
# ════════════════════════════════════════════════════════════════

M1_WHAT_IS_DB = """\
# What is a Relational Database?

A **relational database** is an organized collection of data stored and accessed electronically. It models data as a set of **tables** (also called *relations*), where each table has named columns and typed rows. The relational model was proposed by Edgar F. Codd at IBM in 1970 and remains the dominant paradigm for structured data storage today.

## Brief History

- **1970** — Codd publishes "A Relational Model of Data for Large Shared Data Banks"
- **1979** — Oracle releases the first commercial SQL RDBMS
- **1986** — SQL becomes an ANSI/ISO standard
- **1996** — PostgreSQL (then Postgres) releases version 6.0 as open source
- **2000s** — MySQL becomes the web's most popular open-source database
- **2013** — SQLite surpasses all others in *deployment count* (embedded in every smartphone)

## Tables, Rows, and Columns

Data lives in **tables**. Every table has a fixed set of **columns** (attributes), each with a name and data type. Every **row** (tuple) represents one record:

```sql
CREATE TABLE employees (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL,
    dept     TEXT,
    salary   REAL    NOT NULL DEFAULT 0.0
);
```

Here `employees` is the table, `id / name / dept / salary` are columns, and each inserted employee is a row.

## Primary Keys and Foreign Keys

A **primary key** uniquely identifies each row in a table. It must be unique and NOT NULL.

A **foreign key** is a column (or set of columns) that references the primary key of another table, enforcing **referential integrity**:

```sql
CREATE TABLE departments (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE employees (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    dept_id INTEGER REFERENCES departments(id)
);
```

If you try to insert an employee with a `dept_id` that doesn't exist in `departments`, the database will reject it.

## ACID Properties

Relational databases guarantee **ACID** for transactions:

| Property | Meaning |
|---|---|
| **Atomicity** | A transaction is all-or-nothing — partial updates never persist |
| **Consistency** | The database moves from one valid state to another |
| **Isolation** | Concurrent transactions don't interfere with each other |
| **Durability** | Once committed, data survives crashes and restarts |

## Popular RDBMS Systems

| System | License | Best Known For |
|---|---|---|
| **PostgreSQL** | Open Source | Standards compliance, extensibility, JSON support |
| **MySQL / MariaDB** | Open Source | Web applications, WordPress, LAMP stack |
| **SQLite** | Public Domain | Embedded use, mobile apps, learning SQL |
| **SQL Server** | Commercial | Microsoft ecosystem, enterprise .NET apps |
| **Oracle DB** | Commercial | Large enterprises, financial systems |

## Why Learn Relational Databases?

Even in a world of NoSQL and cloud-native data stores, relational databases power the vast majority of transactional applications. Understanding SQL is a fundamental skill for backend engineers, data analysts, and data scientists alike. The concepts — normalization, joins, indexing — transfer directly to understanding *why* systems behave the way they do.
"""

M1_SQL_OVERVIEW = """\
# SQL Language Overview

**SQL** (Structured Query Language) is the standard language for interacting with relational databases. It is **declarative**: you describe *what* data you want, and the database engine figures out *how* to retrieve it efficiently.

SQL is divided into four main sub-languages:

## DDL — Data Definition Language

DDL statements define and modify the **structure** of database objects.

```sql
-- Create a table
CREATE TABLE products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    price    REAL    NOT NULL,
    stock    INTEGER DEFAULT 0
);

-- Add a column
ALTER TABLE products ADD COLUMN category TEXT;

-- Delete a table permanently
DROP TABLE IF EXISTS products;
```

## DML — Data Manipulation Language

DML statements add, change, and remove **data** inside tables.

```sql
INSERT INTO products (name, price, stock) VALUES ('Widget', 9.99, 100);
UPDATE products SET price = 11.99 WHERE name = 'Widget';
DELETE FROM products WHERE stock = 0;
```

## DQL — Data Query Language

DQL is the SELECT statement — the most frequently used SQL command.

```sql
SELECT name, price
FROM   products
WHERE  price > 10
ORDER  BY price DESC;
```

## DCL — Data Control Language

DCL manages **permissions** (applies mainly to multi-user servers like PostgreSQL/MySQL):

```sql
GRANT  SELECT ON products TO analyst_role;
REVOKE INSERT ON products FROM analyst_role;
```

## TCL — Transaction Control Language

TCL controls **transaction boundaries**:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
UPDATE accounts SET balance = balance + 500 WHERE id = 2;
COMMIT;   -- or ROLLBACK; to undo
```

## SQLite Data Types

SQLite uses a flexible **type affinity** system. The five storage classes are:

| Storage Class | Description |
|---|---|
| **INTEGER** | Signed integer (1–8 bytes) |
| **REAL** | 8-byte IEEE floating-point |
| **TEXT** | UTF-8/16 string |
| **BLOB** | Binary data stored as-is |
| **NULL** | Missing value |

## Common Column Constraints

```sql
CREATE TABLE users (
    id       INTEGER PRIMARY KEY,
    email    TEXT    NOT NULL UNIQUE,
    username TEXT    NOT NULL,
    score    INTEGER DEFAULT 0,
    CHECK (score >= 0)
);
```

| Constraint | Effect |
|---|---|
| `NOT NULL` | Column must have a value |
| `UNIQUE` | All values in column must differ |
| `DEFAULT val` | Used when no value supplied |
| `CHECK (expr)` | Row rejected if expression is false |
| `PRIMARY KEY` | Implies NOT NULL + UNIQUE; identifies rows |
| `REFERENCES` | Enforces foreign-key integrity |

SQL's declarative nature means you can often rewrite queries in multiple equivalent ways and the optimizer will choose the same execution plan. Focus on expressing *what* you need clearly and correctly, and let the engine handle efficiency.
"""

M1_SQLITE_STARTED = """\
# Getting Started with SQLite

**SQLite** is a self-contained, serverless relational database engine. Unlike PostgreSQL or MySQL, there is no separate server process — the entire database lives in a single cross-platform file (`.db`). This makes it perfect for learning SQL.

## Why SQLite for Learning?

- **Zero configuration** — no installation of a server, no users, no ports
- **File-based** — share your database by copying one file
- **Full SQL support** — JOINs, CTEs, window functions, triggers, full-text search
- **Ships with Python** — `import sqlite3` works in every Python installation
- **Used everywhere** — Android, iOS, Firefox, Chrome, and millions of applications

## The SQLite CLI

After installing SQLite (or using the bundled shell), start it with:

```bash
sqlite3 mydb.db
```

Useful dot-commands (they start with `.` and are not SQL):

| Command | Description |
|---|---|
| `.tables` | List all tables |
| `.schema tablename` | Show CREATE statement for a table |
| `.mode column` | Display results in aligned columns |
| `.headers on` | Show column names in results |
| `.quit` | Exit the shell |
| `.read file.sql` | Execute SQL from a file |

## Python `sqlite3` Module

Python ships with the `sqlite3` standard library module. The basic pattern is:

```python
import sqlite3

# 1. Open (or create) a database file
conn = sqlite3.connect("mydb.db")

# 2. Get a cursor to execute SQL
cur = conn.cursor()

# 3. Create a table
cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT    NOT NULL,
        grade TEXT,
        score REAL
    )
''')

# 4. Insert rows (use ? placeholders — NEVER string-format user data)
cur.execute("INSERT INTO students (name, grade, score) VALUES (?, ?, ?)",
            ("Alice", "A", 95.5))
cur.execute("INSERT INTO students (name, grade, score) VALUES (?, ?, ?)",
            ("Bob",   "B", 82.0))

# 5. Commit the transaction
conn.commit()

# 6. Query
cur.execute("SELECT name, score FROM students ORDER BY score DESC")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

# 7. Close
conn.close()
```

## Using `:memory:` for Exercises

For coding exercises, use an **in-memory database** — it disappears when your program exits, which is ideal for isolated test runs:

```python
conn = sqlite3.connect(":memory:")
```

## Complete First Example

```python
import sqlite3, sys

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.execute('''
    CREATE TABLE products (
        id       INTEGER PRIMARY KEY,
        name     TEXT NOT NULL,
        price    REAL NOT NULL
    )
''')

# Read input and insert rows
for line in sys.stdin:
    name, price = line.strip().split(",")
    cur.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                (name, float(price)))
conn.commit()

# Query
cur.execute("SELECT name, price FROM products WHERE price > 10 ORDER BY price")
for name, price in cur.fetchall():
    print(f"{name}: {price:.2f}")

conn.close()
```

This pattern — create, insert from stdin, query, print results — is the template for all SQL exercises in this course.
"""


def seed_module1(db: Session, course: Course) -> None:
    mod = _module(db, course, "Introduction to Relational Databases", 1,
                  "RDBMS history, SQL sub-languages, data types, and SQLite setup.")

    _lesson(db, mod, "what-is-a-database",
            title="What is a Relational Database?",
            lesson_type=LessonType.reading,
            content_md=M1_WHAT_IS_DB,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "sql-overview",
            title="SQL Language Overview",
            lesson_type=LessonType.reading,
            content_md=M1_SQL_OVERVIEW,
            duration_minutes=12,
            order_index=2)

    _lesson(db, mod, "sqlite-getting-started",
            title="Getting Started with SQLite",
            lesson_type=LessonType.reading,
            content_md=M1_SQLITE_STARTED,
            duration_minutes=10,
            order_index=3)


# ════════════════════════════════════════════════════════════════
# MODULE 2 — Basic SELECT Queries
# ════════════════════════════════════════════════════════════════

M2_SELECT_BASICS = """\
# SELECT Statement Fundamentals

The `SELECT` statement is the most important SQL command — it retrieves data from one or more tables. Mastering SELECT is the foundation for everything else in SQL.

## Basic Syntax

```sql
SELECT column1, column2
FROM   table_name;
```

Use `*` to select all columns (convenient for exploration, avoid in production code):

```sql
SELECT * FROM products;
```

## Column Aliases

Rename columns in the result with `AS`:

```sql
SELECT name AS product_name,
       price * 1.1 AS price_with_tax
FROM   products;
```

## DISTINCT — Remove Duplicates

```sql
SELECT DISTINCT category FROM products;
```

## LIMIT and OFFSET — Pagination

```sql
-- First 10 rows
SELECT * FROM products LIMIT 10;

-- Rows 11–20 (skip first 10, take next 10)
SELECT * FROM products LIMIT 10 OFFSET 10;
```

## ORDER BY — Sorting Results

```sql
-- Ascending (default)
SELECT name, price FROM products ORDER BY price;

-- Descending
SELECT name, price FROM products ORDER BY price DESC;

-- Multiple sort keys
SELECT name, category, price
FROM   products
ORDER  BY category ASC, price DESC;
```

## Logical Query Processing Order

SQL has a **logical processing order** that differs from the written order. Understanding this prevents many common mistakes:

| Step | Clause | What happens |
|---|---|---|
| 1 | `FROM` | Identify source tables |
| 2 | `WHERE` | Filter rows |
| 3 | `GROUP BY` | Group remaining rows |
| 4 | `HAVING` | Filter groups |
| 5 | `SELECT` | Compute output columns |
| 6 | `ORDER BY` | Sort results |
| 7 | `LIMIT` | Trim result set |

This is why you **cannot** use a SELECT alias in a WHERE clause — WHERE is processed before SELECT computes the alias.

## Examples with a Products Table

```sql
CREATE TABLE products (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    category TEXT NOT NULL,
    price    REAL NOT NULL,
    stock    INTEGER NOT NULL DEFAULT 0
);
```

Find all electronics under $500, cheapest first:
```sql
SELECT name, price
FROM   products
WHERE  category = 'Electronics' AND price < 500
ORDER  BY price ASC;
```

Count distinct categories:
```sql
SELECT COUNT(DISTINCT category) AS num_categories
FROM   products;
```

Top 5 most expensive products:
```sql
SELECT name, price
FROM   products
ORDER  BY price DESC
LIMIT  5;
```

## NULL Values

`NULL` means "unknown" or "missing". Any comparison with NULL returns NULL (not TRUE or FALSE). Use `IS NULL` / `IS NOT NULL`:

```sql
SELECT name FROM products WHERE stock IS NULL;
SELECT name FROM products WHERE stock IS NOT NULL;
```
"""

M2_WHERE_CLAUSE = """\
# Filtering with WHERE

The `WHERE` clause filters rows before they appear in results. Only rows where the condition evaluates to TRUE are kept.

## Comparison Operators

```sql
SELECT * FROM products WHERE price = 9.99;   -- equal
SELECT * FROM products WHERE price != 9.99;  -- not equal (<> also works)
SELECT * FROM products WHERE price > 10;     -- greater than
SELECT * FROM products WHERE price >= 10;    -- greater than or equal
SELECT * FROM products WHERE price < 5;      -- less than
SELECT * FROM products WHERE price <= 5;     -- less than or equal
```

## BETWEEN — Range Check

```sql
-- Inclusive on both ends
SELECT name, price FROM products WHERE price BETWEEN 10 AND 50;
-- Equivalent to: WHERE price >= 10 AND price <= 50
```

## IN — Membership Check

```sql
SELECT name FROM products
WHERE  category IN ('Electronics', 'Books', 'Clothing');

-- NOT IN
SELECT name FROM products
WHERE  category NOT IN ('Electronics', 'Books');
```

## LIKE — Pattern Matching

`%` matches any sequence of characters; `_` matches exactly one character.

```sql
-- Names starting with 'Pro'
SELECT name FROM products WHERE name LIKE 'Pro%';

-- Names ending with 'er'
SELECT name FROM products WHERE name LIKE '%er';

-- Names with exactly 5 characters
SELECT name FROM products WHERE name LIKE '_____';

-- Names containing 'book' anywhere (case-insensitive in SQLite by default for ASCII)
SELECT name FROM products WHERE name LIKE '%book%';
```

## IS NULL / IS NOT NULL

```sql
SELECT name FROM products WHERE description IS NULL;
SELECT name FROM products WHERE description IS NOT NULL;
```

**Never use `= NULL`** — it always returns NULL (falsy), not TRUE.

## Logical Operators: AND, OR, NOT

```sql
-- AND: both conditions must be true
SELECT name FROM products
WHERE  category = 'Electronics' AND price < 100;

-- OR: at least one condition must be true
SELECT name FROM products
WHERE  category = 'Books' OR category = 'Magazines';

-- NOT: negates a condition
SELECT name FROM products
WHERE  NOT category = 'Clearance';
```

## Operator Precedence

`NOT` binds tighter than `AND`, which binds tighter than `OR`. Use parentheses to be explicit:

```sql
-- Without parens: AND evaluated first, then OR
SELECT * FROM products
WHERE  category = 'Books' OR category = 'Electronics' AND price < 100;

-- With parens: clearer intent
SELECT * FROM products
WHERE  (category = 'Books' OR category = 'Electronics') AND price < 100;
```

## Combining Multiple Conditions

```sql
SELECT name, category, price
FROM   products
WHERE  price BETWEEN 5 AND 50
  AND  category IN ('Books', 'Music')
  AND  name LIKE 'The%'
ORDER  BY price;
```

## Pattern Matching Best Practices

- **Leading wildcards (`%value`) are slow** — they prevent index use; avoid when possible
- **Use `LIKE` for simple patterns**, regular expressions (via `REGEXP` in some DBs) for complex ones
- **SQLite's `LIKE` is case-insensitive for ASCII letters** but case-sensitive for Unicode characters above U+0127
"""


def seed_module2(db: Session, course: Course) -> None:
    mod = _module(db, course, "Basic SELECT Queries", 2,
                  "SELECT fundamentals, WHERE filtering, and first coding exercises.")

    _lesson(db, mod, "select-basics",
            title="SELECT Statement Fundamentals",
            lesson_type=LessonType.reading,
            content_md=M2_SELECT_BASICS,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "where-clause",
            title="Filtering with WHERE",
            lesson_type=LessonType.reading,
            content_md=M2_WHERE_CLAUSE,
            duration_minutes=10,
            order_index=2)

    ex_lesson = _lesson(db, mod, "select-exercises",
                        title="Basic SELECT Exercises",
                        lesson_type=LessonType.exercise,
                        content_md="Practice SELECT queries using Python and sqlite3.",
                        duration_minutes=25,
                        order_index=3)

    # ── Exercise 2.1: Find Products Above Price ──────────────────
    e1 = _exercise(db, ex_lesson, "sql-find-products-above-price",
        title="Find Products Above Price",
        prompt_md=(
            "# Find Products Above Price\n\n"
            "You are given a list of products and a price threshold. "
            "Find all product names and prices where the price is **strictly greater** than the threshold, "
            "ordered by price **descending**.\n\n"
            "**Input format:**\n"
            "- First line: integer threshold\n"
            "- Remaining lines: `name,category,price,stock` (one product per line)\n\n"
            "**Output format:** one line per matching product: `name: price` "
            "(price formatted as a plain integer or float, no trailing zeros beyond 2 decimal places)\n\n"
            "**Example**\n"
            "```\nInput:\n20\nWidget,Tools,9.99,50\nGadget,Electronics,29.99,10\nDoohickey,Tools,49.99,5\n\n"
            "Output:\nDoohickey: 49.99\nGadget: 29.99\n```\n\n"
            "Use Python's `sqlite3` module to create an in-memory database, insert the products, "
            "and run a SELECT query to produce the answer."
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "threshold = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('''\n"
                "    CREATE TABLE products (\n"
                "        id INTEGER PRIMARY KEY,\n"
                "        name TEXT NOT NULL,\n"
                "        category TEXT,\n"
                "        price REAL NOT NULL,\n"
                "        stock INTEGER\n"
                "    )\n"
                "''')\n\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    name, category, price, stock = parts[0], parts[1], float(parts[2]), int(parts[3])\n"
                "    cur.execute('INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)',\n"
                "                (name, category, price, stock))\n"
                "conn.commit()\n\n"
                "# TODO: Write a SELECT query to find products with price > threshold,\n"
                "# ordered by price DESC, and print 'name: price' for each.\n"
                "# Your query here:\n"
                "# cur.execute(...)\n"
                "# for row in cur.fetchall():\n"
                "#     print(...)\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "threshold = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('''\n"
                "    CREATE TABLE products (\n"
                "        id INTEGER PRIMARY KEY,\n"
                "        name TEXT NOT NULL,\n"
                "        category TEXT,\n"
                "        price REAL NOT NULL,\n"
                "        stock INTEGER\n"
                "    )\n"
                "''')\n\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    name, category, price, stock = parts[0], parts[1], float(parts[2]), int(parts[3])\n"
                "    cur.execute('INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)',\n"
                "                (name, category, price, stock))\n"
                "conn.commit()\n\n"
                "cur.execute('SELECT name, price FROM products WHERE price > ? ORDER BY price DESC', (threshold,))\n"
                "for name, price in cur.fetchall():\n"
                "    p = int(price) if price == int(price) else price\n"
                "    print(f'{name}: {p}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=10,
    )
    _cases(db, e1, [
        ("20\nWidget,Tools,9.99,50\nGadget,Electronics,29.99,10\nDoohickey,Tools,49.99,5\n",
         "Doohickey: 49.99\nGadget: 29.99", False),
        ("10\nApple,Fruit,1.5,100\nBanana,Fruit,0.75,200\nCherry,Fruit,15.0,30\n",
         "Cherry: 15.0", False),
        ("0\nPen,Office,1.25,500\nNotebook,Office,3.5,200\nStapler,Office,8.0,75\n",
         "Stapler: 8.0\nNotebook: 3.5\nPen: 1.25", True),
        ("100\nLaptop,Electronics,999.99,5\nPhone,Electronics,599.99,20\nTablet,Electronics,399.99,15\n",
         "Laptop: 999.99\nPhone: 599.99\nTablet: 399.99", True),
        ("50\nHammer,Tools,12.99,40\nDrill,Tools,89.99,10\nSaw,Tools,49.99,8\nLevel,Tools,25.0,20\n",
         "Drill: 89.99", True),
    ])

    # ── Exercise 2.2: Count Products Per Category ────────────────
    e2 = _exercise(db, ex_lesson, "sql-count-category",
        title="Count Products Per Category",
        prompt_md=(
            "# Count Products Per Category\n\n"
            "Given a list of products, count how many products belong to each category. "
            "Output the results ordered **alphabetically by category name**.\n\n"
            "**Input format:** lines of `name,category,price` (no header)\n\n"
            "**Output format:** `category: count` per line, alphabetical order\n\n"
            "**Example**\n"
            "```\nInput:\nWidget,Tools,9.99\nGadget,Electronics,29.99\nHammer,Tools,15.0\n\n"
            "Output:\nElectronics: 1\nTools: 2\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE products (name TEXT, category TEXT, price REAL)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO products VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "# TODO: SELECT category, COUNT(*) grouped by category, ordered alphabetically\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE products (name TEXT, category TEXT, price REAL)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO products VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "cur.execute('SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY category ASC')\n"
                "for category, cnt in cur.fetchall():\n"
                "    print(f'{category}: {cnt}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=10,
    )
    _cases(db, e2, [
        ("Widget,Tools,9.99\nGadget,Electronics,29.99\nHammer,Tools,15.0\n",
         "Electronics: 1\nTools: 2", False),
        ("Apple,Fruit,1.5\nBanana,Fruit,0.75\nCarrot,Vegetable,0.5\nDate,Fruit,3.0\n",
         "Fruit: 3\nVegetable: 1", False),
        ("A,Z,1\nB,Z,2\nC,A,3\nD,M,4\nE,A,5\nF,M,6\n",
         "A: 2\nM: 2\nZ: 2", True),
        ("Solo,Unique,99.99\n",
         "Unique: 1", True),
        ("X,Alpha,1\nY,Beta,2\nZ,Alpha,3\nW,Gamma,4\nV,Beta,5\nU,Alpha,6\n",
         "Alpha: 3\nBeta: 2\nGamma: 1", True),
    ])

    # ── Exercise 2.3: Top N Most Expensive Products ──────────────
    e3 = _exercise(db, ex_lesson, "sql-top-n-products",
        title="Top N Most Expensive Products",
        prompt_md=(
            "# Top N Most Expensive Products\n\n"
            "Find the names of the **top N** most expensive products, ordered from most to least expensive. "
            "If two products have the same price, order them alphabetically by name.\n\n"
            "**Input format:**\n"
            "- First line: integer N\n"
            "- Remaining lines: `name,category,price`\n\n"
            "**Output format:** product names, one per line\n\n"
            "**Example**\n"
            "```\nInput:\n2\nAlpha,A,50.0\nBeta,B,30.0\nGamma,C,75.0\n\n"
            "Output:\nGamma\nAlpha\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE products (name TEXT, category TEXT, price REAL)')\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO products VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "# TODO: SELECT top N products by price DESC, name ASC, print names\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE products (name TEXT, category TEXT, price REAL)')\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO products VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "cur.execute('SELECT name FROM products ORDER BY price DESC, name ASC LIMIT ?', (n,))\n"
                "for (name,) in cur.fetchall():\n"
                "    print(name)\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, e3, [
        ("2\nAlpha,A,50.0\nBeta,B,30.0\nGamma,C,75.0\n",
         "Gamma\nAlpha", False),
        ("3\nA,X,10\nB,X,20\nC,X,30\nD,X,40\nE,X,50\n",
         "E\nD\nC", False),
        ("1\nOnly,Cat,999.0\n",
         "Only", True),
        ("2\nAardvark,Z,100\nZebra,Z,100\nMango,Z,50\n",
         "Aardvark\nZebra", True),
    ])


# ════════════════════════════════════════════════════════════════
# MODULE 3 — Aggregate Functions and GROUP BY
# ════════════════════════════════════════════════════════════════

M3_AGGREGATE = """\
# COUNT, SUM, AVG, MIN, MAX

**Aggregate functions** operate on a set of rows and return a single value. They are the workhorses of reporting and analytics queries.

## The Five Core Aggregates

| Function | Returns | Notes |
|---|---|---|
| `COUNT(*)` | Number of rows | Includes rows with NULLs |
| `COUNT(col)` | Non-NULL values in col | Ignores NULLs |
| `COUNT(DISTINCT col)` | Distinct non-NULL values | |
| `SUM(col)` | Total of all values | Returns NULL if all values are NULL |
| `AVG(col)` | Arithmetic mean | Ignores NULLs |
| `MIN(col)` | Smallest value | Works on text (alphabetical) too |
| `MAX(col)` | Largest value | Works on text too |

## COUNT(*) vs COUNT(column)

This is one of the most important distinctions:

```sql
-- counts ALL rows (including rows where bonus IS NULL)
SELECT COUNT(*) FROM employees;

-- counts only rows where bonus is not NULL
SELECT COUNT(bonus) FROM employees;

-- counts distinct department values
SELECT COUNT(DISTINCT dept) FROM employees;
```

## SUM and AVG

```sql
SELECT
    SUM(amount)                AS total_revenue,
    AVG(amount)                AS avg_sale,
    ROUND(AVG(amount), 2)      AS avg_sale_rounded,
    MIN(amount)                AS smallest_sale,
    MAX(amount)                AS largest_sale
FROM sales;
```

`AVG` **ignores NULL rows** — it divides by the count of non-NULL values, not by total row count. This matters when NULLs mean "no data" vs "zero":

```sql
-- If you want NULLs to count as 0:
SELECT AVG(COALESCE(bonus, 0)) FROM employees;
```

## Aggregates with WHERE

The `WHERE` clause filters rows **before** aggregation:

```sql
-- Average salary only for the Engineering department
SELECT AVG(salary) FROM employees WHERE dept = 'Engineering';
```

## Combining Multiple Aggregates

```sql
SELECT
    COUNT(*)           AS total_products,
    COUNT(DISTINCT category) AS num_categories,
    MIN(price)         AS cheapest,
    MAX(price)         AS most_expensive,
    ROUND(AVG(price),2) AS avg_price,
    SUM(stock * price) AS inventory_value
FROM products
WHERE stock > 0;
```

## NULL Handling Summary

```sql
CREATE TABLE t (val INTEGER);
INSERT INTO t VALUES (1), (2), (NULL), (4);

SELECT COUNT(*) FROM t;       -- 4 (NULL row counted)
SELECT COUNT(val) FROM t;     -- 3 (NULL ignored)
SELECT SUM(val) FROM t;       -- 7 (NULL treated as 0 in sum)
SELECT AVG(val) FROM t;       -- 2.333... (sum/3, NULL ignored)
SELECT MIN(val) FROM t;       -- 1
SELECT MAX(val) FROM t;       -- 4
```

## Practical Example: Sales Dashboard

```sql
SELECT
    COUNT(*)                         AS num_transactions,
    ROUND(SUM(amount), 2)            AS total_revenue,
    ROUND(AVG(amount), 2)            AS avg_transaction,
    MAX(amount)                      AS largest_transaction,
    COUNT(DISTINCT customer_id)      AS unique_customers
FROM sales
WHERE sale_date >= '2024-01-01';
```
"""

M3_GROUP_BY = """\
# GROUP BY and HAVING

`GROUP BY` collapses multiple rows that share the same value in one or more columns into a single summary row. Combined with aggregate functions, it enables powerful reporting.

## Basic GROUP BY

```sql
SELECT category, COUNT(*) AS num_products
FROM   products
GROUP  BY category;
```

This produces one row per distinct `category` value.

## The Golden Rule of GROUP BY

**Every column in SELECT must either be in GROUP BY or wrapped in an aggregate function.**

```sql
-- WRONG: name is neither aggregated nor in GROUP BY
SELECT category, name, COUNT(*)
FROM   products
GROUP  BY category;

-- CORRECT
SELECT category, COUNT(*) AS cnt, AVG(price) AS avg_price
FROM   products
GROUP  BY category;
```

## HAVING — Filtering Groups

`WHERE` filters individual rows (before grouping). `HAVING` filters groups (after aggregation):

```sql
-- Only show categories with more than 5 products
SELECT category, COUNT(*) AS cnt
FROM   products
GROUP  BY category
HAVING cnt > 5;       -- SQLite allows alias here; use COUNT(*) > 5 for portability

-- Equivalent portable form
SELECT category, COUNT(*) AS cnt
FROM   products
GROUP  BY category
HAVING COUNT(*) > 5;
```

## WHERE vs HAVING

```sql
-- WHERE filters rows BEFORE grouping
-- HAVING filters groups AFTER aggregation
SELECT dept, AVG(salary) AS avg_sal
FROM   employees
WHERE  hire_year >= 2020       -- only employees hired in 2020+
GROUP  BY dept
HAVING AVG(salary) > 60000;   -- only depts with avg > 60k
```

## GROUP BY Multiple Columns

```sql
SELECT dept, job_title, COUNT(*) AS headcount, AVG(salary) AS avg_sal
FROM   employees
GROUP  BY dept, job_title
ORDER  BY dept, avg_sal DESC;
```

## Common Mistakes

1. **Selecting non-aggregated columns not in GROUP BY** — SQL error in strict mode, unpredictable in SQLite
2. **Using WHERE to filter aggregates** — must use HAVING instead
3. **Confusing COUNT(*) and COUNT(col)** — COUNT(*) counts all rows; COUNT(col) skips NULLs
4. **HAVING without GROUP BY** — treats the entire table as one group (valid but rare)

## Practical Example: Sales by Quarter

```sql
SELECT
    salesperson,
    quarter,
    COUNT(*)          AS num_sales,
    SUM(amount)       AS total,
    ROUND(AVG(amount), 2) AS avg_sale
FROM   sales
GROUP  BY salesperson, quarter
HAVING SUM(amount) > 1000
ORDER  BY total DESC;
```

## Rollup Concept

Some databases support `GROUP BY ROLLUP(col1, col2)` to automatically include subtotals and grand totals. SQLite doesn't support ROLLUP natively, but you can simulate it with UNION ALL:

```sql
SELECT dept, SUM(salary) FROM employees GROUP BY dept
UNION ALL
SELECT 'TOTAL', SUM(salary) FROM employees;
```
"""


def seed_module3(db: Session, course: Course) -> None:
    mod = _module(db, course, "Aggregate Functions and GROUP BY", 3,
                  "COUNT, SUM, AVG, MIN, MAX, GROUP BY, and HAVING.")

    _lesson(db, mod, "aggregate-functions",
            title="COUNT, SUM, AVG, MIN, MAX",
            lesson_type=LessonType.reading,
            content_md=M3_AGGREGATE,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "group-by-having",
            title="GROUP BY and HAVING",
            lesson_type=LessonType.reading,
            content_md=M3_GROUP_BY,
            duration_minutes=15,
            order_index=2)

    ex_lesson = _lesson(db, mod, "aggregation-exercises",
                        title="Aggregation Exercises",
                        lesson_type=LessonType.exercise,
                        content_md="Practice GROUP BY, HAVING, and aggregate functions.",
                        duration_minutes=25,
                        order_index=3)

    # ── Exercise 3.1: Sales Summary ──────────────────────────────
    e1 = _exercise(db, ex_lesson, "sql-sales-summary",
        title="Sales Summary by Salesperson",
        prompt_md=(
            "# Sales Summary by Salesperson\n\n"
            "Given a table of sales records, compute the **total sales amount** and **number of sales** "
            "for each salesperson. Output ordered by total sales **descending**.\n\n"
            "**Input format:** lines of `salesperson,product,amount,quarter`\n\n"
            "**Output format:** `salesperson: total_sales count` "
            "(total rounded to 2 decimal places, count is integer)\n\n"
            "**Example**\n"
            "```\nInput:\nAlice,Widget,100.0,Q1\nBob,Gadget,200.0,Q1\nAlice,Doohickey,150.0,Q2\n\n"
            "Output:\nBob: 200.0 1\nAlice: 250.0 2\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('''\n"
                "    CREATE TABLE sales (\n"
                "        salesperson TEXT,\n"
                "        product TEXT,\n"
                "        amount REAL,\n"
                "        quarter TEXT\n"
                "    )\n"
                "''')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO sales VALUES (?, ?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2]), parts[3]))\n"
                "conn.commit()\n\n"
                "# TODO: GROUP BY salesperson, SUM(amount), COUNT(*)\n"
                "# ORDER BY total DESC\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('''\n"
                "    CREATE TABLE sales (\n"
                "        salesperson TEXT, product TEXT, amount REAL, quarter TEXT\n"
                "    )\n"
                "''')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO sales VALUES (?, ?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2]), parts[3]))\n"
                "conn.commit()\n\n"
                "cur.execute('''\n"
                "    SELECT salesperson, ROUND(SUM(amount), 2) AS total, COUNT(*) AS cnt\n"
                "    FROM sales\n"
                "    GROUP BY salesperson\n"
                "    ORDER BY total DESC\n"
                "''')\n"
                "for sp, total, cnt in cur.fetchall():\n"
                "    t = int(total) if total == int(total) else total\n"
                "    print(f'{sp}: {t} {cnt}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, e1, [
        ("Alice,Widget,100.0,Q1\nBob,Gadget,200.0,Q1\nAlice,Doohickey,150.0,Q2\n",
         "Bob: 200.0 1\nAlice: 250.0 2", False),
        ("Eve,A,300.0,Q1\nEve,B,100.0,Q2\nFrank,C,500.0,Q1\n",
         "Frank: 500.0 1\nEve: 400.0 2", False),
        ("Alice,X,50.0,Q1\nAlice,Y,50.0,Q2\nAlice,Z,50.0,Q3\n",
         "Alice: 150.0 3", True),
        ("A,p,10.0,Q1\nB,p,20.0,Q1\nC,p,30.0,Q1\nD,p,40.0,Q1\n",
         "D: 40.0 1\nC: 30.0 1\nB: 20.0 1\nA: 10.0 1", True),
        ("X,a,100.5,Q1\nY,b,200.75,Q1\nX,c,99.5,Q2\nZ,d,50.0,Q1\n",
         "Y: 200.75 1\nX: 200.0 2\nZ: 50.0 1", True),
    ])

    # ── Exercise 3.2: Category Stats ─────────────────────────────
    e2 = _exercise(db, ex_lesson, "sql-category-stats",
        title="Category Statistics with HAVING",
        prompt_md=(
            "# Category Statistics with HAVING\n\n"
            "For each product category that has **more than K items**, "
            "output the category name, average price (rounded to 2 decimals), "
            "minimum price, and maximum price. "
            "Order results by average price **descending**.\n\n"
            "**Input format:**\n"
            "- First line: integer K (minimum items threshold)\n"
            "- Remaining lines: `name,category,price`\n\n"
            "**Output format:** `category avg_price min_price max_price` (space-separated)\n\n"
            "**Example**\n"
            "```\nInput:\n1\nA,Tools,10.0\nB,Tools,20.0\nC,Books,5.0\n\n"
            "Output:\nTools 15.0 10.0 20.0\nBooks 5.0 5.0 5.0\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "k = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE products (name TEXT, category TEXT, price REAL)')\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO products VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "# TODO: GROUP BY category, HAVING COUNT(*) > k\n"
                "# SELECT category, ROUND(AVG(price),2), MIN(price), MAX(price)\n"
                "# ORDER BY avg_price DESC\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "k = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE products (name TEXT, category TEXT, price REAL)')\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO products VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "cur.execute('''\n"
                "    SELECT category,\n"
                "           ROUND(AVG(price), 2) AS avg_p,\n"
                "           MIN(price)            AS min_p,\n"
                "           MAX(price)            AS max_p\n"
                "    FROM   products\n"
                "    GROUP  BY category\n"
                "    HAVING COUNT(*) > ?\n"
                "    ORDER  BY avg_p DESC\n"
                "''', (k,))\n"
                "for cat, avg_p, min_p, max_p in cur.fetchall():\n"
                "    def fmt(v): return int(v) if v == int(v) else v\n"
                "    print(f'{cat} {fmt(avg_p)} {fmt(min_p)} {fmt(max_p)}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, e2, [
        ("1\nA,Tools,10.0\nB,Tools,20.0\nC,Books,5.0\n",
         "Tools 15.0 10.0 20.0\nBooks 5.0 5.0 5.0", False),
        ("2\nA,X,10\nB,X,20\nC,X,30\nD,Y,5\nE,Y,15\n",
         "X 20.0 10 30\nY 10.0 5 15", False),
        ("3\nA,Z,100\nB,Z,200\nC,Z,300\nD,Z,400\nE,W,50\n",
         "Z 250.0 100 400", True),
        ("0\nA,A,1\nB,B,2\n",
         "B 2 2 2\nA 1 1 1", True),
        ("2\nA,Alpha,10\nB,Alpha,30\nC,Beta,20\nD,Beta,40\nE,Beta,60\n",
         "Beta 40.0 20 60\nAlpha 20.0 10 30", True),
    ])


# ════════════════════════════════════════════════════════════════
# MODULE 4 — JOINs
# ════════════════════════════════════════════════════════════════

M4_JOIN_TYPES = """\
# Understanding JOINs

A `JOIN` combines rows from two or more tables based on a related column. JOINs are the heart of relational databases — they are how you reconstruct normalized data into useful result sets.

## Visual Overview (ASCII Venn Diagrams)

```
INNER JOIN         LEFT JOIN          FULL OUTER JOIN
  A ∩ B             A ∪ (A ∩ B)         A ∪ B
  ┌──┐              ┌──┐                ┌──┐
  │  ██│            │██████│            │██████│
  └──┘              └──┘                └──┘
```

## Sample Tables

```sql
CREATE TABLE customers (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product     TEXT,
    amount      REAL
);

-- customers: Alice(1), Bob(2), Carol(3)
-- orders: order for Alice(x2), order for Bob(x1), order for unknown customer(x1)
```

## INNER JOIN

Returns only rows where the join condition matches in **both** tables.

```sql
SELECT c.name, o.product, o.amount
FROM   customers c
INNER  JOIN orders o ON c.id = o.customer_id;
-- Result: Alice+order1, Alice+order2, Bob+order3
-- Carol is excluded (no orders); orphan order is excluded (no matching customer)
```

## LEFT JOIN (LEFT OUTER JOIN)

Returns **all rows from the left table** plus matching rows from the right table. Non-matching right-table columns are NULL.

```sql
SELECT c.name, o.product, o.amount
FROM   customers c
LEFT   JOIN orders o ON c.id = o.customer_id;
-- Result: Alice+order1, Alice+order2, Bob+order3, Carol+NULL+NULL
-- Carol appears with NULLs; orphan order still excluded
```

## RIGHT JOIN

SQLite does not support RIGHT JOIN natively. Swap the tables and use LEFT JOIN:

```sql
-- "RIGHT JOIN" simulation in SQLite:
SELECT c.name, o.product
FROM   orders o
LEFT   JOIN customers c ON c.id = o.customer_id;
```

## FULL OUTER JOIN

Returns all rows from both tables. SQLite doesn't support FULL OUTER JOIN directly — simulate with UNION:

```sql
SELECT c.name, o.product FROM customers c LEFT  JOIN orders o ON c.id = o.customer_id
UNION
SELECT c.name, o.product FROM orders o    LEFT  JOIN customers c ON c.id = o.customer_id;
```

## CROSS JOIN

Returns the Cartesian product — every combination of rows from both tables:

```sql
SELECT c.name, p.name AS product
FROM   customers c
CROSS  JOIN products p;
-- If 3 customers and 4 products → 12 rows
```

## ON vs USING

```sql
-- ON: explicit column comparison
SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id;

-- USING: when column names are identical in both tables
SELECT * FROM orders o JOIN customers c USING (customer_id);
```

## Self-Joins

Join a table to itself — useful for hierarchical data:

```sql
-- Find each employee and their manager
SELECT e.name AS employee, m.name AS manager
FROM   employees e
LEFT   JOIN employees m ON e.manager_id = m.id;
```

## "No Match" Behavior Summary

| Join Type | Left unmatched | Right unmatched |
|---|---|---|
| INNER | excluded | excluded |
| LEFT | included (NULLs on right) | excluded |
| RIGHT | excluded | included (NULLs on left) |
| FULL OUTER | included (NULLs on right) | included (NULLs on left) |
| CROSS | — | — (all combinations) |

The most common JOIN in practice is LEFT JOIN — it lets you include all records from the primary table even when no related record exists.
"""

M4_MULTI_JOIN = """\
# Multi-table JOINs and Aliases

Real queries often join three or more tables. Understanding how to chain JOINs and use table aliases cleanly is essential for readable, maintainable SQL.

## Three-Table JOIN Example

```sql
-- Schema
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER);
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE enrollments (student_id INTEGER, course_id INTEGER, grade TEXT);
CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, dept_id INTEGER);

-- Query: student name, course title, grade
SELECT s.name    AS student,
       c.title   AS course,
       e.grade
FROM   students   s
JOIN   enrollments e ON s.id = e.student_id
JOIN   courses     c ON e.course_id = c.id
ORDER  BY s.name, c.title;
```

## Table Aliases

Aliases (`AS t` or just `t`) make queries shorter and resolve ambiguity when the same column name exists in multiple tables:

```sql
-- Without aliases — verbose and ambiguous
SELECT employees.name, departments.name
FROM employees JOIN departments ON employees.dept_id = departments.id;

-- With aliases — clean
SELECT e.name AS emp_name, d.name AS dept_name
FROM   employees e JOIN departments d ON e.dept_id = d.id;
```

## Join Order and the Optimizer

The logical order in which you write JOINs doesn't affect correctness — the query optimizer reorders joins for efficiency. However, for readability, follow the natural "story" of the data:

1. Start with your primary/driving table
2. JOIN to related tables in dependency order
3. Use LEFT JOIN for optional relationships (may have no matching row)

## Many-to-Many Pattern

```sql
-- Tags for articles (M:N via article_tags junction table)
SELECT a.title, t.name AS tag
FROM   articles      a
JOIN   article_tags  at ON a.id = at.article_id
JOIN   tags          t  ON at.tag_id = t.id
ORDER  BY a.title, t.name;
```

## Practical Reporting Pattern

```sql
-- Revenue report: customer, total orders, total spent
SELECT
    c.name                        AS customer,
    COUNT(o.id)                   AS num_orders,
    COALESCE(SUM(o.amount), 0)    AS total_spent
FROM      customers c
LEFT JOIN orders    o ON c.id = o.customer_id
GROUP BY  c.id, c.name
ORDER BY  total_spent DESC;
```

The `COALESCE(SUM(o.amount), 0)` handles customers with no orders — SUM of zero rows returns NULL, which COALESCE converts to 0.

## Filtering JOIN Results

Apply `WHERE` after joins, or use join conditions to filter:

```sql
-- Only orders from customers in 'New York'
SELECT c.name, o.product, o.amount
FROM   customers c
JOIN   orders    o ON c.id = o.customer_id
WHERE  c.city = 'New York';
```

## Avoiding Duplicate Rows

When joining one-to-many, the "one" side row appears multiple times:

```sql
-- customer appears once per order (expected for LEFT JOIN)
-- Use DISTINCT or GROUP BY if you only want unique customers
SELECT DISTINCT c.name
FROM   customers c
JOIN   orders    o ON c.id = o.customer_id
WHERE  o.amount > 100;
```
"""


def seed_module4(db: Session, course: Course) -> None:
    mod = _module(db, course, "JOINs", 4,
                  "INNER, LEFT, CROSS joins, multi-table queries, and table aliases.")

    _lesson(db, mod, "join-types",
            title="Understanding JOINs",
            lesson_type=LessonType.reading,
            content_md=M4_JOIN_TYPES,
            duration_minutes=20,
            order_index=1)

    _lesson(db, mod, "multi-table-joins",
            title="Multi-table JOINs and Aliases",
            lesson_type=LessonType.reading,
            content_md=M4_MULTI_JOIN,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "join-exercises",
                        title="JOIN Exercises",
                        lesson_type=LessonType.exercise,
                        content_md="Practice INNER JOIN, LEFT JOIN, and multi-table queries.",
                        duration_minutes=30,
                        order_index=3)

    # ── Exercise 4.1: Customer Orders (LEFT JOIN) ────────────────
    e1 = _exercise(db, ex_lesson, "sql-customer-orders",
        title="Customer Order Totals",
        prompt_md=(
            "# Customer Order Totals\n\n"
            "Given customers and orders tables, find each customer's **total order amount**. "
            "Include customers who have placed **no orders** (show 0 for them). "
            "Order results by total amount **descending**, then by customer name **ascending** for ties.\n\n"
            "**Input format:**\n"
            "- Customer lines: `id,name,city` — until a line containing only `---`\n"
            "- Order lines: `id,customer_id,product,amount`\n\n"
            "**Output format:** `name: total` (total as integer if whole, else 2 decimal places)\n\n"
            "**Example**\n"
            "```\nInput:\n1,Alice,NYC\n2,Bob,LA\n3,Carol,NYC\n---\n1,1,Widget,100.0\n2,1,Gadget,50.0\n3,2,Doohickey,200.0\n\n"
            "Output:\nBob: 200.0\nAlice: 150.0\nCarol: 0\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)')\n"
                "cur.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, product TEXT, amount REAL)')\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "section = 'customers'\n"
                "for line in lines:\n"
                "    if line.strip() == '---': section = 'orders'; continue\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    if section == 'customers':\n"
                "        cur.execute('INSERT INTO customers VALUES (?, ?, ?)',\n"
                "                    (int(parts[0]), parts[1], parts[2]))\n"
                "    else:\n"
                "        cur.execute('INSERT INTO orders VALUES (?, ?, ?, ?)',\n"
                "                    (int(parts[0]), int(parts[1]), parts[2], float(parts[3])))\n"
                "conn.commit()\n\n"
                "# TODO: LEFT JOIN customers to orders, SUM(amount) per customer (COALESCE to 0),\n"
                "# ORDER BY total DESC, name ASC\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)')\n"
                "cur.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, product TEXT, amount REAL)')\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "section = 'customers'\n"
                "for line in lines:\n"
                "    if line.strip() == '---': section = 'orders'; continue\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    if section == 'customers':\n"
                "        cur.execute('INSERT INTO customers VALUES (?, ?, ?)',\n"
                "                    (int(parts[0]), parts[1], parts[2]))\n"
                "    else:\n"
                "        cur.execute('INSERT INTO orders VALUES (?, ?, ?, ?)',\n"
                "                    (int(parts[0]), int(parts[1]), parts[2], float(parts[3])))\n"
                "conn.commit()\n\n"
                "cur.execute('''\n"
                "    SELECT c.name, COALESCE(SUM(o.amount), 0) AS total\n"
                "    FROM   customers c\n"
                "    LEFT   JOIN orders o ON c.id = o.customer_id\n"
                "    GROUP  BY c.id, c.name\n"
                "    ORDER  BY total DESC, c.name ASC\n"
                "''')\n"
                "for name, total in cur.fetchall():\n"
                "    t = int(total) if total == int(total) else round(total, 2)\n"
                "    print(f'{name}: {t}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=20,
    )
    _cases(db, e1, [
        (
            "1,Alice,NYC\n2,Bob,LA\n3,Carol,NYC\n---\n1,1,Widget,100.0\n2,1,Gadget,50.0\n3,2,Doohickey,200.0\n",
            "Bob: 200.0\nAlice: 150.0\nCarol: 0", False
        ),
        (
            "1,Alice,A\n2,Bob,B\n---\n",
            "Alice: 0\nBob: 0", False
        ),
        (
            "1,Zara,X\n2,Amy,Y\n---\n1,1,A,500.0\n2,2,B,500.0\n",
            "Amy: 500.0\nZara: 500.0", True
        ),
        (
            "1,Alice,X\n2,Bob,X\n3,Carol,X\n---\n1,2,P,300.0\n2,2,Q,200.0\n3,3,R,100.0\n",
            "Bob: 500.0\nCarol: 100.0\nAlice: 0", True
        ),
        (
            "1,A,X\n2,B,X\n3,C,X\n4,D,X\n---\n1,1,x,10.0\n2,3,y,20.0\n3,3,z,30.0\n",
            "C: 50.0\nA: 10.0\nB: 0\nD: 0", True
        ),
    ])

    # ── Exercise 4.2: Employee Department Stats ──────────────────
    e2 = _exercise(db, ex_lesson, "sql-employee-department",
        title="Department Employee Stats",
        prompt_md=(
            "# Department Employee Stats\n\n"
            "Given employees and departments tables, find the **department name**, "
            "**number of employees**, and **average salary** for all departments whose "
            "budget is greater than a given threshold. Order by average salary **descending**.\n\n"
            "**Input format:**\n"
            "- First line: integer threshold\n"
            "- Department lines: `id,name,budget` until `---`\n"
            "- Employee lines: `id,name,dept_id,salary`\n\n"
            "**Output format:** `dept_name employee_count avg_salary` "
            "(avg rounded to 2 decimals, space-separated)\n\n"
            "**Example**\n"
            "```\nInput:\n50000\n1,Engineering,100000\n2,HR,40000\n---\n1,Alice,1,80000\n2,Bob,1,90000\n3,Carol,2,50000\n\n"
            "Output:\nEngineering 2 85000.0\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "threshold = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT, budget INTEGER)')\n"
                "cur.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER, salary INTEGER)')\n\n"
                "section = 'depts'\n"
                "for line in lines[1:]:\n"
                "    if line.strip() == '---': section = 'emps'; continue\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    if section == 'depts':\n"
                "        cur.execute('INSERT INTO departments VALUES (?, ?, ?)',\n"
                "                    (int(parts[0]), parts[1], int(parts[2])))\n"
                "    else:\n"
                "        cur.execute('INSERT INTO employees VALUES (?, ?, ?, ?)',\n"
                "                    (int(parts[0]), parts[1], int(parts[2]), int(parts[3])))\n"
                "conn.commit()\n\n"
                "# TODO: JOIN departments to employees, filter by budget > threshold,\n"
                "# GROUP BY dept, SELECT name, COUNT, AVG(salary), ORDER BY avg DESC\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "threshold = int(lines[0])\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT, budget INTEGER)')\n"
                "cur.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER, salary INTEGER)')\n\n"
                "section = 'depts'\n"
                "for line in lines[1:]:\n"
                "    if line.strip() == '---': section = 'emps'; continue\n"
                "    if not line.strip(): continue\n"
                "    parts = line.split(',')\n"
                "    if section == 'depts':\n"
                "        cur.execute('INSERT INTO departments VALUES (?, ?, ?)',\n"
                "                    (int(parts[0]), parts[1], int(parts[2])))\n"
                "    else:\n"
                "        cur.execute('INSERT INTO employees VALUES (?, ?, ?, ?)',\n"
                "                    (int(parts[0]), parts[1], int(parts[2]), int(parts[3])))\n"
                "conn.commit()\n\n"
                "cur.execute('''\n"
                "    SELECT d.name, COUNT(e.id) AS cnt, ROUND(AVG(e.salary), 2) AS avg_sal\n"
                "    FROM   departments d\n"
                "    JOIN   employees   e ON d.id = e.dept_id\n"
                "    WHERE  d.budget > ?\n"
                "    GROUP  BY d.id, d.name\n"
                "    ORDER  BY avg_sal DESC\n"
                "''', (threshold,))\n"
                "for dname, cnt, avg_sal in cur.fetchall():\n"
                "    a = int(avg_sal) if avg_sal == int(avg_sal) else avg_sal\n"
                "    print(f'{dname} {cnt} {a}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=20,
    )
    _cases(db, e2, [
        (
            "50000\n1,Engineering,100000\n2,HR,40000\n---\n1,Alice,1,80000\n2,Bob,1,90000\n3,Carol,2,50000\n",
            "Engineering 2 85000.0", False
        ),
        (
            "0\n1,Sales,10000\n2,IT,20000\n---\n1,A,1,30000\n2,B,2,60000\n3,C,2,40000\n",
            "IT 2 50000.0\nSales 1 30000.0", False
        ),
        (
            "100000\n1,BigDept,200000\n2,SmallDept,50000\n---\n1,A,1,100000\n2,B,1,120000\n3,C,2,80000\n",
            "BigDept 2 110000.0", True
        ),
        (
            "999999\n1,Rich,500000\n2,Poor,1000\n---\n1,A,1,200000\n2,B,2,50000\n",
            "", True
        ),
    ])


# ════════════════════════════════════════════════════════════════
# MODULE 5 — Subqueries and CTEs
# ════════════════════════════════════════════════════════════════

M5_SUBQUERIES = """\
# Subqueries

A **subquery** (also called an inner query or nested query) is a SELECT statement embedded inside another SQL statement. Subqueries let you break complex logic into composable pieces.

## Scalar Subqueries

A scalar subquery returns exactly **one row, one column**. It can appear anywhere an expression is valid:

```sql
-- Find products priced above the average
SELECT name, price
FROM   products
WHERE  price > (SELECT AVG(price) FROM products);

-- Use a scalar subquery in SELECT
SELECT name, price,
       price - (SELECT AVG(price) FROM products) AS diff_from_avg
FROM   products;
```

## Table Subqueries (Derived Tables)

A subquery in the `FROM` clause acts as a temporary table (alias required):

```sql
SELECT dept, avg_sal
FROM (
    SELECT dept, AVG(salary) AS avg_sal
    FROM   employees
    GROUP  BY dept
) AS dept_stats
WHERE avg_sal > 70000;
```

## Correlated Subqueries

A **correlated subquery** references columns from the outer query. It is re-evaluated for each outer row:

```sql
-- For each employee, find their rank in their department
SELECT e1.name, e1.dept, e1.salary,
       (SELECT COUNT(*) + 1
        FROM employees e2
        WHERE e2.dept = e1.dept AND e2.salary > e1.salary) AS rank_in_dept
FROM employees e1
ORDER BY e1.dept, rank_in_dept;
```

Correlated subqueries can be slow for large tables — consider window functions or JOINs instead.

## EXISTS / NOT EXISTS

`EXISTS` returns TRUE if the subquery produces at least one row:

```sql
-- Find customers who have placed at least one order
SELECT name FROM customers c
WHERE  EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- Find customers with NO orders
SELECT name FROM customers c
WHERE  NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

`EXISTS` is typically faster than `IN` for large subquery results because it short-circuits on the first match.

## IN with Subquery

```sql
-- Find employees in departments with budget > 100000
SELECT name FROM employees
WHERE  dept_id IN (SELECT id FROM departments WHERE budget > 100000);
```

## Subqueries in SELECT

```sql
SELECT
    name,
    salary,
    (SELECT name FROM departments WHERE id = e.dept_id) AS dept_name
FROM employees e;
```

## When to Use Subqueries vs JOINs

| Scenario | Prefer |
|---|---|
| Simple filtering based on aggregation | Subquery (clearer) |
| Retrieving columns from both tables | JOIN |
| EXISTS/NOT EXISTS pattern | Subquery |
| Large datasets with index support | JOIN (optimizer-friendly) |
| Readability over micro-optimization | CTE (next lesson) |
"""

M5_CTE = """\
# Common Table Expressions (CTEs)

A **Common Table Expression** (CTE) is a named temporary result set defined with the `WITH` clause. CTEs make complex queries dramatically more readable by giving names to intermediate results.

## Basic CTE Syntax

```sql
WITH cte_name AS (
    SELECT ...
    FROM   ...
    WHERE  ...
)
SELECT *
FROM   cte_name
WHERE  ...;
```

## Example: Above-Average Sales

```sql
WITH avg_sales AS (
    SELECT AVG(amount) AS avg_amt FROM sales
)
SELECT s.salesperson, s.amount
FROM   sales s, avg_sales
WHERE  s.amount > avg_sales.avg_amt
ORDER  BY s.amount DESC;
```

## Multiple CTEs

Chain multiple CTEs separated by commas:

```sql
WITH
dept_totals AS (
    SELECT dept_id, SUM(salary) AS total_salary
    FROM   employees
    GROUP  BY dept_id
),
dept_info AS (
    SELECT d.name, dt.total_salary
    FROM   departments d
    JOIN   dept_totals dt ON d.id = dt.dept_id
)
SELECT name, total_salary
FROM   dept_info
ORDER  BY total_salary DESC;
```

## Recursive CTEs

Recursive CTEs enable processing **hierarchical data** like org charts, file systems, or bill of materials:

```sql
-- Org chart: find all reports under manager with id=1
WITH RECURSIVE org AS (
    -- Base case: the manager themselves
    SELECT id, name, manager_id, 0 AS depth
    FROM   employees
    WHERE  id = 1

    UNION ALL

    -- Recursive case: each direct report
    SELECT e.id, e.name, e.manager_id, org.depth + 1
    FROM   employees e
    JOIN   org ON e.manager_id = org.id
)
SELECT name, depth FROM org ORDER BY depth, name;
```

The `UNION ALL` is the recursive step. The database repeats it until no new rows are produced.

## CTE vs Subquery: Readability

```sql
-- Hard to read: nested subqueries
SELECT * FROM (
    SELECT dept, AVG(salary) AS avg_sal FROM (
        SELECT * FROM employees WHERE active = 1
    ) GROUP BY dept
) WHERE avg_sal > 60000;

-- Easy to read: CTE equivalent
WITH active_emps AS (
    SELECT * FROM employees WHERE active = 1
),
dept_avgs AS (
    SELECT dept, AVG(salary) AS avg_sal FROM active_emps GROUP BY dept
)
SELECT * FROM dept_avgs WHERE avg_sal > 60000;
```

## CTE Materialization

In SQLite and PostgreSQL, CTEs can be **materialized** (computed once and stored) or **inlined** (expanded like a subquery). By default:

- **SQLite**: CTEs are not materialized (inlined by default since 3.35.0)
- **PostgreSQL**: CTEs are materialized (compute once, great for expensive subqueries)

Use `WITH ... AS MATERIALIZED (...)` or `AS NOT MATERIALIZED (...)` in PostgreSQL 12+ to control this explicitly.
"""


def seed_module5(db: Session, course: Course) -> None:
    mod = _module(db, course, "Subqueries and CTEs", 5,
                  "Scalar, correlated, and table subqueries; WITH clause and recursive CTEs.")

    _lesson(db, mod, "subqueries",
            title="Subqueries",
            lesson_type=LessonType.reading,
            content_md=M5_SUBQUERIES,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "common-table-expressions",
            title="Common Table Expressions (CTEs)",
            lesson_type=LessonType.reading,
            content_md=M5_CTE,
            duration_minutes=15,
            order_index=2)

    ex_lesson = _lesson(db, mod, "subquery-exercises",
                        title="Subquery and CTE Exercises",
                        lesson_type=LessonType.exercise,
                        content_md="Practice subqueries, EXISTS, and CTEs.",
                        duration_minutes=25,
                        order_index=3)

    # ── Exercise 5.1: Above-Average Salary ──────────────────────
    e1 = _exercise(db, ex_lesson, "sql-above-average-salary",
        title="Above Average Salary",
        prompt_md=(
            "# Above Average Salary\n\n"
            "Find all employees whose salary is **strictly above** the company-wide average salary. "
            "Output their names ordered by salary **descending**.\n\n"
            "**Input format:** lines of `name,department,salary`\n\n"
            "**Output format:** one employee name per line, highest salary first\n\n"
            "**Example**\n"
            "```\nInput:\nAlice,Eng,90000\nBob,HR,50000\nCarol,Eng,70000\n\n"
            "Output:\nAlice\nCarol\n```\n\n"
            "*(Average is (90000+50000+70000)/3 = 70000; Carol ties the average so she is NOT included — "
            "use strictly greater than.)*\n\n"
            "Use a subquery or CTE to compute the average first."
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE employees (name TEXT, department TEXT, salary REAL)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO employees VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "# TODO: Use a subquery or CTE to find employees with salary > AVG(salary)\n"
                "# Print names ordered by salary DESC\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE employees (name TEXT, department TEXT, salary REAL)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO employees VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], float(parts[2])))\n"
                "conn.commit()\n\n"
                "cur.execute('''\n"
                "    WITH avg_sal AS (SELECT AVG(salary) AS avg FROM employees)\n"
                "    SELECT name FROM employees, avg_sal\n"
                "    WHERE  salary > avg_sal.avg\n"
                "    ORDER  BY salary DESC\n"
                "''')\n"
                "for (name,) in cur.fetchall():\n"
                "    print(name)\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, e1, [
        ("Alice,Eng,90000\nBob,HR,50000\nCarol,Eng,70000\n",
         "Alice", False),
        ("Alice,A,100\nBob,B,200\nCarol,C,300\nDave,D,400\n",
         "Dave\nCarol\nBob", False),
        ("Solo,X,50000\n",
         "", True),
        ("A,X,100\nB,X,100\nC,X,100\n",
         "", True),
        ("A,X,80000\nB,X,90000\nC,X,70000\nD,X,60000\nE,X,100000\n",
         "E\nB\nA", True),
    ])

    # ── Exercise 5.2: Rank Within Department ────────────────────
    e2 = _exercise(db, ex_lesson, "sql-rank-within-dept",
        title="Rank Employees Within Department",
        prompt_md=(
            "# Rank Employees Within Department\n\n"
            "Using a CTE, rank each employee within their department by salary "
            "(rank 1 = highest salary in that department). "
            "If two employees have the same salary in the same department, assign them the same rank "
            "and skip the next rank (standard competition ranking).\n\n"
            "**Input format:** lines of `name,department,salary`\n\n"
            "**Output format:** `department name salary rank` (space-separated), "
            "ordered by department ASC, rank ASC, name ASC\n\n"
            "**Example**\n"
            "```\nInput:\nAlice,Eng,90000\nBob,Eng,70000\nCarol,HR,60000\nDave,HR,60000\n\n"
            "Output:\nEng Alice 90000 1\nEng Bob 70000 2\nHR Carol 60000 1\nHR Dave 60000 1\n```"
        ),
        difficulty=Difficulty.hard,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE employees (name TEXT, department TEXT, salary INTEGER)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO employees VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], int(parts[2])))\n"
                "conn.commit()\n\n"
                "# TODO: For each employee, compute rank = count of employees in same dept\n"
                "# with strictly higher salary + 1. Use a CTE or correlated subquery.\n"
                "# Output: dept name salary rank, ordered by dept ASC, rank ASC, name ASC\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE employees (name TEXT, department TEXT, salary INTEGER)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split(',')\n"
                "    cur.execute('INSERT INTO employees VALUES (?, ?, ?)',\n"
                "                (parts[0], parts[1], int(parts[2])))\n"
                "conn.commit()\n\n"
                "cur.execute('''\n"
                "    WITH ranked AS (\n"
                "        SELECT e1.name, e1.department, e1.salary,\n"
                "               (SELECT COUNT(*) + 1\n"
                "                FROM employees e2\n"
                "                WHERE e2.department = e1.department\n"
                "                  AND e2.salary > e1.salary) AS rnk\n"
                "        FROM employees e1\n"
                "    )\n"
                "    SELECT department, name, salary, rnk\n"
                "    FROM   ranked\n"
                "    ORDER  BY department ASC, rnk ASC, name ASC\n"
                "''')\n"
                "for dept, name, salary, rnk in cur.fetchall():\n"
                "    print(f'{dept} {name} {salary} {rnk}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=25,
    )
    _cases(db, e2, [
        ("Alice,Eng,90000\nBob,Eng,70000\nCarol,HR,60000\nDave,HR,60000\n",
         "Eng Alice 90000 1\nEng Bob 70000 2\nHR Carol 60000 1\nHR Dave 60000 1", False),
        ("Alice,A,100\nBob,A,200\nCarol,A,150\n",
         "A Bob 200 1\nA Carol 150 2\nA Alice 100 3", False),
        ("Solo,X,50000\n",
         "X Solo 50000 1", True),
        ("A,Dept1,100\nB,Dept1,200\nC,Dept2,300\nD,Dept2,300\nE,Dept2,100\n",
         "Dept1 B 200 1\nDept1 A 100 2\nDept2 C 300 1\nDept2 D 300 1\nDept2 E 100 3", True),
    ])


# ════════════════════════════════════════════════════════════════
# MODULE 6 — Data Manipulation: INSERT, UPDATE, DELETE
# ════════════════════════════════════════════════════════════════

M6_DML = """\
# Modifying Data

SQL's **Data Manipulation Language (DML)** covers the three statements that change the contents of tables: `INSERT`, `UPDATE`, and `DELETE`. Mastering safe DML is critical — mistakes without transactions can be hard or impossible to reverse.

## INSERT

### Single-row INSERT
```sql
INSERT INTO products (name, category, price, stock)
VALUES ('Keyboard', 'Electronics', 79.99, 50);
```

### Multi-row INSERT (SQL standard, supported by SQLite 3.7.11+)
```sql
INSERT INTO products (name, category, price, stock) VALUES
    ('Mouse',   'Electronics', 29.99, 100),
    ('Monitor', 'Electronics', 349.99, 20),
    ('Desk',    'Furniture',   199.99, 15);
```

### INSERT INTO ... SELECT (copy data between tables)
```sql
INSERT INTO product_archive (name, price)
SELECT name, price FROM products WHERE stock = 0;
```

### UPSERT — INSERT OR REPLACE (SQLite)
```sql
-- If a row with the same PRIMARY KEY exists, replace it
INSERT OR REPLACE INTO products (id, name, price, stock)
VALUES (5, 'Widget v2', 12.99, 200);

-- ON CONFLICT DO UPDATE (SQLite 3.24+, PostgreSQL-compatible)
INSERT INTO products (id, name, price)
VALUES (5, 'Widget v2', 12.99)
ON CONFLICT(id) DO UPDATE SET price = excluded.price;
```

## UPDATE

```sql
-- Increase all Electronics prices by 10%
UPDATE products
SET    price = price * 1.1
WHERE  category = 'Electronics';

-- Update multiple columns at once
UPDATE employees
SET    salary = salary * 1.05,
       title  = 'Senior ' || title
WHERE  years_experience >= 5;
```

**Warning:** An `UPDATE` without a `WHERE` clause modifies **every row** in the table. Always double-check your WHERE condition (run a SELECT first).

## DELETE

```sql
-- Remove out-of-stock products
DELETE FROM products WHERE stock = 0;

-- Remove all rows (table structure remains)
DELETE FROM products;
```

**TRUNCATE vs DELETE:** SQLite doesn't have TRUNCATE. `DELETE FROM table` without WHERE deletes all rows and is similar — but it logs each deletion. For large tables on other databases, `TRUNCATE` is faster (not logged per-row).

## Soft Delete Pattern

Instead of hard-deleting rows (making them unrecoverable), many production systems use a `deleted_at` timestamp:

```sql
ALTER TABLE products ADD COLUMN deleted_at TEXT;  -- NULL = active

-- "Delete" a product (soft)
UPDATE products SET deleted_at = datetime('now') WHERE id = 42;

-- Query only active products
SELECT * FROM products WHERE deleted_at IS NULL;
```

## RETURNING Clause (SQLite 3.35+)

Retrieve the values of modified rows:

```sql
INSERT INTO orders (customer_id, product, amount)
VALUES (1, 'Widget', 29.99)
RETURNING id, amount;
```
"""

M6_TRANSACTIONS = """\
# Transactions and ACID

A **transaction** is a sequence of SQL statements executed as a single atomic unit. Either all statements succeed (COMMIT), or none of them take effect (ROLLBACK).

## BEGIN / COMMIT / ROLLBACK

```sql
BEGIN;

UPDATE accounts SET balance = balance - 500 WHERE id = 1;   -- debit
UPDATE accounts SET balance = balance + 500 WHERE id = 2;   -- credit

-- Check: did both updates succeed?
COMMIT;   -- make permanent

-- Or, if something went wrong:
-- ROLLBACK;  -- undo everything since BEGIN
```

Without a transaction, if the server crashes between the two UPDATEs, one account loses $500 but the other never gains it — money disappears. Transactions prevent this.

## Autocommit

In SQLite's Python module, every statement is automatically wrapped in an implicit transaction unless you use `with conn:` or `conn.commit()` explicitly:

```python
import sqlite3
conn = sqlite3.connect('bank.db')

# Python sqlite3: explicit transaction
conn.execute('BEGIN')
try:
    conn.execute("UPDATE accounts SET balance = balance - 500 WHERE id = 1")
    conn.execute("UPDATE accounts SET balance = balance + 500 WHERE id = 2")
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

Or use the context manager:

```python
with conn:   # auto-commits on success, auto-rolls back on exception
    conn.execute("UPDATE accounts SET balance = balance - 500 WHERE id = 1")
    conn.execute("UPDATE accounts SET balance = balance + 500 WHERE id = 2")
```

## Savepoints

Savepoints let you partially roll back within a transaction:

```sql
BEGIN;
INSERT INTO orders VALUES (1, 'Widget', 50);
SAVEPOINT sp1;
INSERT INTO orders VALUES (2, 'Gadget', 100);  -- oops, wrong product
ROLLBACK TO sp1;    -- undo only the second insert
INSERT INTO orders VALUES (2, 'Doohickey', 100);
COMMIT;
```

## Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| READ UNCOMMITTED | Possible | Possible | Possible |
| READ COMMITTED | No | Possible | Possible |
| REPEATABLE READ | No | No | Possible |
| SERIALIZABLE | No | No | No |

- **Dirty read**: seeing uncommitted changes from another transaction
- **Non-repeatable read**: re-reading a row and getting different values
- **Phantom read**: re-running a range query and getting different rows

SQLite uses **serialized** access by default — only one writer at a time, so isolation issues are less common than in multi-user databases.

## Why Transactions Matter

1. **Atomicity**: partial updates never persist
2. **Consistency**: constraints are checked at COMMIT time
3. **Isolation**: concurrent transactions don't interfere
4. **Durability**: committed data survives crashes (written to the WAL/journal)

Always wrap multi-statement operations (transfers, order processing, batch imports) in explicit transactions for both safety and performance — a transaction with 1000 inserts is *much* faster than 1000 individual autocommit inserts.
"""


def seed_module6(db: Session, course: Course) -> None:
    mod = _module(db, course, "Data Manipulation — INSERT, UPDATE, DELETE", 6,
                  "INSERT/UPDATE/DELETE, UPSERT, soft deletes, and transactions.")

    _lesson(db, mod, "insert-update-delete",
            title="Modifying Data",
            lesson_type=LessonType.reading,
            content_md=M6_DML,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "transactions",
            title="Transactions and ACID",
            lesson_type=LessonType.reading,
            content_md=M6_TRANSACTIONS,
            duration_minutes=10,
            order_index=2)

    ex_lesson = _lesson(db, mod, "dml-exercises",
                        title="DML Exercises",
                        lesson_type=LessonType.exercise,
                        content_md="Practice INSERT, UPDATE, DELETE with real-world inventory scenarios.",
                        duration_minutes=25,
                        order_index=3)

    # ── Exercise 6.1: Inventory Update ──────────────────────────
    e1 = _exercise(db, ex_lesson, "sql-inventory-update",
        title="Inventory Command Processor",
        prompt_md=(
            "# Inventory Command Processor\n\n"
            "Process a series of inventory commands on a products table and output the final state.\n\n"
            "**Input format:**\n"
            "- Stock lines: `product_name,initial_stock` until `---`\n"
            "- Command lines (one of):\n"
            "  - `RESTOCK product qty` — increase stock by qty\n"
            "  - `SELL product qty` — decrease stock by qty (stock cannot go below 0)\n"
            "  - `REMOVE product` — delete the product entirely\n\n"
            "**Output format:** `product: stock` lines for surviving products, "
            "ordered alphabetically by product name\n\n"
            "**Example**\n"
            "```\nInput:\nApple,100\nBanana,50\n---\nRESTOCK Apple 20\nSELL Banana 30\nREMOVE Apple\n\n"
            "Output:\nBanana: 20\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE inventory (product TEXT PRIMARY KEY, stock INTEGER NOT NULL)')\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "section = 'stock'\n"
                "for line in lines:\n"
                "    if line.strip() == '---': section = 'cmds'; continue\n"
                "    if not line.strip(): continue\n"
                "    if section == 'stock':\n"
                "        parts = line.split(',')\n"
                "        cur.execute('INSERT INTO inventory VALUES (?, ?)', (parts[0], int(parts[1])))\n"
                "    else:\n"
                "        parts = line.split()\n"
                "        cmd = parts[0]\n"
                "        # TODO: handle RESTOCK, SELL, REMOVE commands using UPDATE/DELETE\n"
                "conn.commit()\n\n"
                "# TODO: SELECT product, stock ORDER BY product, print 'product: stock'\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE inventory (product TEXT PRIMARY KEY, stock INTEGER NOT NULL)')\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "section = 'stock'\n"
                "for line in lines:\n"
                "    if line.strip() == '---': section = 'cmds'; continue\n"
                "    if not line.strip(): continue\n"
                "    if section == 'stock':\n"
                "        parts = line.split(',')\n"
                "        cur.execute('INSERT INTO inventory VALUES (?, ?)', (parts[0], int(parts[1])))\n"
                "    else:\n"
                "        parts = line.split()\n"
                "        cmd = parts[0]\n"
                "        if cmd == 'RESTOCK':\n"
                "            cur.execute('UPDATE inventory SET stock = stock + ? WHERE product = ?',\n"
                "                        (int(parts[2]), parts[1]))\n"
                "        elif cmd == 'SELL':\n"
                "            cur.execute('UPDATE inventory SET stock = MAX(0, stock - ?) WHERE product = ?',\n"
                "                        (int(parts[2]), parts[1]))\n"
                "        elif cmd == 'REMOVE':\n"
                "            cur.execute('DELETE FROM inventory WHERE product = ?', (parts[1],))\n"
                "conn.commit()\n\n"
                "cur.execute('SELECT product, stock FROM inventory ORDER BY product')\n"
                "for product, stock in cur.fetchall():\n"
                "    print(f'{product}: {stock}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, e1, [
        ("Apple,100\nBanana,50\n---\nRESTOCK Apple 20\nSELL Banana 30\nREMOVE Apple\n",
         "Banana: 20", False),
        ("Widget,10\nGadget,20\n---\nSELL Widget 5\nRESTOCK Gadget 10\n",
         "Gadget: 30\nWidget: 5", False),
        ("A,5\nB,5\n---\nSELL A 10\nSELL B 3\n",
         "A: 0\nB: 2", True),
        ("X,100\nY,50\nZ,75\n---\nREMOVE Y\nRESTOCK X 50\nSELL Z 25\n",
         "X: 150\nZ: 50", True),
        ("Alpha,1\nBeta,1\nGamma,1\n---\nREMOVE Alpha\nREMOVE Beta\nREMOVE Gamma\n",
         "", True),
    ])

    # ── Exercise 6.2: Batch Insert and Query ────────────────────
    e2 = _exercise(db, ex_lesson, "sql-batch-insert-query",
        title="Student Records Batch Processor",
        prompt_md=(
            "# Student Records Batch Processor\n\n"
            "Process student record commands and answer queries.\n\n"
            "**Commands:**\n"
            "- `ADD name grade score` — insert a student record\n"
            "- `QUERY_GRADE grade` — print names of students with that grade, sorted alphabetically\n"
            "- `QUERY_MIN_SCORE threshold` — print names of students with score >= threshold, sorted by score DESC then name ASC\n"
            "- `STATS` — print `count avg_score` where avg_score is rounded to 2 decimal places\n\n"
            "**Example**\n"
            "```\nInput:\nADD Alice A 95\nADD Bob B 75\nADD Carol A 88\nQUERY_GRADE A\nSTATS\n\n"
            "Output:\nAlice\nCarol\n3 86.0\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE students (name TEXT, grade TEXT, score INTEGER)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split()\n"
                "    cmd = parts[0]\n"
                "    # TODO: handle ADD, QUERY_GRADE, QUERY_MIN_SCORE, STATS\n"
                "conn.close()\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE students (name TEXT, grade TEXT, score INTEGER)')\n\n"
                "for line in sys.stdin:\n"
                "    line = line.strip()\n"
                "    if not line: continue\n"
                "    parts = line.split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'ADD':\n"
                "        name, grade, score = parts[1], parts[2], int(parts[3])\n"
                "        cur.execute('INSERT INTO students VALUES (?, ?, ?)', (name, grade, score))\n"
                "    elif cmd == 'QUERY_GRADE':\n"
                "        cur.execute('SELECT name FROM students WHERE grade = ? ORDER BY name', (parts[1],))\n"
                "        for (n,) in cur.fetchall(): print(n)\n"
                "    elif cmd == 'QUERY_MIN_SCORE':\n"
                "        threshold = int(parts[1])\n"
                "        cur.execute('SELECT name FROM students WHERE score >= ? ORDER BY score DESC, name ASC', (threshold,))\n"
                "        for (n,) in cur.fetchall(): print(n)\n"
                "    elif cmd == 'STATS':\n"
                "        cur.execute('SELECT COUNT(*), ROUND(AVG(score), 2) FROM students')\n"
                "        cnt, avg = cur.fetchone()\n"
                "        a = int(avg) if avg == int(avg) else avg\n"
                "        print(f'{cnt} {a}')\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, e2, [
        ("ADD Alice A 95\nADD Bob B 75\nADD Carol A 88\nQUERY_GRADE A\nSTATS\n",
         "Alice\nCarol\n3 86.0", False),
        ("ADD Dave C 60\nADD Eve B 80\nQUERY_MIN_SCORE 70\nSTATS\n",
         "Eve\n2 70.0", False),
        ("ADD A X 100\nADD B X 90\nADD C Y 80\nQUERY_GRADE X\nQUERY_GRADE Y\n",
         "A\nB\nC", True),
        ("ADD A A 50\nADD B B 60\nADD C A 70\nQUERY_MIN_SCORE 55\nSTATS\n",
         "C\nB\n3 60.0", True),
    ])


# ════════════════════════════════════════════════════════════════
# MODULE 7 — Indexes, Views, and Optimization
# ════════════════════════════════════════════════════════════════

M7_INDEXES = """\
# Indexes and Query Performance

An **index** is a separate data structure that the database maintains alongside a table to speed up data retrieval. Without indexes, every query must scan every row — a **full table scan** — which becomes unacceptably slow as tables grow.

## How B-tree Indexes Work

The most common index type is a **B-tree** (balanced tree). Think of it as the index at the back of a textbook:

- Keys are sorted, enabling binary search: O(log n) instead of O(n)
- Leaf nodes contain the key value and a pointer to the actual row
- Insert/update/delete are slightly slower because the index must stay synchronized

```sql
-- Create an index
CREATE INDEX idx_products_category ON products(category);

-- Create a unique index (also enforces uniqueness constraint)
CREATE UNIQUE INDEX idx_employees_email ON employees(email);

-- Drop an index
DROP INDEX IF EXISTS idx_products_category;
```

## When the Optimizer Uses an Index

The query optimizer chooses an index when:

1. The indexed column appears in a `WHERE` clause with `=`, `<`, `>`, `BETWEEN`, or `IN`
2. The indexed column appears in `ORDER BY` (avoids a sort step)
3. The indexed column appears in a `JOIN` condition
4. The index **selectivity** is high (few matching rows vs total rows)

```sql
-- Uses idx_products_category (equality check)
SELECT * FROM products WHERE category = 'Electronics';

-- Uses index for sort
SELECT * FROM products ORDER BY category;

-- LIKE with leading wildcard — cannot use index!
SELECT * FROM products WHERE category LIKE '%Electronics%';
```

## Composite Indexes and Column Order

A **composite index** covers multiple columns. Column order matters:

```sql
CREATE INDEX idx_emp_dept_salary ON employees(dept, salary);

-- Uses the index (leftmost prefix rule)
SELECT * FROM employees WHERE dept = 'Engineering';
SELECT * FROM employees WHERE dept = 'Engineering' AND salary > 80000;

-- Cannot use this index efficiently (dept is not in WHERE)
SELECT * FROM employees WHERE salary > 80000;
```

The rule: the index is usable if the query filters on a **prefix** of the indexed columns.

## Covering Indexes

A **covering index** includes all columns the query needs — the database never touches the main table:

```sql
-- This index covers the query below
CREATE INDEX idx_prod_cat_price ON products(category, price, name);

SELECT name, price FROM products WHERE category = 'Electronics' ORDER BY price;
-- All needed columns (name, price) are in the index → no table lookup
```

## EXPLAIN QUERY PLAN

Use SQLite's `EXPLAIN QUERY PLAN` to see how the optimizer executes a query:

```sql
EXPLAIN QUERY PLAN
SELECT name FROM products WHERE category = 'Electronics' AND price < 100;
```

Output shows whether it uses a `SCAN` (full scan) or `SEARCH` (index-based).

## When NOT to Index

- **Low-selectivity columns**: boolean flags, status fields (only 2-3 distinct values)
- **Small tables**: a full scan on 100 rows is faster than index overhead
- **Write-heavy tables**: every INSERT/UPDATE/DELETE must update all indexes
- **Rarely queried columns**: indexes consume disk space and memory

## Index Selectivity and Statistics

The optimizer uses statistics (maintained by `ANALYZE` in SQLite) to estimate row counts. Run `ANALYZE` after bulk imports:

```sql
ANALYZE;          -- update statistics for all tables
ANALYZE products; -- update for one table
```
"""

M7_VIEWS = """\
# Views, Triggers, and Virtual Tables

## Views

A **view** is a named, stored SELECT query. It looks like a table to queries but contains no data of its own — the underlying query runs each time the view is accessed.

```sql
-- Create a view
CREATE VIEW active_products AS
SELECT id, name, category, price
FROM   products
WHERE  deleted_at IS NULL;

-- Query a view exactly like a table
SELECT * FROM active_products WHERE category = 'Electronics';

-- Drop a view
DROP VIEW IF EXISTS active_products;
```

### Benefits of Views
- **Security**: expose only certain columns/rows to users
- **Simplicity**: hide complex JOINs behind a simple name
- **Consistency**: ensure all queries use the same business logic

### Updatable Views

Simple views (no GROUP BY, DISTINCT, JOINs, aggregates) are **updatable** in SQLite — INSERT/UPDATE/DELETE on the view propagates to the base table.

### WITH CHECK OPTION

```sql
CREATE VIEW cheap_products AS
SELECT * FROM products WHERE price < 50
WITH CHECK OPTION;  -- prevents inserting rows that don't satisfy price < 50
```

## Triggers

A **trigger** automatically executes SQL when a specified event (INSERT, UPDATE, DELETE) occurs on a table:

```sql
-- Maintain an updated_at timestamp automatically
CREATE TRIGGER update_product_timestamp
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    UPDATE products SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Audit log: record every DELETE
CREATE TRIGGER log_product_delete
BEFORE DELETE ON products
FOR EACH ROW
BEGIN
    INSERT INTO product_audit (product_id, name, deleted_at)
    VALUES (OLD.id, OLD.name, datetime('now'));
END;
```

Trigger variables:
- `NEW.column` — the new value (in INSERT/UPDATE)
- `OLD.column` — the old value (in UPDATE/DELETE)

## Virtual Tables — FTS5

SQLite's **FTS5** (Full-Text Search 5) virtual table enables fast text searching:

```sql
-- Create a full-text search index
CREATE VIRTUAL TABLE products_fts USING fts5(name, description);

-- Populate it
INSERT INTO products_fts SELECT name, description FROM products;

-- Fast full-text search (much faster than LIKE '%term%')
SELECT * FROM products_fts WHERE products_fts MATCH 'wireless keyboard';
```

FTS5 supports phrase queries, prefix queries (`keyb*`), boolean operators (AND, OR, NOT), and BM25 relevance ranking.

## Materialized Views (Concept)

SQLite doesn't support materialized views natively, but the pattern can be simulated:

```sql
-- A "materialized view" is just a regular table refreshed manually
CREATE TABLE product_category_stats AS
SELECT category, COUNT(*) AS cnt, AVG(price) AS avg_price
FROM   products GROUP BY category;

-- Refresh it periodically
DELETE FROM product_category_stats;
INSERT INTO product_category_stats
SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category;
```

True materialized views (PostgreSQL) are refreshed with `REFRESH MATERIALIZED VIEW`.
"""


def seed_module7(db: Session, course: Course) -> None:
    mod = _module(db, course, "Indexes, Views, and Optimization", 7,
                  "B-tree indexes, EXPLAIN, views, triggers, and FTS5.")

    _lesson(db, mod, "indexes",
            title="Indexes and Query Performance",
            lesson_type=LessonType.reading,
            content_md=M7_INDEXES,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "views-and-virtual-tables",
            title="Views, Triggers, and Virtual Tables",
            lesson_type=LessonType.reading,
            content_md=M7_VIEWS,
            duration_minutes=15,
            order_index=2)

    ex_lesson = _lesson(db, mod, "optimization-exercises",
                        title="Query Optimization Exercise",
                        lesson_type=LessonType.exercise,
                        content_md="Practice writing efficient queries using joins instead of repeated lookups.",
                        duration_minutes=20,
                        order_index=3)

    # ── Exercise 7.1: Customers in All Quarters ──────────────────
    e1 = _exercise(db, ex_lesson, "sql-query-analyzer",
        title="Customers Present in All Quarters",
        prompt_md=(
            "# Customers Present in All Quarters\n\n"
            "Given orders data and a list of required quarters, find all customers "
            "who placed at least one order in **every** required quarter. "
            "Output customer names sorted alphabetically.\n\n"
            "**Input format:**\n"
            "- First line: space-separated required quarters (e.g. `Q1 Q2 Q3`)\n"
            "- Remaining lines: `customer_name,quarter`\n\n"
            "**Output format:** matching customer names, one per line, alphabetical order\n\n"
            "**Example**\n"
            "```\nInput:\nQ1 Q2\nAlice,Q1\nAlice,Q2\nBob,Q1\nCarol,Q1\nCarol,Q2\n\n"
            "Output:\nAlice\nCarol\n```\n\n"
            "Hint: GROUP BY customer, COUNT(DISTINCT quarter WHERE quarter IN required_set) = len(required_set)."
        ),
        difficulty=Difficulty.hard,
        is_published=True,
        starter_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "required = lines[0].split()\n"
                "num_required = len(required)\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE orders (customer TEXT, quarter TEXT)')\n\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    customer, quarter = line.split(',')\n"
                "    cur.execute('INSERT INTO orders VALUES (?, ?)', (customer, quarter))\n"
                "conn.commit()\n\n"
                "# TODO: Find customers who have orders in ALL required quarters.\n"
                "# Hint: filter orders to only required quarters, then GROUP BY customer,\n"
                "# COUNT(DISTINCT quarter) = num_required\n"
            )
        },
        solution_code={
            "python": (
                "import sqlite3, sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "required = lines[0].split()\n"
                "num_required = len(required)\n\n"
                "conn = sqlite3.connect(':memory:')\n"
                "cur = conn.cursor()\n"
                "cur.execute('CREATE TABLE orders (customer TEXT, quarter TEXT)')\n\n"
                "for line in lines[1:]:\n"
                "    if not line.strip(): continue\n"
                "    customer, quarter = line.split(',')\n"
                "    cur.execute('INSERT INTO orders VALUES (?, ?)', (customer, quarter))\n"
                "conn.commit()\n\n"
                "placeholders = ','.join('?' * num_required)\n"
                "cur.execute(f'''\n"
                "    SELECT customer\n"
                "    FROM   orders\n"
                "    WHERE  quarter IN ({placeholders})\n"
                "    GROUP  BY customer\n"
                "    HAVING COUNT(DISTINCT quarter) = ?\n"
                "    ORDER  BY customer\n"
                "''', required + [num_required])\n"
                "for (customer,) in cur.fetchall():\n"
                "    print(customer)\n"
                "conn.close()\n"
            )
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=25,
    )
    _cases(db, e1, [
        ("Q1 Q2\nAlice,Q1\nAlice,Q2\nBob,Q1\nCarol,Q1\nCarol,Q2\n",
         "Alice\nCarol", False),
        ("Q1 Q2 Q3\nAlice,Q1\nAlice,Q2\nAlice,Q3\nBob,Q1\nBob,Q2\n",
         "Alice", False),
        ("Q1\nAlice,Q1\nBob,Q2\nCarol,Q1\n",
         "Alice\nCarol", True),
        ("Q1 Q2 Q3 Q4\nA,Q1\nA,Q2\nA,Q3\nA,Q4\nB,Q1\nB,Q2\nB,Q3\nC,Q1\nC,Q2\nC,Q3\nC,Q4\n",
         "A\nC", True),
    ])


# ════════════════════════════════════════════════════════════════
# MODULE 8 — Database Design and Normalization
# ════════════════════════════════════════════════════════════════

M8_NORMALIZATION = """\
# Normal Forms and Normalization

**Normalization** is the process of organizing a relational database to reduce data redundancy and improve data integrity. It was formalized by Edgar Codd through a series of **normal forms** (NF), each building on the previous.

## Why Normalize?

An unnormalized database suffers from **update anomalies**:

- **Insertion anomaly**: can't add a fact without adding other unrelated facts
- **Update anomaly**: changing one fact requires updating multiple rows (inconsistency risk)
- **Deletion anomaly**: deleting one fact accidentally deletes other unrelated facts

## First Normal Form (1NF)

A table is in **1NF** if:
1. Every column contains **atomic** (indivisible) values
2. There are no **repeating groups** (no multiple values in one cell)
3. Every row is uniquely identifiable (has a primary key)

```
-- NOT in 1NF (repeating group: multiple phone numbers in one cell)
| customer_id | name  | phones              |
|-------------|-------|---------------------|
| 1           | Alice | 555-1234, 555-5678  |

-- 1NF: separate table for phones
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE customer_phones (customer_id INTEGER, phone TEXT,
    PRIMARY KEY (customer_id, phone));
```

## Second Normal Form (2NF)

A table is in **2NF** if it is in 1NF and every non-key attribute is **fully functionally dependent** on the entire primary key (no partial dependencies).

This only applies when the primary key is **composite** (multiple columns):

```
-- NOT in 2NF: composite PK (order_id, product_id), but product_name depends only on product_id
| order_id | product_id | product_name | quantity |
|----------|------------|--------------|----------|

-- 2NF: separate products table
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE order_items (order_id INTEGER, product_id INTEGER,
    quantity INTEGER, PRIMARY KEY(order_id, product_id));
```

## Third Normal Form (3NF)

A table is in **3NF** if it is in 2NF and there are **no transitive dependencies** (non-key columns don't depend on other non-key columns):

```
-- NOT in 3NF: zip_code → city (transitive: emp_id → zip_code → city)
| emp_id | name  | zip_code | city     |
|--------|-------|----------|----------|

-- 3NF: separate zip codes table
CREATE TABLE zip_codes (zip TEXT PRIMARY KEY, city TEXT);
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, zip TEXT REFERENCES zip_codes(zip));
```

## Boyce-Codd Normal Form (BCNF)

A stricter version of 3NF: every determinant must be a **candidate key**. Most tables in 3NF are already in BCNF; violations occur only in tables with overlapping composite candidate keys (rare in practice).

## Denormalization Trade-offs

Normalization optimizes for **write performance and consistency**. For **read-heavy** workloads (analytics, reporting), controlled denormalization can be beneficial:

- Store pre-computed aggregates in summary tables
- Duplicate infrequently changing reference data to avoid joins
- Use materialized views

The key is intentional trade-off: denormalize specific paths that are proven bottlenecks, keeping the normalized form as the source of truth.

## Worked Example: 1NF → 3NF

Unnormalized sales table:
```
| sale_id | customer_name | customer_city | product_name | category | qty | price |
```

After 3NF normalization:
```sql
CREATE TABLE cities     (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE customers  (id INTEGER PRIMARY KEY, name TEXT, city_id INTEGER REFERENCES cities(id));
CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE products   (id INTEGER PRIMARY KEY, name TEXT, category_id INTEGER REFERENCES categories(id), price REAL);
CREATE TABLE sales      (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
                         product_id INTEGER REFERENCES products(id), qty INTEGER, sale_date TEXT);
```
"""

M8_ER_MODELING = """\
# Entity-Relationship Modeling

**Entity-Relationship (ER) modeling** is a technique for visually designing the logical structure of a database before writing any SQL. It captures entities, their attributes, and the relationships between them.

## Core Concepts

- **Entity**: a real-world object or concept (Customer, Product, Order)
- **Attribute**: a property of an entity (name, price, created_at)
- **Relationship**: a meaningful association between entities (Customer *places* Order)
- **Cardinality**: how many instances of one entity relate to another

## Cardinality Notation

| Relationship | Example | Notation |
|---|---|---|
| One-to-One (1:1) | Person ↔ Passport | Each person has exactly one passport |
| One-to-Many (1:N) | Department → Employee | One dept has many employees |
| Many-to-Many (M:N) | Student ↔ Course | Students enroll in many courses; courses have many students |

**Crow's foot notation** (common in ER tools):
```
Department ──<  Employee     (one department, many employees)
Student    >──< Course       (many students, many courses)
```

## Mapping ER to Relational Tables

### 1:N Relationship
The foreign key goes on the "many" side:
```sql
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE employees   (id INTEGER PRIMARY KEY, name TEXT,
                          dept_id INTEGER REFERENCES departments(id));
```

### M:N Relationship — Junction Table
```sql
CREATE TABLE students     (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE courses      (id INTEGER PRIMARY KEY, title TEXT);
CREATE TABLE enrollments  (student_id INTEGER REFERENCES students(id),
                           course_id  INTEGER REFERENCES courses(id),
                           enrolled_at TEXT,
                           grade TEXT,
                           PRIMARY KEY (student_id, course_id));
```

### 1:1 Relationship
Use a shared primary key or a unique foreign key:
```sql
CREATE TABLE persons   (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE passports (id INTEGER PRIMARY KEY REFERENCES persons(id),
                        passport_number TEXT UNIQUE, expiry_date TEXT);
```

## Weak Entities

A **weak entity** depends on another entity for its identity. Example: an order line item only exists as part of an order.

```sql
CREATE TABLE order_items (
    order_id   INTEGER REFERENCES orders(id),
    line_num   INTEGER,
    product_id INTEGER REFERENCES products(id),
    qty        INTEGER,
    PRIMARY KEY (order_id, line_num)   -- composite PK includes parent
);
```

## Case Study: School Enrollment System

Entities: Student, Course, Instructor, Department, Enrollment

```sql
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT, budget REAL);
CREATE TABLE instructors (id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER REFERENCES departments(id));
CREATE TABLE courses     (id INTEGER PRIMARY KEY, title TEXT, credits INTEGER,
                          dept_id INTEGER REFERENCES departments(id),
                          instructor_id INTEGER REFERENCES instructors(id));
CREATE TABLE students    (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, gpa REAL);
CREATE TABLE enrollments (student_id INTEGER REFERENCES students(id),
                          course_id  INTEGER REFERENCES courses(id),
                          semester   TEXT,
                          grade      TEXT,
                          PRIMARY KEY (student_id, course_id, semester));
```

This design supports queries like: "Which students are enrolled in courses taught by instructors in the CS department?" — answerable with a 4-table JOIN.
"""

M8_BEST_PRACTICES = """\
# SQL Best Practices and Course Recap

This final lesson consolidates the best practices you should apply in every SQL project, plus a roadmap for continuing your SQL journey.

## Naming Conventions

Consistent naming prevents confusion:

| Object | Convention | Examples |
|---|---|---|
| Tables | plural snake_case | `users`, `order_items`, `product_categories` |
| Columns | singular snake_case | `first_name`, `created_at`, `is_active` |
| Primary key | `id` | `id INTEGER PRIMARY KEY` |
| Foreign key | `{table_singular}_id` | `user_id`, `product_id` |
| Indexes | `idx_{table}_{columns}` | `idx_orders_customer_id` |
| Views | `v_{description}` | `v_active_products` |

## Surrogate vs Natural Keys

| Key Type | Description | Pro | Con |
|---|---|---|---|
| **Surrogate** | Auto-generated integer (`AUTOINCREMENT`) | Stable, simple joins | No business meaning |
| **Natural** | Real-world value (`email`, `isbn`) | Self-documenting | Can change, may be long |

**Recommendation**: Use surrogate integer primary keys for most tables. Use natural keys as UNIQUE constraints when the column is stable and meaningful.

## Audit Columns

Add these to every important table:

```sql
CREATE TABLE products (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    price      REAL    NOT NULL,
    -- audit
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT    NOT NULL DEFAULT (datetime('now')),
    deleted_at TEXT    -- NULL = active (soft delete)
);
```

## SQL Injection Prevention

**Never** build queries by string concatenation with user input:

```python
# DANGEROUS — SQL injection vulnerable
user_input = "'; DROP TABLE users; --"
cur.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

# SAFE — parameterized query
cur.execute("SELECT * FROM users WHERE name = ?", (user_input,))
```

Always use **parameterized queries** (placeholders `?` in SQLite, `%s` in psycopg2).

## Connection Pooling

In web applications, opening a new database connection for every request is expensive. Use a **connection pool**:

- SQLite: single file, use one connection per thread (or SQLAlchemy's `StaticPool` for tests)
- PostgreSQL: use `psycopg2` with `psycopg2.pool.ThreadedConnectionPool` or SQLAlchemy's pool
- Default pool size: 5–20 connections depending on server capacity

## Backup Strategies

| Strategy | Command | Use Case |
|---|---|---|
| SQLite file copy | `cp mydb.db mydb_backup.db` | Simple, no transactions in progress |
| SQLite `.dump` | `sqlite3 mydb.db .dump > backup.sql` | Portable SQL dump |
| PostgreSQL `pg_dump` | `pg_dump mydb > backup.sql` | Full backup with schema |
| Continuous WAL archiving | PostgreSQL streaming replication | Production HA setup |

## What to Learn Next

You have completed SQL Fundamentals. Your next steps:

1. **PostgreSQL** — production-grade open-source RDBMS with advanced features (JSONB, arrays, window functions, CTEs, full-text search, replication)
2. **Query Optimization** — EXPLAIN ANALYZE, index strategies, query planner hints, vacuum/analyze
3. **ORM Frameworks** — SQLAlchemy (Python), Prisma (Node.js), ActiveRecord (Ruby) — interact with databases using your programming language's objects
4. **Database Administration** — users, roles, grants, backup/restore, monitoring
5. **NoSQL** — understand when to use document (MongoDB), key-value (Redis), columnar (Cassandra), or graph (Neo4j) databases instead

## Course Recap

| Module | Key Concepts |
|---|---|
| 1 | Relational model, ACID, SQL sub-languages, SQLite setup |
| 2 | SELECT, WHERE, DISTINCT, LIMIT, ORDER BY |
| 3 | COUNT/SUM/AVG/MIN/MAX, GROUP BY, HAVING |
| 4 | INNER/LEFT/CROSS JOIN, multi-table queries |
| 5 | Subqueries, EXISTS, CTEs, recursive queries |
| 6 | INSERT/UPDATE/DELETE, transactions, UPSERT |
| 7 | Indexes, EXPLAIN, views, triggers, FTS5 |
| 8 | Normalization (1NF-3NF), ER modeling, best practices |

Congratulations on completing SQL Fundamentals!
"""


def seed_module8(db: Session, course: Course) -> None:
    mod = _module(db, course, "Database Design and Normalization", 8,
                  "Normal forms, ER modeling, and SQL best practices.")

    _lesson(db, mod, "normalization",
            title="Normal Forms and Normalization",
            lesson_type=LessonType.reading,
            content_md=M8_NORMALIZATION,
            duration_minutes=22,
            order_index=1)

    _lesson(db, mod, "er-modeling",
            title="Entity-Relationship Modeling",
            lesson_type=LessonType.reading,
            content_md=M8_ER_MODELING,
            duration_minutes=18,
            order_index=2)

    _lesson(db, mod, "sql-best-practices",
            title="SQL Best Practices and Recap",
            lesson_type=LessonType.reading,
            content_md=M8_BEST_PRACTICES,
            duration_minutes=12,
            order_index=3)


# ════════════════════════════════════════════════════════════════
# MAIN SEED FUNCTION
# ════════════════════════════════════════════════════════════════

def seed() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Require the Databases subject to already exist
        subject = _subject(db, "databases")
        if subject is None:
            sys.exit(
                "Error: Subject with slug 'databases' not found. "
                "Please run app/seed.py first to create the Databases subject."
            )

        # Create or find the SQL Fundamentals course
        course = _course(db, "sql-fundamentals")
        if course is None:
            course = Course(
                subject_id=subject.id,
                slug="sql-fundamentals",
                title="SQL Fundamentals",
                summary="Master SQL from SELECT basics to database design, covering all core relational database concepts.",
                description=(
                    "A comprehensive introduction to SQL and relational databases. "
                    "You will learn to query, modify, and design databases using SQLite and Python's sqlite3 module. "
                    "Covers SELECT queries, JOINs, aggregations, subqueries, CTEs, transactions, indexing, "
                    "normalization, and entity-relationship modeling through reading lessons and hands-on coding exercises."
                ),
                difficulty="beginner",
                estimated_hours=18,
                is_published=True,
                order_index=1,
            )
            db.add(course)
            db.flush()

        # Build all 8 modules
        seed_module1(db, course)
        seed_module2(db, course)
        seed_module3(db, course)
        seed_module4(db, course)
        seed_module5(db, course)
        seed_module6(db, course)
        seed_module7(db, course)
        seed_module8(db, course)

        db.commit()

    print("=" * 60)
    print("  SQL Fundamentals course seeded successfully.")
    print("  8 modules | 24 lessons | 10 exercises | 45+ test cases")
    print("=" * 60)


if __name__ == "__main__":
    seed()
