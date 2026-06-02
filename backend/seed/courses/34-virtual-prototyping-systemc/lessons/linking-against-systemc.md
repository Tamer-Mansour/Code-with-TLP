# Linking a Model Against the SystemC Library

SystemC is distributed as a C++ library — you compile your model's source files normally and then link them against `libsystemc`. Getting the include paths, library paths, and link flags exactly right is the first practical hurdle every new SystemC developer hits.

## What the SystemC Library Provides

The library supplies the kernel (`sc_start`, the scheduler, delta cycles), all primitive channels (`sc_signal`, `sc_fifo`), TLM infrastructure, and the simulation control API. Your code declares and uses these, but their definitions live in `libsystemc.a` (or `libsystemc.so`).

## Directory Layout of a SystemC Installation

```
/opt/systemc/
  include/
    systemc.h           <- top-level convenience header
    systemc/
      ...               <- individual sub-headers
    tlm.h
    tlm_utils/
      ...
  lib-linux64/          <- or lib-macos, lib-mingw64, etc.
    libsystemc.a
    libsystemc.so       <- may not always be built
```

## Compiler Flags

```bash
-I/opt/systemc/include      # tell the compiler where systemc.h lives
```

If SystemC was built with C++17 features or a specific ABI, match those flags:

```bash
-std=c++17
-DSC_CPLUSPLUS=201703L      # some builds require this define
```

## Linker Flags

```bash
-L/opt/systemc/lib-linux64  # directory containing libsystemc.a
-lsystemc                   # link against libsystemc (without lib prefix and .a suffix)
-lpthread                   # SystemC kernel uses POSIX threads internally
```

Order matters on the `g++` command line: put `-lsystemc` **after** the object files that reference it.

```bash
# Correct order
g++ main.o cpu.o bus.o -L/opt/systemc/lib-linux64 -lsystemc -lpthread -o sim

# Wrong — linker may fail to resolve symbols
g++ -lsystemc -L/opt/systemc/lib-linux64 main.o cpu.o bus.o -o sim
```

## A Complete Build Command

```bash
g++ -std=c++17 \
    -I/opt/systemc/include \
    main.cpp cpu_model.cpp bus_model.cpp \
    -L/opt/systemc/lib-linux64 \
    -lsystemc -lpthread \
    -o sim
```

## Using Environment Variables in a Makefile

Hardcoding `/opt/systemc` breaks the build on other machines. The standard approach is an environment variable `SYSTEMC_HOME`:

```makefile
SYSTEMC_HOME ?= /opt/systemc

CXXFLAGS := -std=c++17 -Wall -I$(SYSTEMC_HOME)/include
LDFLAGS  := -L$(SYSTEMC_HOME)/lib-linux64
LDLIBS   := -lsystemc -lpthread

SRCS := main.cpp cpu_model.cpp bus_model.cpp
OBJS := $(SRCS:.cpp=.o)

sim: $(OBJS)
	$(CXX) $^ $(LDFLAGS) $(LDLIBS) -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@
```

A developer who installed SystemC elsewhere can override it: `make SYSTEMC_HOME=/home/user/systemc-3.0`.

## Using pkg-config (When Available)

Some distributions install a `systemc.pc` file:

```bash
pkg-config --cflags systemc    # prints -I path
pkg-config --libs   systemc    # prints -L and -l flags
```

In a Makefile:

```makefile
CXXFLAGS += $(shell pkg-config --cflags systemc)
LDLIBS   += $(shell pkg-config --libs   systemc)
```

## Verifying the Link

```bash
# Check the executable is linked correctly
ldd ./sim | grep systemc       # for shared library
nm -u ./sim | grep sc_start    # should show U (undefined, resolved at load) or T (text, for static)
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `systemc.h: No such file` | Missing `-I` flag | Add `-I$(SYSTEMC_HOME)/include` |
| `undefined reference to sc_start` | Missing `-lsystemc` | Add `-lsystemc` after object files |
| `cannot find -lsystemc` | Wrong `-L` path | Check `SYSTEMC_HOME` and lib directory name |
| `undefined reference to pthread_create` | Missing `-lpthread` | Add `-lpthread` |

## Interview Answer

> "To link against SystemC, compile with `-I<systemc>/include` and link with `-L<systemc>/lib -lsystemc -lpthread`. Libraries must appear **after** the object files on the command line so the linker can resolve forward references."
