# Quiz: Modern Python

**Q1. What does `Optional[str]` mean in a type hint?**
- [ ] The parameter is ignored at runtime
- [x] The value can be either a `str` or `None`
- [ ] The parameter is optional in the sense that it has a default value
- [ ] The type checker will skip this parameter

**Q2. Which statement correctly annotates a function that takes a list of integers and returns a float?**
- [ ] `def avg(nums: list) -> float:`
- [x] `def avg(nums: list[int]) -> float:`
- [ ] `def avg(nums: List[int]) -> float:` (Python 3.9+, this is also valid)
- [ ] Both B and C are correct

**Q3. `async def` functions return:**
- [ ] The value directly when called
- [x] A coroutine object that must be awaited or scheduled
- [ ] A `Future` immediately
- [ ] `None` always

**Q4. What does `await` do inside an async function?**
- [ ] Blocks all threads until the awaitable completes
- [x] Suspends the current coroutine and gives control back to the event loop until the awaitable is done
- [ ] Starts a new thread
- [ ] Converts a synchronous function to async

**Q5. `asyncio.gather(coro1(), coro2())` runs the coroutines:**
- [x] Concurrently (interleaved on a single thread)
- [ ] In parallel on separate CPU cores
- [ ] Sequentially, one after the other
- [ ] In separate processes

**Q6. In a `pyproject.toml`, the `[project.optional-dependencies]` section is used for:**
- [ ] Specifying the Python version constraint
- [x] Declaring extra dependency groups (e.g., `dev`, `test`) that are not installed by default
- [ ] Listing packages to exclude from the build
- [ ] Defining entry-point scripts

**Q7. What is the purpose of a virtual environment (`venv`)?**
- [ ] To sandbox Python from the operating system kernel
- [x] To isolate project dependencies from system-wide Python packages
- [ ] To speed up package installation
- [ ] To compile Python to native code
