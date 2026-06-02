"""Generate `course.yaml` for the directory-based courses that ship only lesson
markdown (no manifest yet): cpp-for-systems, computer-architecture-riscv, and
virtual-prototyping-systemc.

The lesson `.md` files carry no front-matter, so this script imposes structure:

  * Each course defines an ORDERED list of modules, each with keyword patterns.
  * Every lesson file is assigned to the module whose *longest* matching pattern
    is a substring of the lesson slug (longest-match wins, so `smart-pointer`
    beats `pointer`). Unmatched lessons fall into a final "Further Topics" module.
  * `*.prompt.md` files become `exercise`-type lessons; `quiz-*.md` become
    `quiz`-type lessons; everything else is `reading`.
  * Lesson titles are read from the first markdown H1.

It prints a coverage report (module sizes + any unmatched slugs) and writes a
`course.yaml` into each course folder that `import_courses.py` then loads.

Run from the backend/ directory:

    python seed/generate_course_yaml.py            # write all course.yaml files
    python seed/generate_course_yaml.py --dry-run  # report only, write nothing
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

COURSES_DIR = Path(__file__).resolve().parent / "courses"

# Subject reused across all three (matches the existing 05-computer-architecture).
SYSTEMS_SUBJECT = {
    "slug": "systems",
    "name": "Systems",
    "description": "How computers run software, from the CPU up to the network.",
    "icon": "server",
    "color": "#ef4444",
    "order_index": 4,
}

# Course prefixes used on *.prompt.md exercise slugs, stripped before matching.
EXERCISE_PREFIXES = ("cpp-", "arch-", "vp-")

DURATION = {"reading": 10, "quiz": 6, "exercise": 20}


# ── Module definitions (ordered) ─────────────────────────────────────────────
# Each entry: (module title, [keyword patterns matched as substrings of slug]).

CPP_MODULES = [
    ("C++ Foundations & Toolchain", [
        "what-is-cpp", "c-vs-cpp", "hello-systems", "compilation-pipeline",
        "compile-time-vs-runtime", "declaration-vs-definition", "translation-units",
        "one-definition-rule", "extern-linkage", "cpp-foundations"]),
    ("Types & Operators", [
        "fundamental-types", "auto-type", "decltype", "integer-promotion",
        "arithmetic-operator", "arithmetic-and-comparison", "comparison-operator",
        "increment-decrement", "logical-and", "operator-precedence", "short-circuit",
        "uniform-initialization", "structured-bindings", "casts-static-reinterpret",
        "types-and-operators"]),
    ("Control Flow & Functions", [
        "if-switch", "loops-while", "break-continue", "recursion-and-the-stack",
        "functions-parameters", "function-overloading", "default-arguments",
        "inline-functions", "lambda", "fizzbuzz", "control-flow-functions"]),
    ("Pointers & References", [
        "what-is-a-pointer", "what-is-a-reference", "pointer-vs-reference",
        "dereferencing", "pointer-arithmetic", "pointers-to-pointers", "void-pointers",
        "pointer-decay", "pass-by-value", "pass-by-reference", "pass-by-pointer",
        "parameter-passing", "swap-and-out-params", "returning-references",
        "reference-lifetime", "nullptr-vs-null", "references-and-passing",
        "quiz-pointers"]),
    ("Dynamic Memory", [
        "new-and-delete", "new-delete", "array-new", "placement-new", "stack-vs-heap",
        "automatic-vs-dynamic", "object-lifetime", "heap-allocation", "memory-leak",
        "dangling-pointer", "double-free-and-corruption", "mmap", "uninitialized-memory",
        "ownership-and-lifetime", "alloc-tracker", "nothrow-and-bad-alloc", "dynamic-memory"]),
    ("Classes & Objects", [
        "class-and-object", "data-members", "this-pointer", "member-initializer",
        "access-specifiers", "struct-vs-class", "nested-and-local-classes",
        "static-members", "static-in-classes", "static-local", "static-at-file-scope",
        "designing-a-class-api", "classes-and-objects"]),
    ("Encapsulation & Abstraction", [
        "encapsulation", "information-hiding", "getters-setters", "abstraction-defined",
        "four-pillars", "friend-functions", "interface-vs-implementation",
        "encapsulation-abstraction"]),
    ("Constructors & Destructors", [
        "constructor-basics", "destructor-basics", "construction-order",
        "delegating-constructors", "explicit-and-conversion-constructors",
        "conversion-operators", "default-and-delete", "implicit-special-members",
        "base-class-initialization", "why-constructors-cannot-be-virtual",
        "constructors-destructors"]),
    ("Copy Semantics", [
        "copy-constructor", "copy-assignment", "shallow-vs-deep-copy", "shallow-copy",
        "deep-copy", "self-assignment", "double-free-from-shallow-copy", "rule-of-three",
        "rule-of-zero", "copy-elision", "copy-semantics"]),
    ("Move Semantics", [
        "move-constructor", "move-assignment", "rvalue-references", "lvalues-and-rvalues",
        "std-move", "perfect-forwarding", "rule-of-five", "noexcept-move",
        "move-semantics"]),
    ("Inheritance", [
        "inheritance-basics", "public-protected-private-inheritance", "is-a-vs-has-a",
        "favor-composition", "multiple-inheritance", "diamond-problem", "upcasting",
        "object-slicing", "name-hiding", "quiz-inheritance"]),
    ("Polymorphism & Virtual Functions", [
        "polymorphism", "virtual-function", "virtual-destructor",
        "static-vs-dynamic-binding", "overloading-vs-overriding", "virtual-override",
        "vtable", "virtual-calls", "inline-virtual", "runtime-polymorphism",
        "polymorphism-virtual"]),
    ("Abstract Classes & Interfaces", [
        "abstract-class", "abstract-base-design", "interface-like-class", "pure-virtual",
        "nvi-idiom", "plugin-architecture-with-interfaces", "abstract-classes-interfaces"]),
    ("Operator Overloading", [
        "operator-overloading", "operators-you-should-not-overload",
        "member-vs-nonmember-operators", "stream-insertion-operator",
        "subscript-and-call-operators", "quiz-operator-overloading"]),
    ("RAII & Resource Management", [
        "raii", "scope-guard", "exception-safety"]),
    ("Smart Pointers", [
        "smart-pointer", "unique-ptr", "shared-ptr", "weak-ptr", "make-unique",
        "refcount-cycle", "quiz-smart-pointers"]),
    ("const, constexpr & Qualifiers", [
        "const-deep-dive", "constexpr", "const-member-functions",
        "const-pointer-combinations", "mutable-and-thread-local", "volatile",
        "nullptr-constexpr", "quiz-qualifiers"]),
    ("Templates & Generics", [
        "function-templates", "class-templates", "template-specialization",
        "templates-vs-virtual", "concepts-and-constraints"]),
    ("STL Containers", [
        "stl-overview", "std-vector", "vector-vs-array", "std-map", "map-vs-unordered",
        "unordered-map", "list-deque-set", "container-complexity", "optional-and-variant",
        "std-function", "stl-containers"]),
    ("Iterators & Algorithms", [
        "iterators-and-categories", "iterator-invalidation", "std-algorithms",
        "range-based-for", "ranges-pipeline", "iterators-algorithms-templates"]),
    ("Modern C++ Essentials", [
        "modern-cpp-essentials"]),
    ("Memory Model, Layout & Alignment", [
        "memory-alignment", "alignof", "struct-padding", "struct-size-calculation",
        "packed-structs", "offsetof", "unions-and-bitfields", "type-punning",
        "strict-aliasing", "memory-mapped-device", "modeling-registers",
        "register-mapped-io", "process-memory-layout",
        "stack-frames-and-calling-convention", "where-do-globals", "alignment-padding",
        "memory-model"]),
    ("Bit Manipulation", [
        "bitwise-operators", "bit-masks", "bit-tricks", "set-a-bit", "clear-a-bit",
        "toggle-a-bit", "check-a-bit", "shift-pitfalls", "bit-ops", "bit-manipulation"]),
    ("Endianness & Data Representation", [
        "endianness", "byte-swapping", "network-byte-order", "char-encoding",
        "twos-complement", "signed-vs-unsigned", "floating-point-representation",
        "serialization-and-wire-format", "hex-dump", "quiz-endianness"]),
    ("Undefined Behavior", [
        "undefined-behavior", "common-ub", "integer-overflow", "ub-and-the-optimizer",
        "buffer-overflow", "stack-overflow", "segfault"]),
    ("Debugging & Tooling", [
        "gdb", "debug-symbols", "core-dump", "crash-reports", "valgrind",
        "asan-ubsan-tsan", "static-analysis", "compiler-warnings", "defensive-coding",
        "debugging-tooling"]),
    ("Concurrency", [
        "threads-and-processes", "std-thread", "mutex", "race-condition", "deadlock",
        "condition-variables", "atomics", "memory-order", "false-sharing", "concurrency"]),
    ("Operating-System Concepts", [
        "process-lifecycle", "system-calls-and-user-kernel", "virtual-memory-and-paging",
        "scheduling-policies", "context-switching", "round-robin-scheduler", "os-concepts"]),
    ("Systems Capstone & Interview", [
        "pimpl", "performance-in-simulators", "what-is-a-virtual-prototype",
        "instruction-set-basics", "instruction-decode", "riscv-decode",
        "register-file-simulation", "address-translation", "word-frequency-counter",
        "interview-strategy", "vp-systems-capstone"]),
]

ARCH_MODULES = [
    ("Foundations of Computer Architecture", [
        "what-is-computer-architecture", "architecture-vs-organization",
        "abstraction-layers", "stored-program", "von-neumann", "moores-law-dennard",
        "quiz-foundations"]),
    ("Number Systems & Data", [
        "binary-and-hex", "hex-binary", "binary-hex", "twos-complement", "sign-extension",
        "signed-vs-unsigned", "unsigned-vs-signed", "overflow-and-carry",
        "fixed-point-vs-floating", "ieee-754", "bitwise-and-shift",
        "bit-manipulation-tricks", "quiz-number-systems"]),
    ("Endianness", [
        "what-is-endianness", "little-vs-big-endian", "endianness-in-riscv",
        "why-endianness-matters", "detecting-endianness", "byte-swapping",
        "endianness-converter", "quiz-endianness"]),
    ("Digital Logic", [
        "logic-gates", "boolean-algebra", "boolean-expression", "karnaugh",
        "combinational-vs-sequential", "half-adder", "multiplexers-decoders",
        "flip-flops", "finite-state-machines", "registers-and-counters", "ripple-carry",
        "quiz-digital-logic"]),
    ("The ALU", [
        "the-alu", "alu-flag", "alu-flags", "subtraction-in-the-alu",
        "multiplication-division", "quiz-alu"]),
    ("CPU Components", [
        "what-is-a-cpu", "cpu-datapath", "control-unit", "program-counter",
        "instruction-register-and-mar", "registers-overview", "register-vs-memory",
        "general-purpose-vs-special", "hardwired-vs-microprogrammed", "micro-operations",
        "clock-and-cpu-timing", "quiz-cpu-components"]),
    ("The Instruction Cycle", [
        "instruction-cycle", "fetch-stage", "decode-stage", "execute-stage",
        "memory-access-writeback", "micro-ops-in-modern", "single-cycle-vs-multi-cycle",
        "quiz-instruction-cycle"]),
    ("Instruction Set Architecture", [
        "what-is-an-isa", "isa-as-hardware", "isa-compatibility", "operand-count",
        "addressing-modes", "base-plus-offset", "code-density", "fixed-vs-variable-length",
        "famous-isas", "isa-simulators", "quiz-isa"]),
    ("RISC vs CISC", [
        "risc-philosophy", "cisc-philosophy", "risc-vs-cisc", "when-risc-wins",
        "load-store-architecture-intro", "quiz-risc-vs-cisc"]),
    ("Introducing RISC-V", [
        "why-riscv-important", "riscv-history", "open-isa", "riscv-isa-not",
        "riscv-base-and-extensions", "riscv-naming", "rv32-vs-rv64", "riscv-ecosystem",
        "atomic-extension", "riscv-vs-arm", "qemu-spike", "quiz-intro-riscv"]),
    ("Instruction Formats & Encoding", [
        "instruction-format", "instruction-types", "r-type-format", "i-type-format",
        "s-type-format", "b-type-format", "u-and-j-type", "opcode-and-encoding",
        "opcode-funct", "opcode-field-extractor", "immediate-encoding",
        "riscv-immediate-builder", "riscv-instruction-decoder", "rv32i-instruction-simulator",
        "quiz-instruction-formats"]),
    ("Load/Store & Registers", [
        "what-is-load-store", "riscv-load", "riscv-store", "signed-vs-unsigned-loads",
        "memory-alignment", "alignment-requirements", "riscv-register-file",
        "x0-zero-register", "abi-register-names", "register-usage-analyzer",
        "caller-vs-callee-saved", "function-call-convention", "stack-pointer-and-frame",
        "effective-address", "floating-point-registers", "quiz-load-store",
        "quiz-riscv-registers"]),
    ("Buses & Interconnect", [
        "what-is-a-bus", "address-data-control-buses", "bus-width", "bus-arbitration",
        "synchronous-vs-asynchronous-buses", "system-bus-vs-on-chip", "modern-interconnects",
        "address-range-decoder", "address-space-and-decoding", "quiz-buses"]),
    ("I/O, MMIO & DMA", [
        "io-overview", "memory-mapped-io", "mmio-in-riscv", "mmio-vs-pmio",
        "port-mapped-io", "riscv-memory-map", "device-registers", "accessing-uart",
        "mmio-register-simulator", "what-is-dma", "dma-modes", "polling-vs-interrupts",
        "quiz-mmio-dma", "quiz-riscv-memory-io"]),
    ("Memory Hierarchy & Caches", [
        "memory-hierarchy", "levels-of-the-hierarchy", "locality-of-reference",
        "memory-wall", "sram-vs-dram", "volatile-vs-nonvolatile", "cache-vs-ram",
        "cache-memory", "cache-lines-and-blocks", "direct-mapped-cache", "set-associative",
        "write-policies", "replacement-policies", "hit-rate-miss-penalty", "amat",
        "cache-address-decoder", "memory-access-time", "quiz-memory-hierarchy",
        "quiz-cache-memory"]),
    ("Pipelining & Hazards", [
        "pipelining", "laundry-analogy", "five-stage-pipeline", "pipeline-registers",
        "pipeline-speedup", "pipeline-throughput", "stalls-and-bubbles", "pipeline-hazards",
        "structural-hazards", "data-hazards", "control-hazards", "load-use-hazard",
        "forwarding-bypassing", "hazard-detector", "compiler-scheduling-nops",
        "quiz-pipelining"]),
    ("Branch Prediction & ILP", [
        "why-branches-are-expensive", "static-branch-prediction", "dynamic-branch-prediction",
        "one-and-two-bit", "two-bit-predictor", "correlating-and-tournament",
        "branch-target-buffer", "branch-prediction-security", "speculative-execution",
        "ilp-and-superscalar", "in-order-vs-out-of-order", "quiz-branch-prediction"]),
    ("Virtual Memory", [
        "virtual-memory", "paging-fundamentals", "multi-level-page-tables", "the-tlb",
        "address-translation", "page-faults", "the-mmu", "sv39", "riscv-page-table-walk",
        "satp-register", "enabling-paging", "sfence-vma", "physical-memory-protection",
        "quiz-virtual-memory"]),
    ("Exceptions & Interrupts", [
        "interrupts-vs-exceptions", "interrupt-handling-riscv", "interrupt-priorities",
        "interrupt-vectoring", "interrupt-latency", "interrupt-check-in-the-cycle",
        "nested-interrupts", "timer-interrupts", "software-interrupts",
        "precise-vs-imprecise", "synchronous-vs-asynchronous-events", "direct-vs-vectored",
        "quiz-exceptions-interrupts"]),
    ("CSRs & Trap Handling", [
        "what-are-csrs", "csr-instructions", "mstatus-register", "mcause", "mepc-register",
        "mtvec-register", "mie-mip", "mtval-and-misa", "trap-cause-classifier",
        "riscv-trap-model", "trap-entry-sequence", "trap-delegation", "trap-vs-interrupt",
        "writing-a-trap-handler", "ecall-and-ebreak", "mret-sret", "context-save-restore",
        "syscall-path-riscv", "quiz-csrs", "quiz-trap-handling"]),
    ("Privilege Modes & OS Interface", [
        "why-privilege-modes", "machine-mode", "supervisor-mode", "user-mode",
        "privilege-transitions", "privilege-and-virtual-memory", "kernel-user-isolation",
        "os-hardware-contract", "process-vs-thread-state", "context-switch-mechanics",
        "scheduling-algorithms", "scheduler-metrics", "round-robin-scheduler",
        "quiz-privilege-modes", "quiz-os-hardware-interface"]),
    ("Multicore & Cache Coherence", [
        "why-multicore", "smp-vs-numa", "cache-coherence", "mesi-protocol",
        "snooping-vs-directory", "false-sharing", "memory-consistency",
        "memory-ordering-fence", "riscv-memory-model-rvwmo", "atomics-and-synchronization",
        "quiz-multicore-coherence"]),
    ("Boot Process & Firmware", [
        "power-on-reset", "boot-stages-overview", "bootloader-handoff", "multi-hart-boot",
        "opensbi", "sbi-and-firmware", "device-tree", "setting-up-stack-bss",
        "plic-and-clint", "bare-metal-hello-world", "quiz-boot-process"]),
    ("Performance & Capstone", [
        "performance-metrics", "throughput-vs-latency", "latency-bandwidth", "amdahls-law",
        "struct-packing", "building-a-mini-riscv-simulator", "systemc-tlm",
        "what-is-virtual-prototyping", "debugging-virtual-prototypes",
        "interview-architecture-review", "interview-riscv-review", "quiz-capstone"]),
]

VP_MODULES = [
    ("Embedded Systems Foundations", [
        "what-is-an-embedded-system", "microcontroller-vs-microprocessor", "what-is-firmware",
        "what-is-an-rtos", "bare-metal-vs-rtos", "embedded-development-workflow",
        "why-vp-matters-for-embedded", "quiz-embedded-systems-foundations"]),
    ("Introduction to Virtual Prototypes", [
        "what-is-a-virtual-prototype", "what-is-simulation", "components-of-a-vp",
        "vp-advantages", "vp-limitations", "vp-use-cases-industry", "why-companies-use-vps",
        "pre-silicon-software-development", "shift-left-with-vps", "vp-in-the-soc-flow",
        "quiz-intro-virtual-prototypes"]),
    ("VP vs RTL vs Hardware", [
        "what-is-rtl", "vp-vs-real-hardware", "can-vp-replace", "high-level-model-defined",
        "modeling-spectrum", "abstraction-and-detail-loss", "abstraction-levels",
        "speed-vs-accuracy-tradeoff", "which-is-faster-which-accurate",
        "quiz-vp-vs-rtl-vs-hardware"]),
    ("VP Architecture", [
        "system-design-for-a-vp", "platform-vs-soc", "platform-topology",
        "cpu-memory-bus-peripherals", "reusable-ip-models", "configurability",
        "quiz-vp-architecture"]),
    ("C++ for Modeling", [
        "why-cpp-for-modeling", "why-cpp-based-modeling", "classes-and-objects",
        "inheritance-and-virtual", "operator-overloading", "templates-basics",
        "pointers-and-references", "function-pointers-and-callbacks", "raii-and-lifetime",
        "namespaces-and-headers", "data-types-and-widths", "headers-and-translation-units",
        "compile-link-stages", "quiz-cpp-essentials"]),
    ("Build Systems & Toolchain", [
        "gcc-and-make", "makefile-fundamentals", "cross-compilation",
        "embedded-toolchain-overview", "static-vs-shared-libs", "debug-vs-release-builds",
        "dependency-ordering", "systemc-as-a-library", "linking-against-systemc",
        "topological-build-order", "quiz-build-systems"]),
    ("Linux Command Line", [
        "navigation-pwd-ls-cd", "files-mkdir-cp-mv-rm", "find-files", "viewing-cat-grep",
        "permissions-chmod", "processes-ps-top-kill", "path-env-and-man", "sudo-and-ssh",
        "quiz-linux-commands"]),
    ("Assembly & Machine Code", [
        "machine-code-vs-assembly", "opcode-and-operand", "branch-and-control-flow",
        "load-store-encoding", "fetch-decode-execute", "quiz-assembly-basics"]),
    ("The Stack & ABI", [
        "what-is-the-stack", "stack-frames", "stack-pointer-register", "push-and-pop",
        "call-stack-depth", "calling-conventions", "abi-overview", "cpu-registers",
        "program-counter-and-flags", "risc-v-registers-and-abi", "stack-overflow-and-corruption",
        "stack-simulation", "quiz-stack-and-abi"]),
    ("RISC-V Decode", [
        "risc-v-instruction-formats", "addressing-modes", "load-store-architecture",
        "sign-extension", "decode-r-type", "decode-i-type-immediate", "decode-branch-immediate",
        "instruction-field-decode", "register-decode-exercise", "building-a-tiny-iss",
        "fetch-execute-loop-model", "why-risc-v-for-vp", "quiz-risc-v-decode"]),
    ("Bit Manipulation for Hardware", [
        "bitwise-operators", "bit-masking-and-fields", "bit-field-modeling",
        "bit-tricks-for-hardware", "count-set-bits", "set-clear-toggle-bits",
        "extract-bitfield", "register-access-types", "quiz-bit-manipulation"]),
    ("Endianness & Byte Layout", [
        "big-vs-little-endian", "endianness-in-buses", "byte-halfword-word-access",
        "twos-complement", "binary-hex-decimal", "alignment-and-rounding", "structure-padding",
        "endianness-swap", "pack-unpack-bytes", "parse-hexdump", "hexdump-reading",
        "quiz-endianness"]),
    ("Memory & Address Maps", [
        "what-is-a-memory-model", "ram-rom-mmio", "the-address-map", "address-decoding",
        "address-map-overlap", "address-decode-exercise", "memory-aliasing-and-mirrors",
        "sparse-memory", "memory-mapped-registers", "loading-images-into-memory",
        "address-translation-math", "quiz-memory-and-address-maps"]),
    ("The Simulation Kernel", [
        "event-driven-simulation", "simulation-time", "what-is-a-delta-cycle",
        "delta-cycle-ordering", "evaluate-update-phases", "signal-update-semantics",
        "scheduler-phases", "elaboration-vs-simulation", "event-queue-simulation",
        "synchronization-points", "quiz-simulation-kernel"]),
    ("SystemC Fundamentals", [
        "what-is-systemc", "systemc-standard-history", "systemc-data-types", "sc-main-entry",
        "sc-time-and-units", "primitive-channels", "interfaces-and-channels",
        "first-systemc-model", "quiz-systemc-fundamentals"]),
    ("SystemC Modules", [
        "what-is-sc-module", "sc-ctor-macro", "module-hierarchy", "module-composition-patterns",
        "submodule-instantiation", "module-init-and-end-elab", "module-naming",
        "designing-a-module-interface", "member-data-and-state", "what-is-sc-port",
        "what-is-sc-signal", "what-is-sc-event", "signal-vs-event", "quiz-systemc-modules"]),
    ("SystemC Processes", [
        "what-are-systemc-processes", "sc-method-explained", "sc-thread-explained",
        "sc-cthread", "method-vs-thread", "wait-statement", "next-trigger",
        "process-state-machines", "common-process-pitfalls", "quiz-systemc-processes"]),
    ("Sensitivity & Events", [
        "static-sensitivity", "dynamic-sensitivity", "event-notification",
        "signal-vs-transaction", "quiz-sensitivity-events"]),
    ("RTL vs TLM", [
        "rtl-vs-tlm", "structural-vs-behavioral", "cycle-accurate-recap", "cycle-accurate-vs-at",
        "which-is-faster-which-accurate-recap", "quiz-rtl-vs-tlm"]),
    ("TLM-2.0 Fundamentals", [
        "what-is-tlm", "tlm2-overview", "generic-payload", "initiator-and-target-sockets",
        "b-transport", "nb-transport", "dmi", "debug-transport", "payload-extensions",
        "interoperability-layer", "routing-transactions", "transaction-routing",
        "why-tlm-is-faster", "quiz-tlm2-fundamentals"]),
    ("TLM Coding Styles", [
        "choosing-a-coding-style", "loosely-timed-style", "approximately-timed-style",
        "lt-vs-at", "phases-in-at", "temporal-decoupling", "quantum-keeper", "quantum-budget",
        "modeling-latency", "quiz-tlm-coding-styles"]),
    ("Buses & Interconnect", [
        "what-is-a-bus-model", "amba-axi-ahb", "bus-bridges", "interconnect-topologies",
        "arbitration", "cpu-bus-interface", "quiz-buses-and-interconnect"]),
    ("Peripherals & Registers", [
        "what-is-a-peripheral-model", "what-is-a-register-model", "register-spec-to-model",
        "register-callbacks", "register-dump", "peripheral-register-programming",
        "peripheral-state-machines", "w1c-register", "quiz-peripherals-and-registers"]),
    ("Embedded Peripherals", [
        "gpio-fundamentals", "i2c-protocol-basics", "spi-protocol-basics", "adc-and-pwm",
        "watchdog-timers", "hardware-timers-and-counters", "other-io-models",
        "quiz-embedded-peripherals"]),
    ("Interrupts, Timers & DMA", [
        "interrupts-in-a-vp", "interrupt-controller-model", "interrupt-priorities",
        "level-vs-edge-interrupts", "irq-delivery-to-cpu", "cpu-exceptions-and-traps",
        "virtual-timer", "virtual-dma", "clock-and-reset", "timer-tick", "dma-transfer",
        "fifo-simulation", "quiz-interrupts-timers-dma"]),
    ("The Virtual UART", [
        "virtual-uart-overview", "uart-serial-communication", "uart-register-interface",
        "uart-interrupts", "uart-driver-bringup", "tx-rx-fifos", "char-device-backends",
        "connecting-to-host-console", "uart-baud-divisor-calc", "quiz-virtual-uart"]),
    ("CPU Modeling", [
        "what-is-a-cpu-model", "iss-vs-cycle-accurate-cpu", "iss-step-simulation",
        "interpreted-vs-jit", "instruction-trace-from-cpu", "instruction-trace-analysis",
        "instruction-trace-parse", "integrating-external-iss", "software-on-a-model",
        "host-vs-target-execution", "quiz-cpu-modeling"]),
    ("Boot Flow", [
        "boot-flow-overview", "boot-rom-and-stages", "bootloader-role", "reset-vector",
        "platform-bring-up-order", "platform-assembly", "minimum-hardware-to-boot-linux",
        "kernel-handoff", "boot-checkpointing", "device-tree", "quiz-boot-flow"]),
    ("Co-Simulation", [
        "what-is-co-simulation", "co-sim-with-rtl", "co-sim-tooling-landscape", "iss-in-co-sim",
        "quiz-co-simulation"]),
    ("Debugging Virtual Prototypes", [
        "debugging-strategy", "debugging-software-hangs", "debugging-memory-access-bugs",
        "gdb-with-a-vp", "gdb-remote-stub", "trace-logging", "linux-not-booting",
        "interview-question-bank", "quiz-debugging-vps"]),
]

COURSES = [
    {
        "dir": "31-cpp-for-systems",
        "course": {
            "slug": "cpp-for-systems",
            "title": "C++ for Systems Programming",
            "summary": "Modern C++ from the ground up for systems work — memory, OOP, "
                       "RAII, templates, the STL, bit-level tricks, and concurrency.",
            "description": (
                "A deep, systems-oriented C++ course. Build a precise mental model of "
                "memory, pointers, object lifetime, and the rules that govern undefined "
                "behaviour, then layer on OOP, RAII, smart pointers, templates, the STL, "
                "and concurrency — all with the low-level detail systems engineers need."
            ),
            "difficulty": "advanced",
            "estimated_hours": 40,
            "order_index": 31,
        },
        "modules": CPP_MODULES,
    },
    {
        "dir": "33-computer-architecture-riscv",
        "course": {
            "slug": "computer-architecture-riscv",
            "title": "Computer Architecture with RISC-V",
            "summary": "From transistors and digital logic to pipelines, caches, virtual "
                       "memory, traps, and multicore — taught on the open RISC-V ISA.",
            "description": (
                "A ground-up tour of how a modern processor works, using RISC-V as the "
                "running example. Covers number systems, digital logic, the datapath, "
                "instruction encoding, pipelining and hazards, branch prediction, the "
                "memory hierarchy, virtual memory, traps and CSRs, privilege modes, "
                "multicore coherence, and the boot process."
            ),
            "difficulty": "advanced",
            "estimated_hours": 50,
            "order_index": 33,
        },
        "modules": ARCH_MODULES,
    },
    {
        "dir": "34-virtual-prototyping-systemc",
        "course": {
            "slug": "virtual-prototyping-systemc",
            "title": "Virtual Prototyping with SystemC & TLM-2.0",
            "summary": "Build SystemC/TLM-2.0 virtual platforms — modules, processes, the "
                       "simulation kernel, buses, peripherals, CPU models, and boot.",
            "description": (
                "Learn to build virtual prototypes of embedded SoCs with SystemC and "
                "TLM-2.0. Starts with embedded foundations and the modelling C++ you need, "
                "then covers the simulation kernel, modules and processes, TLM-2.0 sockets "
                "and coding styles, buses, peripherals, interrupts, a virtual UART, CPU "
                "models, boot flow, co-simulation, and debugging."
            ),
            "difficulty": "advanced",
            "estimated_hours": 50,
            "order_index": 34,
        },
        "modules": VP_MODULES,
    },
]


def read_title(path: Path, slug: str) -> str:
    """First markdown H1, else a title-cased slug."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip().rstrip("#").strip()
            if stripped and not stripped.startswith("#"):
                break
    except OSError:
        pass
    return slug.replace("-", " ").title()


