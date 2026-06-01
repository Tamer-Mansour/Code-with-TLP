# async / await

Python's `asyncio` lets you write concurrent code that handles thousands of I/O-bound operations on a single thread. It's how modern web servers, scrapers, and bots scale in Python.

## Coroutines

A coroutine is a function declared with `async def`. Calling it doesn't run it — it returns a coroutine object you must `await`.

```python
import asyncio

async def hello():
    await asyncio.sleep(1)
    print("hello")

asyncio.run(hello())
```

`asyncio.run(coro)` starts the event loop, runs the coroutine to completion, then closes the loop.

## await

You can only `await` inside an `async def`. It pauses the current coroutine until the awaited thing is done.

```python
async def fetch_user(uid):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"/users/{uid}")
        return r.json()
```

While paused, the event loop can run *other* coroutines — that's the concurrency.

## Run things in parallel — gather

```python
async def main():
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
    print(users)
```

All three requests fly in parallel. Total time ≈ slowest one, not sum.

## TaskGroup (3.11+)

Cleaner than `gather` when you want structured concurrency and proper exception handling:

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch_user(1))
        t2 = tg.create_task(fetch_user(2))
    print(t1.result(), t2.result())
```

If one task raises, the group cancels the others and re-raises.

## Async iteration

`async for` over an async iterable:

```python
async for line in stream:
    process(line)
```

`async with` for async context managers:

```python
async with session.get(url) as resp:
    body = await resp.text()
```

## CPU work blocks the loop

`asyncio` is for I/O. CPU-bound work blocks the event loop and starves every other coroutine. For CPU work use `asyncio.to_thread` (3.9+) or `ProcessPoolExecutor`:

```python
result = await asyncio.to_thread(crunch_numbers, big_array)
```

## Timeouts

```python
try:
    r = await asyncio.wait_for(fetch_user(1), timeout=3.0)
except asyncio.TimeoutError:
    ...
```

3.11+ `asyncio.timeout`:

```python
async with asyncio.timeout(3.0):
    r = await fetch_user(1)
```

## The big trap: mixing sync and async

A blocking call inside an `async` function freezes the loop:

```python
async def bad():
    time.sleep(5)            # BLOCKS the whole loop
    requests.get(...)        # ALSO BLOCKS
```

Use async equivalents (`asyncio.sleep`, `httpx`, `aiofiles`, `asyncpg`) or wrap blocking work in `asyncio.to_thread`.

## When NOT to use asyncio

- Pure CPU programs.
- Code that's mostly synchronous already — adding async halfway is a maintenance nightmare.
- Simple scripts where a thread or two would do.

For web servers and high-fanout I/O, `asyncio` is the right call. For everything else, keep it simple.
