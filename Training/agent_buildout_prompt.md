# Training Data Build-Out Agent Prompt

You are a data generation agent. Your job is to produce ChatML training examples to scale a coding assistant training dataset from 99 to 2,000+ examples (add 1,901+ examples).

## Current Dataset

Location: `Training/qwen_training_dataset.jsonl` (99 examples, 106KB)

**Existing infrastructure (already built -- do NOT recreate):**
- `Training/run_pipeline.py` -- Full 8-step pipeline: generate, merge, deduplicate, validate
- `Training/generate_deep_python.py` -- Python async, dataclass, typing, generators
- `Training/generate_multi_lang.py` -- Go, Rust, Java, Bash examples
- `Training/generate_anti_patterns.py` -- Anti-pattern examples
- `Training/generate_multi_turn.py` -- Multi-turn conversations
- `Training/generate_error_recovery.py` -- Error recovery examples

Your job is to **extend** these generators and create new ones for uncovered patterns. Do NOT overwrite existing scripts unless you are adding new functions to them.

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

**Current deep Python coverage:**
- typing (TypeVar, Protocol, Generic): 8
- decorators: 11
- async/await: 8
- dataclass: 7
- generators: 4
- abc (abstract): 2
- itertools/functools: 0
- context managers: 0
- metaclasses: 0
- descriptors: 0
- slots: 0
- enum: 0
- match/case (3.10+): 0
- exception chaining: 0
- pathlib: 0
- struct pattern matching: 0
- TypeGuard: 0
- ParamSpec: 0
- Concatenate: 0
- Unpack: 0

## What the Dataset Needs

This is a **coding agent**, not a chatbot. Every example must contain **real executable code**. No pseudocode. No narrative explanations pretending to be code.

### 1. Deep Python (target: +600 examples)

**Zero-coverage patterns that need 25-30 examples EACH:**
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
- `attrs` (attrib, frozen, factory, evolve)

### 2. Go (target: +300 examples)

- Standard library: `net/http`, `encoding/json`, `os`, `io`, `fmt`, `sync`, `context`
- Concurrency: goroutines, channels, select, WaitGroup, mutex, RWMutex, atomics
- Interfaces and type assertions
- Error handling: custom errors, `errors.Is`, `errors.As`, `fmt.Errorf` with `%w`
- Testing with `testing` package, table-driven tests
- Generics (Go 1.18+)
- `slices` package (Go 1.21+)
- File I/O: `os.ReadFile`, `os.WriteFile`, `filepath.Walk`
- `encoding/csv`, `encoding/xml`, `database/sql`
- HTTP server/client patterns
- `flag` package for CLI parsing
- `log/slog` (Go 1.21+)
- Build tags and platform-specific code

### 3. Rust (target: +300 examples)

- Ownership and borrowing patterns
- `Result<T, E>` and `Option<T>` chaining
- Lifetimes (explicit and elision)
- Traits and trait objects vs generics
- `impl Trait` for argument position
- Smart pointers: `Box`, `Rc`, `Arc`, `Cow`
- Iterators and `Iterator` trait implementation
- `async`/`await` with `tokio`
- Error handling: `thiserror`, `anyhow`
- Serde serialization/deserialization
- `clap` for CLI argument parsing
- Testing with `#[test]` and `#[tokio::test]`
- `#[derive]` macros
- `unsafe` patterns (when and why)
- Interior mutability (`Cell`, `RefCell`, `Mutex`)
- `Pin` and self-referential structs
- `std::collections` (HashMap, HashSet, BTreeMap, VecDeque)
- `rayon` for parallel iterators

### 4. TypeScript (target: +250 examples)

- Type narrowing (discriminated unions, type guards)
- Generic types and constraints (`<T extends X>`)
- Utility types (`Pick`, `Omit`, `Partial`, `Required`, `Record`, `ReturnType`)
- Template literal types
- Conditional types (`T extends X ? Y : Z`)
- Mapped types
- `as const` assertions
- `satisfies` operator
- `interface` vs `type` patterns
- `declare` module and ambient types
- Async patterns (Promise, async/await, AbortController)
- Zod or similar runtime validation
- React patterns (hooks, context, reducers)
- Node.js patterns (streams, workers, events)
- `tsconfig.json` configuration patterns
- Decorators (Stage 3)
- `import type` vs `import`

### 5. Java (target: +200 examples)

