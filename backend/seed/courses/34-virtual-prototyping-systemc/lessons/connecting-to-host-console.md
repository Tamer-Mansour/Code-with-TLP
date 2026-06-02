# Connecting a Virtual UART to the Host Console

Once the register interface and FIFOs are working, the UART model needs a backend: somewhere to send TX bytes and somewhere to receive RX bytes. The simplest backend is the host console, reached through standard I/O. This is usually the first integration step before more sophisticated backends (PTY, socket, file) are added.

## The Backend Abstraction

Decouple the backend from the UART register logic by defining a narrow interface:

```cpp
class UartBackend {
public:
    virtual ~UartBackend() = default;
    virtual void write_byte(uint8_t b) = 0;    // UART TX → backend
    virtual bool read_byte(uint8_t &b) = 0;    // backend → UART RX (non-blocking)
};
```

The UART model holds a pointer to a `UartBackend`. Swapping backends (console → PTY → socket) requires changing only the constructor argument, not the model itself.

## Console Backend Using stdio

The simplest backend writes to stdout and reads from stdin. On Linux/macOS this "just works". On Windows, the console must be put into raw mode to avoid line-buffering.

```cpp
#include <cstdio>
#include <cerrno>
#include <unistd.h>    // POSIX: for read()
#include <termios.h>   // POSIX: for tcsetattr()

class ConsoleBackend : public UartBackend {
public:
    ConsoleBackend() { set_raw_mode(true); }
    ~ConsoleBackend() { set_raw_mode(false); }

    void write_byte(uint8_t b) override {
        fputc(b, stdout);
        fflush(stdout);            // flush immediately — no line buffering
    }

    bool read_byte(uint8_t &b) override {
        // Non-blocking read from stdin
        fd_set fds;
        FD_ZERO(&fds); FD_SET(STDIN_FILENO, &fds);
        struct timeval tv = {0, 0};  // zero timeout
        if (select(1, &fds, nullptr, nullptr, &tv) > 0) {
            int c = fgetc(stdin);
            if (c != EOF) { b = static_cast<uint8_t>(c); return true; }
        }
        return false;
    }

private:
    struct termios saved_;

    void set_raw_mode(bool enable) {
        if (enable) {
            tcgetattr(STDIN_FILENO, &saved_);
            struct termios raw = saved_;
            raw.c_lflag &= ~(ICANON | ECHO);
            tcsetattr(STDIN_FILENO, TCSANOW, &raw);
        } else {
            tcsetattr(STDIN_FILENO, TCSANOW, &saved_);
        }
    }
};
```

## Wiring the Backend into the UART Model

In the UART model's TX thread, call the backend after dequeuing each byte:

```cpp
void UartModel::tx_thread() {
    while (true) {
        wait(tx_event_);
        uint8_t byte;
        while (tx_fifo_.pop(byte)) {
            if (backend_) backend_->write_byte(byte);
            update_lsr();
        }
        update_irq();
    }
}
```

For RX, poll the backend periodically from a dedicated SC_THREAD:

```cpp
void UartModel::rx_poll_thread() {
    while (true) {
        wait(poll_period_);          // e.g., 1 ms of simulation time
        if (backend_) {
            uint8_t b;
            while (backend_->read_byte(b)) {
                rx_push(b);
            }
        }
    }
}
```

## Handling Raw Mode Properly

Without raw mode, the host terminal buffers input until the user presses Enter. This breaks any firmware that expects character-at-a-time input (interactive shells, bootloaders). The `ConsoleBackend` constructor sets `ICANON=0` and `ECHO=0` to disable line editing and local echo. The destructor restores the original settings so the terminal is not left in raw mode after simulation ends.

On Windows, use `SetConsoleMode` with `ENABLE_VIRTUAL_TERMINAL_PROCESSING` and clear `ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT`.

## SystemC Time and Real Time

The RX poll period is a simulation-time quantity. In a virtual platform running faster than real time, 1 ms of simulation time might correspond to microseconds of wall-clock time — the console poll fires more often than needed, but that is harmless. In a platform running slower than real time, the poll may introduce latency. A better approach is to use a separate POSIX thread that blocks on `read()` and posts an SC_EVENT:

```cpp
// Separate std::thread — outside SC kernel
void ConsoleBackend::reader_thread() {
    uint8_t b;
    while (running_) {
        if (read(STDIN_FILENO, &b, 1) == 1) {
            std::lock_guard<std::mutex> lk(mtx_);
            rx_queue_.push(b);
            rx_event_.notify();   // sc_event::notify() is thread-safe in SystemC
        }
    }
}
```

**Interview answer:** Connect a virtual UART to the host console by implementing a `UartBackend` interface with `write_byte` (stdout) and `read_byte` (non-blocking stdin). Set the terminal to raw mode so input is delivered character-at-a-time. Wire the backend into the UART's TX thread and poll it from an RX SC_THREAD.

## Common Pitfalls

- **Forgetting fflush** — without it, TX bytes are buffered in the C library and appear on screen in large batches or only when the simulation ends.
- **Blocking read on stdin** — a blocking `fgetc` inside an SC_THREAD will stall the entire SystemC scheduler. Always use `select`/`poll` with zero timeout, or move blocking I/O to a separate native thread.
- **Not restoring terminal mode** — if simulation crashes without calling the destructor, the terminal is left in raw mode, making subsequent shell commands unusable.
