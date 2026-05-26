# Hardware vs Software

Understanding the difference between hardware and software—and how they interact—is the foundation for everything else in computer science. This lesson goes deeper into each layer and shows exactly how a single keystroke travels from your fingertip to a character on screen.

## Hardware: The Physical Machine

Hardware refers to any component you can physically touch. It obeys the laws of physics and electricity. Hardware does nothing meaningful on its own; it needs software to direct it.

### Major Hardware Categories

**Processing**

- **CPU (Central Processing Unit)** — executes arithmetic, logic, and control instructions. Modern CPUs (Intel Core, AMD Ryzen, Apple M-series) have 8–24 cores, each running at 3–5 GHz. Each core can execute billions of simple operations per second.
- **GPU (Graphics Processing Unit)** — originally for rendering 3D graphics; now widely used for massively parallel computation (AI training, video encoding, scientific simulation). A modern GPU has thousands of small cores, perfect for doing the same operation on millions of data points simultaneously.

**Memory**

- **RAM (Random Access Memory)** — fast, temporary storage used while a program runs. "Random access" means any byte can be reached in the same amount of time, regardless of location. Typical laptop: 8–32 GB. Volatile—contents are lost when power is cut.
- **Cache** — tiny, ultra-fast memory built directly into the CPU die (the silicon chip itself). The CPU checks cache first before going to the slower main RAM. Organised in levels: L1 (32–64 KB, ~1 ns), L2 (256 KB–1 MB, ~4 ns), L3 (4–32 MB, ~10 ns). Cache misses—when the needed data is not in cache—are a major performance bottleneck.

**Storage**

- **HDD (Hard Disk Drive)** — magnetic spinning platters; a read/write head physically moves to the right track. Slow (5–10 ms access time) but cheap per gigabyte. Good for bulk storage.
- **SSD (Solid State Drive)** — stores data in NAND flash memory chips; no moving parts. Much faster than HDD (0.05–0.1 ms access time), more durable, but costs more per GB.
- **NVMe SSD** — connects via the PCIe bus instead of the older SATA connector; up to 10× faster than a SATA SSD. Used in modern laptops and desktops.

**Input / Output**

- Input: keyboard, mouse, touchscreen, microphone, webcam, sensors, game controllers.
- Output: monitor, speakers, printer, haptic motors (vibration in phones).
- Input/Output: USB drives (can read and write), touchscreens (both display and sense touch).

**Connectivity**

- **NIC (Network Interface Card)** — connects the computer to a wired (Ethernet) network.
- **Wi-Fi chip** — wireless network connectivity.
- **PCIe bus** — the high-speed internal highway connecting the CPU to GPUs, SSDs, and other peripherals.
- **USB** — universal serial bus; connects external devices (drives, keyboards, cameras).

## Software: The Set of Instructions

Software is a sequence of instructions encoded as numbers stored in memory. Hardware executes those numbers; it has no concept of "meaning"—it simply carries out each instruction in turn.

### Layers of Software

```
User Applications     (web browser, text editor, game)
        ↓
Libraries & Runtimes  (Python interpreter, C standard library, OpenGL)
        ↓
Operating System      (Linux, Windows, macOS, iOS, Android)
        ↓
Firmware / BIOS/UEFI  (low-level code stored in ROM chips on the motherboard)
        ↓
Hardware              (CPU, RAM, storage, I/O)
```

Each layer provides **services** to the layer above and hides the complexity of the layer below. This is the principle of abstraction in action.

### Types of Software

| Category | Examples | Role |
|----------|---------|------|
| Operating system | Linux, Windows, Android | Manages hardware, runs processes, enforces security |
| Runtime / VM | Python interpreter, JVM (Java), V8 (JavaScript) | Runs code written in high-level languages |
| Libraries | C standard library, NumPy, SQLite | Reusable code components callable by applications |
| Applications | Firefox, VS Code, Excel, Discord | End-user functionality |
| Firmware | BIOS/UEFI, SSD controller firmware | Starts the machine, initialises hardware, embedded device logic |

### The Operating System in Detail

The OS is the most important layer. Its key jobs:

1. **Process management** — decides which program runs on which CPU core at which moment (scheduling).
2. **Memory management** — gives each program its own protected slice of RAM; prevents one program from reading another's data.
3. **File system** — organises data on disk into files and folders.
4. **Device drivers** — software that translates OS requests into the specific commands a hardware device understands (every keyboard model needs a driver).
5. **Security** — enforces access controls (you can read your files, not other users' files).

## How They Work Together: A Concrete Example

When you press a key on your keyboard:

```
1. HARDWARE — The key switch closes a circuit.
      ↓
2. FIRMWARE — The keyboard microcontroller detects the switch,
   maps it to a USB HID scancode (e.g., 0x04 for 'A'),
   and sends a USB packet.
      ↓
3. OS KERNEL (USB driver) — Receives the packet, converts
   the scancode to a virtual key code, places a "key pressed"
   event in the input queue.
      ↓
4. OS KERNEL (window manager) — Delivers the event to the
   focused window (your text editor).
      ↓
5. APPLICATION — The text editor reads the event, inserts
   the character 'A' at the cursor position, and redraws
   the affected portion of the screen.
      ↓
6. HARDWARE (GPU + monitor) — The GPU renders the new frame
   and the monitor displays it.
```

A single keypress triggers a chain of at least six distinct software/hardware layers. This happens in under **1 millisecond**.

## Why the Distinction Matters

**Debugging**

- A crash caused by bad code is a **software bug**; a crash caused by a failing chip is a **hardware failure**. The diagnosis—and the fix—is completely different.
- Overheating CPUs cause random crashes (hardware). Infinite loops that freeze the UI are software bugs.

**Upgrades**

- You can improve a computer's capabilities by replacing hardware (add more RAM, upgrade SSD) *or* by installing better software (a faster algorithm, a more efficient OS).
- A poorly written application can make a powerful machine feel sluggish; a well-optimised program can run blazingly fast on modest hardware.

**Portability**

- Software can (with care) run on many different hardware platforms; hardware cannot move to a different physical machine.
- Web applications run in a browser on Windows, Mac, Linux, iOS, and Android—same software, different hardware. This is portability in action.

## Common Misconceptions

**"The OS is part of the hardware."**
No—the OS is software. It is stored on disk and loaded into RAM at boot time, just like any other program. The CPU runs OS code the same way it runs your application code.

**"More cores always makes everything faster."**
Only if the software is written to use multiple cores (parallel programming). A single-threaded Python script uses one core; adding 15 more cores does not help it go faster.

**"Firmware is just an old term for software."**
Firmware is software, but it is stored in non-volatile memory (ROM or flash) directly on a hardware component and is tightly coupled to that hardware. Updating it requires special care—a bad firmware update can permanently brick a device.

## Key Takeaways

- Hardware is physical; software is logical—but neither is useful without the other.
- Software runs in layers: firmware → OS → runtimes → applications. Each layer hides complexity from the one above.
- The OS manages processes, memory, the file system, device drivers, and security.
- A single keypress triggers a chain of at least six hardware and software layers in under a millisecond.
- More cores, more RAM, and faster storage all improve different aspects of performance—there is no single "make it faster" upgrade.
