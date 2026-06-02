# Character Device Backends: PTY, Socket, File

A production-quality virtual UART supports multiple backends. The console backend is fine for quick bringup, but real workflows require headless operation (no interactive terminal), multi-process communication, and logging. PTY, socket, and file backends cover these scenarios.

## Why Multiple Backends Matter

| Use Case | Best Backend |
|---|---|
| Interactive bootloader / shell debugging | Console (stdin/stdout) |
| Running firmware under a test script | File (stdin from file, stdout captured) |
| Connecting a real terminal emulator (minicom, picocom) | PTY |
| Network-remote debugging or CI on a server | TCP socket |
| Scripted regression test | File or socket with expect-style driver |

## PTY Backend

A **pseudo-terminal** (PTY) is a pair of file descriptors: the master end is held by the UART model, the slave end is exposed as a device node (e.g. `/dev/pts/3`). A terminal emulator opens the slave end and interacts with the simulation exactly as if it were a real serial port.

```cpp
#include <pty.h>    // openpty / forkpty (glibc)
// OR: #include <util.h> on macOS

class PtyBackend : public UartBackend {
public:
    PtyBackend() {
        char slave_name[64];
        if (openpty(&master_fd_, &slave_fd_, slave_name,
                    nullptr, nullptr) < 0)
            throw std::runtime_error("openpty failed");
        std::printf("[UART] PTY slave: %s\n", slave_name);
        // Set master_fd_ to non-blocking
        fcntl(master_fd_, F_SETFL, O_NONBLOCK);
    }

    void write_byte(uint8_t b) override {
        write(master_fd_, &b, 1);
    }

    bool read_byte(uint8_t &b) override {
        uint8_t buf;
        ssize_t n = read(master_fd_, &buf, 1);
        if (n == 1) { b = buf; return true; }
        return false;
    }

private:
    int master_fd_, slave_fd_;
};
```

The user runs `minicom -D /dev/pts/3` in a separate terminal. The virtual platform announces the slave name at startup.

## Socket Backend (TCP)

A TCP socket backend lets the UART communicate over a network, which is essential for CI infrastructure where the simulation runs on a remote server.

```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>

class TcpBackend : public UartBackend {
public:
    explicit TcpBackend(uint16_t port) {
        int srv = socket(AF_INET, SOCK_STREAM, 0);
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port   = htons(port);
        addr.sin_addr.s_addr = INADDR_ANY;
        int opt = 1;
        setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        bind(srv, (sockaddr*)&addr, sizeof(addr));
        listen(srv, 1);
        std::printf("[UART] Waiting for connection on port %u\n", port);
        conn_fd_ = accept(srv, nullptr, nullptr);  // blocks until client connects
        close(srv);
        fcntl(conn_fd_, F_SETFL, O_NONBLOCK);
    }

    void write_byte(uint8_t b) override { send(conn_fd_, &b, 1, MSG_NOSIGNAL); }

    bool read_byte(uint8_t &b) override {
        ssize_t n = recv(conn_fd_, &b, 1, 0);
        return n == 1;
    }

private:
    int conn_fd_;
};
```

Connect with `telnet localhost 5000` or `nc localhost 5000`. On the CI side, scripts can open a raw TCP connection and feed test vectors.

## File Backend

The file backend is the simplest for automated testing: TX output goes to a file (or stdout redirect), RX input comes from a pre-generated file.

```cpp
class FileBackend : public UartBackend {
public:
    FileBackend(const char *rx_path, const char *tx_path)
        : rx_file_(fopen(rx_path, "rb")),
          tx_file_(fopen(tx_path, "wb")) {}

    void write_byte(uint8_t b) override {
        fputc(b, tx_file_);
        fflush(tx_file_);
    }

    bool read_byte(uint8_t &b) override {
        int c = fgetc(rx_file_);
        if (c == EOF) return false;
        b = static_cast<uint8_t>(c);
        return true;
    }

private:
    FILE *rx_file_, *tx_file_;
};
```

Run the simulation with `./sim --uart-rx input.bin --uart-tx output.bin`, then diff `output.bin` against a golden reference.

## Selecting the Backend at Runtime

Use a command-line flag or an environment variable to choose:

```cpp
std::unique_ptr<UartBackend> make_backend(const std::string &type) {
    if (type == "console") return std::make_unique<ConsoleBackend>();
    if (type == "pty")     return std::make_unique<PtyBackend>();
    if (type == "tcp")     return std::make_unique<TcpBackend>(5000);
    if (type == "file")    return std::make_unique<FileBackend>("rx.bin","tx.bin");
    throw std::invalid_argument("Unknown backend: " + type);
}
```

**Interview answer:** A virtual UART backend is abstracted behind a `write_byte`/`read_byte` interface. The PTY backend exposes a `/dev/pts` node for terminal emulators, the TCP socket backend enables network-remote access and CI scripting, and the file backend enables deterministic replay testing — all without changing the UART register model.

## Common Pitfalls

- **Blocking accept in the SC kernel** — `accept()` blocks until a client connects. Call it before `sc_start()` or in a separate thread, otherwise the SystemC scheduler hangs before simulation begins.
- **Non-blocking not set on socket/PTY** — without `O_NONBLOCK`, a `read()` inside an SC_THREAD will stall the scheduler when no data is available.
- **PTY echo mode** — by default the PTY master echoes writes back to the master. Disable it with `cfmakeraw` on the slave termios, otherwise every TX byte is looped back into the RX FIFO.
