# Quiz: Standard Library

**Q1. `collections.defaultdict(list)` is useful because:**
- [ ] It prevents lists from being modified
- [x] Accessing a missing key automatically creates an empty list for that key
- [ ] It makes the dict ordered by insertion
- [ ] It deduplicates values in the lists

**Q2. `collections.Counter("abracadabra")["a"]` returns:**
- [ ] `1`
- [ ] `3`
- [x] `5`
- [ ] A `KeyError`

**Q3. `pathlib.Path("data") / "file.txt"` produces:**
- [ ] A string `"data/file.txt"` (on Unix) or `"data\\file.txt"` (on Windows)
- [x] A `Path` object representing `data/file.txt`
- [ ] A `TypeError` because `/` is not valid for Path objects
- [ ] The contents of the file

**Q4. `Path.glob("**/*.py")` matches:**
- [ ] Only `.py` files in the current directory
- [x] All `.py` files in the current directory and all subdirectories recursively
- [ ] Only files ending in exactly `*.py` literally
- [ ] All files in all subdirectories regardless of extension

**Q5. Which `collections` type gives you a fixed-length sequence with named fields (like a lightweight class)?**
- [ ] `OrderedDict`
- [ ] `deque`
- [x] `namedtuple`
- [ ] `Counter`

**Q6. `collections.deque` is preferred over a list when:**
- [ ] You need random access by index
- [x] You need fast appends and pops from both ends (O(1))
- [ ] You need sorting
- [ ] You need deduplication

**Q7. `pathlib.Path.read_text()` is equivalent to:**
- [x] `open(path).read()`
- [ ] `open(path, "rb").read()`
- [ ] `open(path).readlines()`
- [ ] `json.load(open(path))`
