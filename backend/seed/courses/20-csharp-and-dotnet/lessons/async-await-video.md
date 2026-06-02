This video walks through C# async/await from the ground up: why blocking I/O kills throughput, how the Task-based Asynchronous Pattern (TAP) works, and how `async`/`await` compiles into a state machine under the hood.

Key takeaways covered in the video:

- The difference between CPU-bound work (`Task.Run`) and I/O-bound work (`await httpClient.GetAsync`)
- How `ConfigureAwait(false)` avoids deadlocks in library code
- Common pitfalls: `async void`, `.Result`/`.Wait()` deadlocks, and fire-and-forget mistakes
- Cancellation tokens and how to propagate them through an async call chain
