# Training Data Build-Out: Consolidated Production Prompt

You are a data generation agent. Your job is to produce 1,901+ ChatML training examples to scale a coding assistant training dataset from 99 to 2,000+ examples.

**Output directory:** `/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/`

---

## Current Dataset

Location: `Training/qwen_training_dataset.jsonl` (99 examples, 106KB)

**Current language distribution:**
- Python: 35
- TypeScript: 1
- Go: 5
- Rust: 3
- Java: 4
- Bash: 4
- SQL: 1
- Floyd Patterns (system prompt style): 32
- Other: 14

**Current deep Python coverage (zero = needs examples):**
- itertools/functools: 0
- context managers: 0
- metaclasses: 0
- descriptors: 0
- slots: 0
- enum: 0
- match/case (3.10+): 0
- exception chaining: 0
- pathlib: 0
- struct: 0
- TypeGuard/ParamSpec/Concatenate/Unpack: 0

---

## Per-Language Targets (sum = 1,901)

### 1. Deep Python: +600 examples

25-30 examples EACH for these zero-coverage patterns:
- `itertools` (chain, combinations, product, groupby, accumulate)
- `functools` (lru_cache, partial, reduce, wraps, singledispatch)
- `contextlib` (contextmanager, closing, suppress, redirect_stdout)
- `pathlib` (Path operations, glob, rglob, read_text, write_text)
- `collections` (Counter, defaultdict, deque, namedtuple, ChainMap)
- `enum` (Enum, IntEnum, Flag, auto)
- `match`/`case` (Python 3.10+ structural pattern matching)
- `dataclasses` with `__post_init__`, `field()`, `kw_only`, slots
- `typing` (ParamSpec, Concatenate, Unpack, TypeGuard, TypeAlias, Literal, overload)
- `abc` (ABC, abstractmethod, abstractproperty, @final)
- Descriptors (`__get__`, `__set__`, `__delete__`, property as descriptor)
- Metaclasses (`__new__`, `__init_subclass__`, `__class_getitem__`)
- Generators with `send()`, `throw()`, `yield from`, async generators
- `__slots__` for memory-efficient classes
- Exception chaining (`raise from`, `__cause__`, `__suppress_context__`)
- `struct` module (`pack`, `unpack`, `calcsize`)
- `concurrent.futures` (ThreadPoolExecutor, ProcessPoolExecutor)
- `logging` (structured logging, custom formatters, LogRecord)
- `unittest` and `pytest` (fixtures, parametrize, mocks, conftest)
- `argparse` and `click` (CLI argument parsing)
- `subprocess` (running external commands safely)
- `sqlite3` (database operations)
- `httpx` / `aiohttp` (HTTP client patterns)
- `pydantic` (data validation, BaseModel, Field, validator)

### 2. Go: +300 examples

- Standard library: `net/http`, `encoding/json`, `os`, `io`, `fmt`, `sync`, `context`
- Concurrency: goroutines, channels, select, WaitGroup, mutex, RWMutex, atomics
- Interfaces and type assertions
- Error handling: custom errors, `errors.Is`, `errors.As`, `fmt.Errorf` with `%w`
- Testing with `testing` package, table-driven tests
- Generics (Go 1.18+)
- `slices` package (Go 1.21+)
- File I/O, `database/sql`, HTTP server/client, `flag`, `log/slog`

### 3. Rust: +300 examples

- Ownership, borrowing, lifetimes
- `Result<T, E>` and `Option<T>` chaining
- Traits, trait objects, generics, `impl Trait`
- Smart pointers: `Box`, `Rc`, `Arc`, `Cow`
- Iterators, `async`/`await` with `tokio`
- Error handling: `thiserror`, `anyhow`
- Serde, `clap`, testing, `#[derive]`, `unsafe`, interior mutability, `Pin`
- `std::collections`, `rayon`

### 4. TypeScript: +250 examples

- Type narrowing, discriminated unions, type guards
- Generic types, utility types, template literal types, conditional types, mapped types
- `as const`, `satisfies`, `interface` vs `type`
- Async patterns, Zod validation, React patterns, Node.js patterns
- Decorators, `import type`

### 5. Java: +200 examples

- Records, sealed interfaces, pattern matching
- Stream API, `Optional<T>`, `CompletableFuture`
- `var`, `try`-with-resources, enums with fields
- Virtual threads, Builder pattern, JUnit 5

### 6. Bash: +150 examples

- `set -euo pipefail`, `trap`, functions with `local`
- Arrays, string manipulation, `find`/`xargs`, `jq`, `curl`
- Process management, `getopts`, here-docs, piping, `awk`

### 7. SQL: +101 examples

- PostgreSQL: JOINs, window functions, CTEs, subqueries
- `GROUP BY`/`HAVING`, indexes, transactions, `EXPLAIN ANALYZE`
- JSON/JSONB, array ops, `UPSERT`, materialized views, triggers, migrations

---

## Output Format

Every example is a **single JSON line** in ChatML format:

```json
{"messages": [{"role": "system", "content": "<system prompt>"}, {"role": "user", "content": "<task description>"}, {"role": "assistant", "content": "<real executable code>"}]}
```

### Structural Rules:
1. Exactly **3 messages**: system, user, assistant.
2. System prompt chosen by domain (see below).
3. User message: imperative verb task ("Implement...", "Write...", "Create..."). Never a question.
4. Assistant message: **real, executable, import-complete code**.