def best_module(slug: str, modules: list[tuple[str, list[str]]]) -> int | None:
    """Index of the module whose longest matching pattern is a substring of slug."""
    best_idx: int | None = None
    best_len = 0
    for idx, (_title, patterns) in enumerate(modules):
        for pat in patterns:
            if pat in slug and len(pat) > best_len:
                best_len = len(pat)
                best_idx = idx
    return best_idx


def strip_prefix(slug: str) -> str:
    for pre in EXERCISE_PREFIXES:
        if slug.startswith(pre):
            return slug[len(pre):]
    return slug


def build_course(spec: dict) -> tuple[dict, dict]:
    course_dir = COURSES_DIR / spec["dir"]
    lessons_dir = course_dir / "lessons"
    modules = spec["modules"]

    # buckets[module_index] = list of lesson dicts
    buckets: dict[int, list[dict]] = {i: [] for i in range(len(modules))}
    extras: list[dict] = []
    report = {"course": spec["course"]["title"], "unmatched": [], "counts": {}}

    for md in sorted(lessons_dir.glob("*.md")):
        name = md.name
        if name.endswith(".prompt.md"):
            slug = name[: -len(".prompt.md")]
            ltype = "exercise"
            content_file = f"lessons/{name}"
            match_slug = strip_prefix(slug)
        else:
            slug = name[: -len(".md")]
            ltype = "quiz" if slug.startswith("quiz-") else "reading"
            content_file = f"lessons/{name}"
            match_slug = slug

        lesson = {
            "slug": slug,
            "title": read_title(md, slug),
            "type": ltype,
            "duration_minutes": DURATION[ltype],
            "content_file": content_file,
            "_rank": {"reading": 0, "exercise": 1, "quiz": 2}[ltype],
        }

        idx = best_module(match_slug, modules)
        if idx is None:
            extras.append(lesson)
            report["unmatched"].append(slug)
        else:
            buckets[idx].append(lesson)

    # Assemble ordered module list, dropping empty ones.
    out_modules = []
    order = 1
    for i, (title, _patterns) in enumerate(modules):
        items = buckets[i]
        if not items:
            continue
        items.sort(key=lambda l: (l["_rank"], l["title"].lower()))
        out_modules.append({
            "title": title,
            "order_index": order,
            "lessons": [_clean(l) for l in items],
        })
        report["counts"][title] = len(items)
        order += 1

    if extras:
        extras.sort(key=lambda l: (l["_rank"], l["title"].lower()))
        out_modules.append({
            "title": "Further Topics",
            "order_index": order,
            "lessons": [_clean(l) for l in extras],
        })
        report["counts"]["Further Topics"] = len(extras)

    data = {
        "subject": SYSTEMS_SUBJECT,
        "course": {**spec["course"], "is_published": True},
        "modules": out_modules,
    }
    return data, report


