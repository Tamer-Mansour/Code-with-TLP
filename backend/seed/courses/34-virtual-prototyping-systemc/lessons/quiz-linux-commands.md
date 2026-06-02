# Quiz: Linux Command Line for VP Engineers

Test your knowledge of the Linux commands used daily in virtual prototype development.

---

**Q1. You type `./sim_top` and get "Permission denied". Which command fixes this?**

- [ ] `chmod 644 sim_top`
- [x] `chmod +x sim_top`
- [ ] `sudo rm sim_top`
- [ ] `mv sim_top /usr/bin/`

The execute bit (`x`) must be set for a file to run as a program. `chmod 644` grants read/write but no execute. `chmod +x` adds execute permission for the owner.

---

**Q2. Your simulation binary cannot find `libsystemc.so` at runtime. Which environment variable should you update?**

- [ ] `PATH`
- [ ] `SYSTEMC_HOME`
- [x] `LD_LIBRARY_PATH`
- [ ] `CXXFLAGS`

`PATH` controls where the shell finds executables. `LD_LIBRARY_PATH` controls where the dynamic linker searches for shared libraries (`.so` files). A missing or wrong `LD_LIBRARY_PATH` causes "cannot open shared object file" errors.

---

**Q3. Which command finds all `.cpp` files under the current directory that contain the text `b_transport`?**

- [ ] `find . -name "b_transport"`
- [x] `grep -r "b_transport" --include="*.cpp" .`
- [ ] `ls -r *.cpp | grep b_transport`
- [ ] `cat *.cpp | find b_transport`

`grep -r` searches recursively through directory trees. `--include="*.cpp"` restricts matches to C++ source files. `find` locates files by metadata, not content.

---

**Q4. You want to compile `main.cpp` and `initiator.cpp` into a binary called `sim_top`, linking with SystemC headers in `/opt/sc/include` and the library in `/opt/sc/lib`. Which command is correct?**

- [ ] `gcc -I/opt/sc/include -L/opt/sc/lib -lsystemc -o sim_top main.cpp initiator.cpp`
- [x] `g++ -std=c++17 -I/opt/sc/include -L/opt/sc/lib -o sim_top main.cpp initiator.cpp -lsystemc`
- [ ] `g++ -I/opt/sc/lib -L/opt/sc/include -lsystemc -o sim_top main.cpp initiator.cpp`
- [ ] `gcc -std=c++17 -o sim_top main.cpp initiator.cpp -lsystemc`

SystemC is a C++ library so `g++` is required (not `gcc`). `-I` takes the header directory and `-L` takes the library directory — they must not be swapped. `-lsystemc` links the SystemC library.

---

**Q5. A simulation has been running for 2 hours and appears frozen. You find its PID is 9341. What is the correct sequence of commands?**

- [ ] `rm -f /proc/9341` then reboot
- [ ] `kill -1 9341` and wait forever
- [x] `kill 9341` to try SIGTERM, then `kill -9 9341` if it does not stop
- [ ] `top -k 9341` only

Best practice is to send SIGTERM (default `kill`) first, giving the process a chance to flush logs and release resources. Only escalate to SIGKILL (`-9`) if the process does not respond. SIGKILL cannot be caught or ignored, so cleanup code never runs.

---

**Q6. Which `make` flag rebuilds all targets in parallel using 4 CPU cores?**

- [ ] `make -r 4`
- [ ] `make --parallel=4`
- [x] `make -j4`
- [ ] `make -p 4`

`-j N` tells `make` to run up to N jobs simultaneously. This dramatically speeds up large SystemC projects with many translation units. Without `-j`, make builds one file at a time.
