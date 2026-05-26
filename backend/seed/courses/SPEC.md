# Course authoring format — "Code with TLP"

This is the **single source of truth** for how a course is stored on disk so the
importer (`backend/seed/import_courses.py`) can load it into `studying_app.db`.

Read this whole file before writing any course.

## Data model (do not change names)

```
Subject  -> Course -> Module -> Lesson -> Exercise -> TestCase
```

- `Subject`  = a top-level area (e.g. "Systems"). Many courses share one subject.
- `Course`   = one course (what you build).
- `Module`   = a numbered section of the course.
- `Lesson`   = one page. `type` is one of: `reading`, `video`, `quiz`, `exercise`.
- `Exercise` = a stdin→stdout coding problem attached to a lesson (optional).
- `TestCase` = input/expected-output pair used to auto-grade an exercise.

## Folder layout (one folder per course)

```
backend/seed/courses/<NN>-<course-slug>/
  course.yaml                 # REQUIRED — metadata + full module/lesson/exercise tree
  lessons/
    <lesson-slug>.md          # one markdown file per lesson body
    <exercise-slug>.prompt.md  # (optional) exercise prompt body
```

- `<NN>` is the course `order_index` zero-padded to 2 digits (e.g. `05-operating-systems`).
- Every lesson's markdown body lives in its own `.md` file under `lessons/` and is
  referenced from `course.yaml` via `content_file:`.
- Put exercise prompts in their own `.prompt.md` file referenced via `prompt_file:`.
- Only write inside your own course folder. Never edit another course or any app code.

## course.yaml schema

```yaml
subject:
  slug: systems                      # lowercase-kebab, stable across courses
  name: Systems
  description: How computers run software, from the CPU up to the network.
  icon: server                       # lucide icon name
  color: "#ef4444"                   # hex, quoted
  order_index: 4

course:
  slug: operating-systems            # lowercase-kebab, globally unique
  title: Operating Systems
  summary: Processes, threads, scheduling, memory, and file systems.  # <= 200 chars
  description: |                      # 2-4 sentences, markdown allowed
    A hands-on tour of how an operating system manages processes, concurrency,
    memory, and storage. Builds the mental model every backend engineer needs.
  difficulty: advanced               # beginner | intermediate | advanced
  estimated_hours: 24
  is_published: true
  order_index: 5

modules:
  - title: Processes & Threads
    summary: How the OS represents and runs programs.
    order_index: 1
    lessons:
      - slug: what-is-a-process
        title: What is a Process?
        type: reading                # reading | video | quiz | exercise
        duration_minutes: 10
        content_file: lessons/what-is-a-process.md
        # exercises: optional list, only when a stdin->stdout problem makes sense
      - slug: process-scheduling-practice
        title: Round-Robin Scheduling
        type: exercise
        duration_minutes: 20
        content_file: lessons/process-scheduling-practice.md
        exercises:
          - slug: round-robin-scheduler
            title: Round-Robin Scheduler
            difficulty: medium       # easy | medium | hard
            points: 20
            prompt_file: lessons/round-robin-scheduler.prompt.md
            supported_languages: [python]   # subset of: python javascript typescript java csharp
            tags: [scheduling, simulation]
            time_limit_ms: 3000
            memory_limit_mb: 256
            starter_code:
              python: |
                import sys

                def solve():
                    data = sys.stdin.read().split()
                    # TODO
                solve()
            solution_code:
              python: |
                import sys

                def solve():
                    # full working reference solution
                    ...
                solve()
            test_cases:
              - name: case-1
                stdin: "3 2\n10 5 8\n"
                expected_stdout: "1 2 3 1 3 3"
                is_hidden: false
                weight: 1
              - name: case-2
                stdin: "1 4\n4\n"
                expected_stdout: "1"
                is_hidden: true
                weight: 1
```

## Hard rules (the importer / judge will break otherwise)

1. **YAML must parse.** Quote any string containing `:`, `#`, or starting with a
   special char. Use `|` block scalars for code and multi-line text.
2. **Enums are exact lowercase:** lesson `type` ∈ {reading, video, quiz, exercise};
   exercise `difficulty` ∈ {easy, medium, hard}; course `difficulty` ∈
   {beginner, intermediate, advanced}.
3. **Slugs** are `lowercase-kebab-case`, unique within their scope. Course and
   exercise slugs must be globally unique — prefix exercise slugs with a topic word
   to avoid clashes across courses.
4. **Exercises are stdin → stdout only.** The grader runs your code, pipes
   `test_cases[].stdin` to standard input, and compares trimmed standard output to
   `expected_stdout`. No file I/O, no network, no GUI.
5. **Pure standard library only.** The runner has plain Python / Node / Java / C# —
   NO numpy, pandas, requests, etc. If a topic needs heavy libs, make it a `reading`
   or `quiz` lesson instead of an exercise.
6. **Every exercise needs a correct `solution_code.python`** plus **3–6 test cases**
   (mix visible + hidden). The solution must actually produce each
   `expected_stdout`. Verify your test cases by hand before writing them.
7. **`expected_stdout` is compared after trimming trailing whitespace/newline.**
   Keep outputs simple and deterministic.
8. Lesson markdown files: start with an `#` H1 title, then rich content — short
   paragraphs, bullet lists, fenced code blocks with language hints, tables, and
   small worked examples. Aim for 250–700 words per reading lesson. Be accurate.

## Quiz lessons

For `type: quiz`, put the questions directly in the lesson's `.md` file using this
simple convention (the app renders markdown; no special parser needed):

```markdown
# Quiz: Memory Hierarchy

**Q1. Which is fastest to access?**
- [ ] Main memory (RAM)
- [x] L1 cache
- [ ] SSD
- [ ] Hard disk

**Q2. ...**
```

Mark the correct answer with `[x]`.

## Checklist before you finish

- [ ] `course.yaml` parses as valid YAML.
- [ ] Every `content_file` / `prompt_file` path exists under `lessons/`.
- [ ] Every lesson `type`, every `difficulty` uses an exact allowed value.
- [ ] Each exercise has a working pure-stdlib python solution and 3–6 test cases.
- [ ] No edits outside your own `backend/seed/courses/<NN>-<slug>/` folder.