def _clean(lesson: dict) -> dict:
    return {
        "slug": lesson["slug"],
        "title": lesson["title"],
        "type": lesson["type"],
        "duration_minutes": lesson["duration_minutes"],
        "content_file": lesson["content_file"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate course.yaml for new courses.")
    parser.add_argument("--dry-run", action="store_true", help="Report only; write nothing.")
    args = parser.parse_args()

    print("=" * 72)
    print("  Generating course.yaml for directory courses without a manifest")
    print("=" * 72)

    for spec in COURSES:
        data, report = build_course(spec)
        total = sum(report["counts"].values())
        print(f"\n>>> {report['course']}  ({total} lessons, "
              f"{len(report['counts'])} modules)")
        for title, n in report["counts"].items():
            print(f"      {n:>3}  {title}")
        if report["unmatched"]:
            print(f"    !! {len(report['unmatched'])} unmatched -> 'Further Topics':")
            for slug in report["unmatched"]:
                print(f"         - {slug}")

        if not args.dry_run:
            out = COURSES_DIR / spec["dir"] / "course.yaml"
            out.write_text(
                yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
                encoding="utf-8",
            )
            print(f"    wrote {out.relative_to(COURSES_DIR.parents[1])}")

    print("\n" + "=" * 72)
    print("  Done." if not args.dry_run else "  Dry run — no files written.")
    print("=" * 72)


if __name__ == "__main__":
    main()
