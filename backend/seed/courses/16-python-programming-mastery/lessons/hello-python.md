# Hello, Python

Python is a high-level, interpreted, dynamically-typed language designed to be readable. It runs everywhere — Windows, macOS, Linux, browsers (via WebAssembly), embedded chips — and powers everything from one-off scripts to TikTok's backend.

## A first program

```python
print("hello, world")
```

Save as `hello.py`, then:

```bash
python hello.py
```

That's it — no `main()`, no semicolons, no curly braces.

## The REPL

Open `python` with no arguments and you're in the **interactive interpreter**:

```
>>> 2 + 2
4
>>> name = "world"
>>> f"hello, {name}"
'hello, world'
```

Treat the REPL as a scratch pad. `import` modules and poke at them — it's the fastest way to learn standard library behavior.

## Indentation matters

Python uses indentation, not braces, to delimit blocks:

```python
if hour < 12:
    print("morning")
else:
    print("afternoon")
```

**Four spaces** is the universal convention (PEP 8). Mixing tabs and spaces is a parse error.

## Versions

Python 3 is the only one that exists. Python 2 was retired in 2020 — if you see it, run.

Within Python 3, minor versions matter: 3.10 brought structural pattern matching, 3.11/3.12 brought big speed improvements, 3.13 brought a no-GIL build. Check your project's required version in `pyproject.toml`.

## A flavor of the language

```python
def fizzbuzz(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out

print("\n".join(fizzbuzz(15)))
```

You can read this without knowing Python. That's the design goal — readability is a feature.

## What you can build

- Web backends (FastAPI, Django, Flask).
- Data analysis and ML (pandas, NumPy, scikit-learn, PyTorch).
- DevOps automation (Ansible, scripts, glue code).
- CLI tools (`click`, `typer`).
- Game prototypes (Pygame).

For pure systems work or maximum throughput, reach for Go/Rust/C++. For everything else, Python is a solid default.
