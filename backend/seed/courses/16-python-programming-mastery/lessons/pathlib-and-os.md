# pathlib and File System Operations

Working with file paths in Python used to mean string manipulation and `os.path` calls. Since Python 3.4, `pathlib.Path` provides an object-oriented, cross-platform interface that is easier to read and less error-prone.

## Creating a Path object

```python
from pathlib import Path

p = Path("data/results.csv")   # relative path
home = Path.home()             # /home/alice  or  C:\Users\Alice
cwd = Path.cwd()               # current working directory

abs_path = Path("/etc/hosts")
```

`Path` automatically uses the correct separator for the OS (`/` on POSIX, `\` on Windows).

## Navigating paths

```python
base = Path("/project")
full = base / "src" / "main.py"   # /project/src/main.py

print(full.name)       # "main.py"
print(full.stem)       # "main"
print(full.suffix)     # ".py"
print(full.parent)     # /project/src
print(full.parents[1]) # /project
```

The `/` operator joins path components — no more `os.path.join` with commas.

## Querying the file system

```python
p = Path("config.yaml")

p.exists()        # True / False
p.is_file()       # True if it's a regular file
p.is_dir()        # True if it's a directory
p.stat().st_size  # size in bytes
```

## Reading and writing files

```python
# Text
text = Path("readme.md").read_text(encoding="utf-8")
Path("output.txt").write_text("hello\n", encoding="utf-8")

# Bytes
data = Path("image.png").read_bytes()
Path("copy.png").write_bytes(data)
```

These one-liners open, read/write, and close the file automatically.

## Listing and globbing

```python
src = Path("src")

# All direct children
for child in src.iterdir():
    print(child)

# All Python files in the tree
for py_file in src.rglob("*.py"):
    print(py_file)

# Only top-level .txt files
for txt in src.glob("*.txt"):
    print(txt)
```

`rglob("*")` is equivalent to `glob("**/*")` — it recurses into subdirectories.

## Creating and removing paths

```python
Path("logs").mkdir(parents=True, exist_ok=True)   # mkdir -p
Path("temp.txt").touch()                          # create empty file
Path("old.txt").unlink()                          # delete file
Path("old_dir").rmdir()                           # delete empty dir
```

## Renaming and moving

```python
Path("draft.txt").rename("final.txt")               # rename in place
Path("a.txt").replace("b.txt")                      # overwrite b.txt
Path("file.txt").rename(Path("archive") / "file.txt")  # move
```

## When to still use os / shutil

`pathlib` covers most day-to-day needs. Reach for the other modules when you need:

| Task | Module |
|------|--------|
| Recursive delete a non-empty directory | `shutil.rmtree(path)` |
| Copy files and directories | `shutil.copy2`, `shutil.copytree` |
| Temporary files and directories | `tempfile.TemporaryDirectory()` |
| Environment variables | `os.environ` |
| Low-level stat/chmod | `os.stat`, `os.chmod` |

## Worked example: collect all logs older than 7 days

```python
import time
from pathlib import Path

cutoff = time.time() - 7 * 86400   # seconds
log_dir = Path("logs")

old_logs = [
    p for p in log_dir.glob("*.log")
    if p.stat().st_mtime < cutoff
]
print(f"Found {len(old_logs)} old log files.")
for p in old_logs:
    p.unlink()
    print(f"Deleted {p}")
```

`pathlib` makes the intent clear at every step: glob for `.log` files, check modification time, delete each one.