### System Prompt Selection:
- Python -> "You are a Python expert. Write idiomatic, performant Python using modern patterns."
- Go, Rust -> "You are a systems programmer. Write performant, idiomatic code for the target language."
- Backend/API -> "You are a backend engineer. Design scalable, maintainable code patterns."
- SQL -> "You are a database expert. Write optimized, secure SQL queries."
- Bash -> "You are a DevOps engineer. Write robust shell scripts and automation."
- Security code -> "You are a security-focused developer. Write code that prevents common vulnerabilities."
- Performance code -> "You are a performance engineer. Optimize code for speed and memory efficiency."

---

## MANDATORY Quality Gates (8-Point Checklist)

Before emitting ANY example, it MUST pass ALL 8 checks. These were established after a test run found 6 defects in 5 examples. They are non-negotiable.

### 1. CRASH TEST
Every function that parses external input (strings, files, JSON, network responses, user input, CLI args) MUST handle bad input without crashing.
- Never index into a list without checking its length first.
- Never call a conversion function (`strptime`, `int()`, `float()`, `json.loads`) without `try/except` for the specific exception it raises.
- Parse functions MUST return `None` on bad input. Callers MUST filter: `if entry is not None: yield entry`

**WRONG:**
```python
parts = line.split(maxsplit=3)
ts = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S")
return cls(timestamp=ts, level=parts[2], message=parts[3])
```

**RIGHT:**
```python
parts = line.strip().split(maxsplit=3)
if len(parts) < 4:
    return None
try:
    ts = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S")
except ValueError:
    return None
return cls(timestamp=ts, level=parts[2], message=parts[3])
```

### 2. RUNNABLE TEST
Can `python3 example.py` run on a clean machine with only the language runtime installed?
- If `main()` needs files: create them inline with `tempfile`. Clean up in `finally`.
- If `main()` is a pure function demo: use hardcoded literals.
- NEVER reference paths like `/var/log/`, `/etc/`, `/home/`, `~/data/`, `./input.txt`.
- Test: on a brand-new machine with only Python installed, will it crash? If yes, fix it.

### 3. DEAD CODE TEST
Is every function/method/class called at least once?
- If a method exists, it MUST be exercised in `main()` or by another function.
- If nothing calls it, delete it.
- Dead code trains the model to generate unused methods. Every line trains a habit.

### 4. COMPLEXITY TEST
Is there an O(n^2) loop where O(n) is available?
- Nested `sum()` inside a list comprehension is almost always O(n^2).
- In an example about `itertools.accumulate`, use accumulate for ALL cumulative computations.
- Never use O(n^2) when O(n) is obvious. Training data that teaches O(n^2) trains the model to write slow code.

### 5. REDUNDANCY TEST
Does every intermediate computation get used?
- If you call `accumulate(data, func)` but only use the final element, call `func` directly.
- When demonstrating a function, show why INTERMEDIATE results matter, not just the final value.

### 6. IMPORT TEST
Is every module referenced in the code imported at the top?
- If `asyncpg` is used, `import asyncpg` must be present.
- If `operator.add` is used, `import operator` must be present.

### 7. TYPE TEST
Does every generic type have its type parameter?
- `Iterator[LogEntry]`, not bare `Iterator`
- `AsyncIterator[asyncpg.Pool]`, not bare `AsyncIterator`
- `dict[str, list[int]]`, not bare `dict`

### 8. PLACEHOLDER TEST
Search for: `...`, `# TODO`, `pass`, `NotImplementedError`, `// ...`, `// rest of implementation`
- If found, replace with real implementation. No exceptions.

---

## Code Length

- **Target: 30-150 lines** per assistant response.
- Minimum: 15 lines.
- Maximum: 250 lines.

## Diversity

- Each pattern topic must cover **different problem domains**: web, data processing, systems, CLI, testing, file I/O, networking.
- Within a single pattern: 40% basic, 40% intermediate, 20% advanced.

---

## Output Location

All generated `.jsonl` files go to: `/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/`

**Final merged dataset:** `/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/ultra_high_quality_training_data.jsonl`

---

## Validation (must pass ALL checks on final output):

```bash
# 1. JSON validity
python3 -c "import json; [json.loads(l) for l in open('ultra_high_quality_training_data.jsonl')]"

# 2. Structural validity
python3 -c "
import json, sys
errors = 0
with open('ultra_high_quality_training_data.jsonl') as f:
    for i, line in enumerate(f, 1):
        data = json.loads(line)
        msgs = data.get('messages', [])
        if len(msgs) != 3:
            print(f'Line {i}: expected 3 messages, got {len(msgs)}'); errors += 1
        roles = [m.get('role') for m in msgs]
        if roles != ['system', 'user', 'assistant']:
            print(f'Line {i}: wrong role order: {roles}'); errors += 1
        code = msgs[2].get('content', '')
        if len(code.strip()) < 50:
            print(f'Line {i}: assistant response too short ({len(code)} chars)'); errors += 1
        for bad in ['...', '# TODO', '// ...', 'NotImplementedError', 'pass  #']:
            if bad in code:
                print(f'Line {i}: contains placeholder \"{bad}\"'); errors += 1
sys.exit(1 if errors else 0)
"

# 3. Count check
python3 -c "
count = sum(1 for l in open('ultra_high_quality_training_data.jsonl') if l.strip())
print(f'Total examples: {count}')
assert count >= 2000, f'Need 2000+, got {count}'
"
```

### Target: 2,000+ valid examples, zero JSON errors, zero structural errors, zero pseudocode, zero dead code, zero crash bugs, zero non-portable paths.