- Records (Java 17+)
- Sealed interfaces and pattern matching
- Stream API (collect, flatMap, reduce, groupingBy)
- `Optional<T>` patterns
- `CompletableFuture` for async operations
- `var` and type inference
- `try`-with-resources
- Records as DTOs
- Enum with fields and methods
- `StringTemplates` (Java 21+)
- Virtual threads (Java 21+)
- `Foreign Function & Memory API`
- Builder pattern with method chaining
- Observer pattern with `java.util.Observable`
- Testing with JUnit 5

### 6. Bash (target: +150 examples)

- Proper error handling (`set -euo pipefail`, `trap`)
- Functions with local variables (`local`)
- Arrays and associative arrays
- String manipulation (parameter expansion, sed, awk, tr)
- `find` with `-exec`, `-print0`, `xargs -0`
- `jq` for JSON processing
- `curl` for HTTP requests
- Process management (signals, wait, background jobs)
- `getopts` for argument parsing
- Here-docs and here-strings
- Arrays: map, filter, reduce patterns in pure bash
- Piping and redirection patterns
- `nc` / `socat` for network operations
- `awk` one-liners and programs

### 7. SQL (target: +101 examples)

- PostgreSQL: `SELECT`, `INSERT`, `UPDATE`, `DELETE` with JOINs
- Window functions (`ROW_NUMBER`, `RANK`, `LEAD`, `LAG`)
- CTEs (`WITH RECURSIVE`)
- Subqueries (correlated, lateral, exists)
- `GROUP BY` with `HAVING` and `ROLLUP`/`CUBE`
- Indexes (btree, gin, gist, partial, expression)
- Transactions (`BEGIN`, `SAVEPOINT`, `ROLLBACK TO`)
- `EXPLAIN ANALYZE` patterns
- JSON/JSONB operations
- Array operations
- `UPSERT` (`INSERT ... ON CONFLICT`)
- Materialized views
- Triggers and functions
- Schema migrations (ALTER TABLE patterns)
- Common Table Expressions for complex queries

**Per-language targets sum to 1,901, matching the total needed.**

## Quality Requirements

Every generated example must meet ALL of these criteria:

### Code Quality
- **Real, executable code**: Complete with all imports. Must run without modification (aside from installing packages for non-stdlib examples).
- **No placeholders**: Never `...`, `// rest of implementation`, `pass  # TODO`, `NotImplementedError`, or stub functions.
- **Complete implementations**: Every function body must have real logic. If a function is 3 lines, those 3 lines must do something real.
- **Correct type annotations**: All generic types must have type parameters (e.g., `AsyncIterator[T]`, not bare `AsyncIterator`).
- **All imports present**: If a function uses a module, that module must be imported.

### Code Length
- **Target: 30-150 lines per assistant response**. Short enough to fit in context, long enough to demonstrate real patterns.
- Minimum: 15 lines (below this, the example teaches too little).
- Maximum: 250 lines (above this, the example becomes noise for the model).

### Diversity
- Each pattern topic must cover **different problem domains**: web, data processing, systems, CLI, testing, file I/O, networking, embedded logic.
- Within a single pattern (e.g., `itertools`), vary the difficulty: 40% basic usage, 40% intermediate composition, 20% advanced/combined patterns.

### System Prompt Selection
Choose the system prompt that matches the example's domain:
- Python examples -> "You are a Python expert. Write idiomatic, performant Python using modern patterns."
- Systems code (Go, Rust) -> "You are a systems programmer. Write performant, idiomatic code for the target language."
- Backend/API code -> "You are a backend engineer. Design scalable, maintainable code patterns."
- SQL -> "You are a database expert. Write optimized, secure SQL queries."
- Bash -> "You are a DevOps engineer. Write robust shell scripts and automation."
- Security-sensitive code (auth, crypto, input validation) -> "You are a security-focused developer. Write code that prevents common vulnerabilities."
- Performance-critical code -> "You are a performance engineer. Optimize code for speed and memory efficiency."

## Output Format

Every example must be a **single JSON line** in this exact ChatML format:

```json
{"messages": [{"role": "system", "content": "<system prompt>"}, {"role": "user", "content": "<task description>"}, {"role": "assistant", "content": "<real executable code>"}]}
```

### Structural Rules:
1. Exactly **3 messages** per example: system, user, assistant. No more, no fewer.
2. System prompt: choose from the 7 variants above based on the example's domain.
3. User message: a specific coding task description (imperative verb, not a question). Examples: "Implement...", "Write...", "Create...", "Build...". NOT "How do I..." or "What is...".
4. Assistant message: **real, executable, import-complete code** -- never pseudocode.

### Example of GOOD quality (what to match):

```json
{"messages": [{"role": "system", "content": "You are a Python expert. Write idiomatic, performant Python using modern patterns."}, {"role": "user", "content": "Implement an async context manager for database connection pooling."}, {"role": "assistant", "content": "import asyncio\nfrom contextlib import asynccontextmanager\nfrom typing import AsyncIterator\nimport asyncpg\n\n@asynccontextmanager\nasync def get_pool(dsn: str) -> AsyncIterator[asyncpg.Pool]:\n    \"\"\"Async context manager that provides a connection pool.\"\"\"\n    pool = await asyncpg.create_pool(dsn, min_size=2, max_size=10)\n    try:\n        yield pool\n    finally:\n        await pool.close()\n\n\nasync def main() -> None:\n    async with get_pool(\"postgresql://user:pass@localhost/db\") as pool:\n        async with pool.acquire() as conn:\n            row = await conn.fetchrow(\"SELECT version()\")\n            print(row)\n\n\nif __name__ == \"__main__\":\n    asyncio.run(main())"}]}
```

Note: imports are complete, type annotation `AsyncIterator[asyncpg.Pool]` is fully parameterized, function semantics match the name, and the code includes a runnable `main()`.

### Examples of BAD quality (what to avoid):

**Pseudocode:**
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "1. Parse the input\n2. Build the graph\n3. Run BFS\n4. Return the result"}]}
```

**Incomplete implementation:**
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "def process(data):\n    # TODO: implement\n    pass"}]}
```

**Ellipsis placeholder:**
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "func handleRequest(w http.ResponseWriter, r *http.Request) {\n    // ... parse request\n    // ... validate input\n    // ... write response\n}"}]}
```

**Missing import:**
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "pool = asyncpg.create_pool(dsn)\nasync with pool.acquire() as conn:\n    await conn.execute(query)"}]}
```

All four of these are garbage. Do not produce anything like them.

## Output Location

The pipeline uses separate intermediate `.jsonl` files that `run_pipeline.py` merges, deduplicates, and validates into the final dataset.

**Do NOT append directly to `qwen_training_dataset.jsonl`.** Instead:

1. Each generator script produces a separate `.jsonl` file in `Training/`.
2. Register new source files in `run_pipeline.py`'s `source_files` list (line ~196).
3. Run `python3 Training/run_pipeline.py` to merge everything into the final dataset.

**Naming convention for new generator output files:**
- `Training/deep_python_itertools.jsonl`
- `Training/deep_python_collections.jsonl`
- `Training/go_concurrency.jsonl`
- `Training/rust_error_handling.jsonl`
- etc.

## Execution

1. **Audit** existing generators (`generate_deep_python.py`, `generate_multi_lang.py`) to understand patterns already covered. Do NOT duplicate.
2. **Extend** existing generators by adding new example functions for uncovered topics.
3. **Create** new generator scripts for topics not covered by existing scripts (e.g., `generate_sql.py`, `generate_typescript.py`).
4. **Run** each generator to produce its `.jsonl` output file.
5. **Register** all new `.jsonl` files in `run_pipeline.py`'s `source_files` list.
6. **Run** `python3 Training/run_pipeline.py` to merge, deduplicate, and validate.
7. **Validate** the final dataset with the structural validator below.

### Validation (must pass ALL checks):

```bash
# 1. JSON validity (zero parse errors)
python3 -c "import json; [json.loads(l) for l in open('Training/qwen_training_dataset.jsonl')]"

# 2. Structural validity (zero structural errors)
python3 -c "
import json, sys
errors = 0
with open('Training/qwen_training_dataset.jsonl') as f:
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

# 3. Count check (must be 2,000+)
python3 -c "
import json
count = sum(1 for l in open('Training/qwen_training_dataset.jsonl') if l.strip())
print(f'Total examples: {count}')
assert count >= 2000, f'Need 2000+, got {count}'
"
```

### Target: 2,000+ valid examples, zero JSON errors, zero structural errors, zero pseudocode.
