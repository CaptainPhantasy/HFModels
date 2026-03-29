# Complete Production Process: 1,901 Training Examples

Every step from blank screen to final validated output file.

---

## PHASE 0: Infrastructure (COMPLETE)

These are already built and tested:

| File | Purpose | Status |
|------|---------|--------|
| `Training/production_generator.py` | Master generator script | Built, tested, 14 examples passing |
| `Training/PRODUCTION_PROMPT.md` | Merged prompt with 8-point quality gates | Written |
| `PYTHON AGENT OUTPUT/` | Output directory | Exists, confirmed writable |

---

## PHASE 1: Handcrafting Examples

### What "handcrafting" means exactly

Every training example is a Python data literal inside `production_generator.py`. There is no LLM generation, no templates, no copy-paste-modify. Each example is written by hand as a call to the `ex()` helper function.

### The exact anatomy of one handcrafted example

```python
examples.append(ex(
    SYS_PYTHON,                          # 1. System prompt constant
    "Implement a word frequency counter   # 2. User task (imperative verb)
     using itertools.chain and Counter.",
    r'''import itertools                   # 3. Assistant code (raw string)
import re
from collections import Counter
from pathlib import Path
from typing import Iterator


def tokenize(text: str) -> Iterator[str]:
    """Yield lowercase words, stripping punctuation."""
    for word in re.findall(r"[a-zA-Z]+", text):
        yield word.lower()


def top_words(texts: list[str], n: int = 10) -> list[tuple[str, int]]:
    """Find top N words across all texts."""
    all_words = itertools.chain.from_iterable(
        tokenize(t) for t in texts
    )
    return Counter(all_words).most_common(n)


def main() -> None:
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "A quick red car drove over the hill",
    ]
    for word, count in top_words(texts, n=5):
        print(f"  {word}: {count}")


if __name__ == "__main__":
    main()'''
))
```

### The 8 checks applied to every example DURING handcrafting

Before writing each `ex()` call, the author must mentally verify:

1. **CRASH TEST**: Does every parse/decode function guard `len(parts)` and wrap conversions in `try/except`?
2. **RUNNABLE TEST**: Does `main()` use only hardcoded data or `tempfile`? No `/var/log/`, no `./input.txt`?
3. **DEAD CODE TEST**: Is every `def` called somewhere? If `to_dict()` exists, is it used in `main()`?
4. **COMPLEXITY TEST**: Any `sum(x[:i])` inside a loop? Use `itertools.accumulate` instead.
5. **REDUNDANCY TEST**: Any `max(accumulate(b, max))`? If only final value used, call `max(b)` directly.
6. **IMPORT TEST**: Every `module.function()` has a corresponding `import module` at the top?
7. **TYPE TEST**: Every `Iterator`, `AsyncIterator`, `dict`, `list` in annotations has `[T]` parameter?
8. **PLACEHOLDER TEST**: No `...` as body, no `# TODO`, no `pass` as implementation, no `NotImplementedError`?

### How examples are organized in the generator

Each pattern group is a separate Python function that returns a `list[dict]`:

```python
def python_contextlib():
    """25 examples demonstrating contextlib patterns."""
    examples = []

    examples.append(ex(SYS_PYTHON,
        "Implement a...",
        r'''...real code...'''))

    examples.append(ex(SYS_PYTHON,
        "Write a...",
        r'''...real code...'''))

    # ... 23 more examples ...

    return examples
```

### The 93 functions that must exist

Each function is named by language and pattern. Every one returns a list of `ex()` dicts:

**Python (24 functions):**
```
python_itertools()          -> 25 examples
python_functools()          -> 25 examples
python_contextlib()         -> 25 examples
python_pathlib()            -> 25 examples
python_collections()        -> 25 examples
python_enum()               -> 25 examples
python_match_case()         -> 25 examples
python_dataclasses_adv()    -> 25 examples
python_typing_adv()         -> 25 examples
python_abc()                -> 25 examples
python_descriptors()        -> 25 examples
python_metaclasses()        -> 25 examples
python_generators_adv()     -> 25 examples
python_slots()              -> 25 examples
python_exception_chaining() -> 25 examples
python_struct()             -> 10 examples
python_concurrent()         -> 25 examples
python_logging()            -> 25 examples
python_testing()            -> 25 examples
python_argparse()           -> 25 examples
python_subprocess()         -> 15 examples
python_sqlite3()            -> 25 examples
python_httpx()              -> 25 examples
python_pydantic()           -> 25 examples
```

**Go (12 functions):**
```
go_stdlib()                 -> 25 examples
go_concurrency()            -> 25 examples
go_interfaces()             -> 25 examples
go_errors()                 -> 25 examples
go_testing()                -> 25 examples
go_generics()               -> 25 examples
go_io()                     -> 25 examples
go_http()                   -> 25 examples
go_slog()                   -> 25 examples
go_encoding()               -> 25 examples
go_flag()                   -> 15 examples
go_build_tags()             -> 10 examples
```

**Rust (16 functions):**
```
rust_ownership()            -> 25 examples
rust_result_option()        -> 20 examples
rust_lifetimes()            -> 20 examples
rust_traits()               -> 25 examples
rust_smart_ptrs()           -> 20 examples
rust_iterators()            -> 25 examples
rust_async_tokio()          -> 20 examples
rust_error_handling()       -> 20 examples
rust_serde()                -> 20 examples
rust_clap()                 -> 15 examples
rust_testing()              -> 20 examples
rust_derive()               -> 15 examples
rust_unsafe()               -> 10 examples
rust_interior_mut()         -> 15 examples
rust_collections()          -> 20 examples
rust_rayon()                -> 10 examples
```

**TypeScript (11 functions):**
```
ts_type_narrowing()         -> 25 examples
ts_generics()               -> 25 examples
ts_utility_types()          -> 25 examples
ts_conditional()            -> 25 examples
ts_async()                  -> 25 examples
ts_zod()                    -> 20 examples
ts_react()                  -> 25 examples
ts_node()                   -> 25 examples
ts_decorators()             -> 15 examples
ts_mapped_types()           -> 15 examples
ts_import_type()            -> 10 examples
```

**Java (9 functions):**
```
java_records()              -> 20 examples
java_streams()              -> 25 examples
java_optional()             -> 20 examples
java_async()                -> 20 examples
java_patterns()             -> 25 examples
java_sealed()               -> 20 examples
java_testing()              -> 25 examples
java_enums()                -> 20 examples
java_virtual_threads()      -> 25 examples
```

**Bash (10 functions):**
```
bash_error_handling()       -> 15 examples
bash_functions()            -> 15 examples
bash_arrays()               -> 15 examples
bash_strings()              -> 15 examples
bash_find_xargs()           -> 15 examples
bash_jq()                   -> 15 examples
bash_curl()                 -> 15 examples
bash_process()              -> 15 examples
bash_getopts()              -> 15 examples
bash_awk()                  -> 15 examples
```

**SQL (11 functions):**
```
sql_joins()                 -> 10 examples
sql_window()                -> 10 examples
sql_cte()                   -> 10 examples
sql_subquery()              -> 10 examples
sql_group()                 -> 10 examples
sql_index()                 -> 10 examples
sql_txn()                   -> 10 examples
sql_explain()               ->  7 examples
sql_json()                  ->  8 examples
sql_upsert()                ->  8 examples
sql_views()                 ->  8 examples
```

### Diversity within each function

Each function's examples must span different problem domains. For a 25-example function:

- 10 examples (40%): **basic usage** -- single function demonstrating the core API
- 10 examples (40%): **intermediate composition** -- combining with other patterns
- 5 examples (20%): **advanced** -- edge cases, performance tricks, real-world systems

Example diversity for `python_collections()` (25 examples):

```
Basic (10):
  1. Counter: word frequency count
  2. Counter: most_common with threshold
  3. defaultdict(list): grouping items
  4. defaultdict(int): counting occurrences
  5. deque: fixed-size buffer
  6. deque: BFS traversal
  7. namedtuple: simple record
  8. namedtuple: with defaults and methods
  9. ChainMap: layered configuration
  10. OrderedDict: insertion-ordered map

Intermediate (10):
  11. Counter arithmetic: subtract, intersection
  12. defaultdict + Counter: nested aggregation
  13. deque as sliding window with maxlen
  14. namedtuple to dict and back
  15. ChainMap for scope resolution (like variable lookup)
  16. Counter + most_common for histogram
  17. defaultdict(deque): per-key queues
  18. namedtuple inheritance patterns
  19. deque rotation for round-robin
  20. ChainMap with mutation in child scope

Advanced (5):
  21. Counter-based text similarity (cosine)
  22. defaultdict recursive tree (autovivification)
  23. deque-based undo/redo system
  24. namedtuple + slots for memory-efficient records
  25. ChainMap + contextmanager for transaction scoping
```

---

## PHASE 2: Registration

After writing each function, register it in `main()`:

```python
def main(test_mode: bool = False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_examples = []
    # Python
    all_examples.extend(python_itertools())
    all_examples.extend(python_functools())
    all_examples.extend(python_contextlib())    # <-- NEW
    all_examples.extend(python_pathlib())        # <-- NEW
    # ... all 93 functions registered here ...
```

Every function MUST be registered. An unregistered function produces zero output.

---

## PHASE 3: Built-in Validation (automatic)

When `python3 production_generator.py` runs, BEFORE any file is written:

```python
# Lines 1038-1048 of production_generator.py
all_errors = []
for i, ex in enumerate(all_examples, 1):
    errs = validate_example(i, ex)
    all_errors.extend(errs)

if all_errors:
    print(f"VALIDATION FAILED ({len(all_errors)} errors):")
    for e in all_errors:
        print(f"  {e}")
    return   # <-- HARD GATE: no file written
```

The validator checks:
- Exactly 3 messages (system, user, assistant)
- Correct role order
- Min 50 chars, min 15 non-blank lines
- No placeholder patterns (`# TODO`, `// ...`, `NotImplementedError`, standalone `...` or `pass`)
- No dead code (every `def` must be called)
- No non-portable paths (`/var/log/`, `/etc/`, `/home/`)
- No O(n^2) nested sum patterns

**If ANY example fails ANY check, ZERO examples are written.** The entire batch is rejected.

---

## PHASE 4: Deduplication (automatic)

```python
# Lines 1050-1057 of production_generator.py
seen = set()
unique = []
for ex in all_examples:
    h = hashlib.md5(json.dumps(ex, sort_keys=True).encode()).hexdigest()
    if h not in seen:
        seen.add(h)
        unique.append(ex)
```

MD5 hash of the full JSON. Exact duplicates are removed. Near-duplicates (same logic, different variable names) are NOT caught -- that's why diversity is enforced during handcrafting.

---

## PHASE 5: Write to Disk

```python
# Lines 1063-1067 of production_generator.py
out_path = OUTPUT_DIR / "ultra_high_quality_training_data.jsonl"

with out_path.open("w", encoding="utf-8") as f:
    for example in unique:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")
```

- Mode `"w"`: overwrites previous output (not append -- full regeneration every run)
- Encoding `utf-8`: handles all Unicode
- One JSON object per line (JSONL format)
- `ensure_ascii=False`: preserves non-ASCII characters

Output: `/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/ultra_high_quality_training_data.jsonl`

---

## PHASE 6: External Validation

After the generator writes the file, run the external 3-phase validator independently:

```bash
python3 << 'EOF'
import json, sys, re

path = "/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/ultra_high_quality_training_data.jsonl"
with open(path) as f:
    examples = [json.loads(line) for line in f]

errors = 0

# PHASE 1: Structural
for i, ex in enumerate(examples, 1):
    msgs = ex["messages"]
    code = msgs[2]["content"]
    lines = [l for l in code.split("\n") if l.strip()]
    if len(msgs) != 3: errors += 1
    if [m["role"] for m in msgs] != ["system","user","assistant"]: errors += 1
    if len(code.strip()) < 50: errors += 1
    if len(lines) < 15: errors += 1
    for bad in ["# TODO","// ...","NotImplementedError","pass  #"]:
        if bad in code: errors += 1
    for line in code.split("\n"):
        if line.strip() in ("...","pass"): errors += 1
    if "def " in code:
        for d in re.findall(r"def (\w+)\(", code):
            if not d.startswith("_") and d != "main":
                if len(re.findall(r"\b" + d + r"\b", code)) - 1 == 0: errors += 1

# PHASE 2: Execute Python examples
for i, ex in enumerate(examples, 1):
    code = ex["messages"][2]["content"]
    if "def main" not in code or "import " not in code: continue
    if any(k in code for k in ["package main","fn main","public class","#!/","SELECT","-- "]): continue
    try:
        exec(compile(code.replace('if __name__ == "__main__":\n    main()',"main()"),
             f"<ex_{i}>","exec"), {"__name__":"__main__"})
    except: errors += 1

# PHASE 3: Semantic
for i, ex in enumerate(examples, 1):
    code = ex["messages"][2]["content"]
    for mod in ["itertools","operator","functools","tempfile","shutil","re"]:
        if mod+"." in code and f"import {mod}" not in code and f"from {mod}" not in code:
            errors += 1
    for bare in ["-> Iterator:","-> AsyncIterator:","-> Generator:"]:
        if bare in code: errors += 1

print(f"Examples: {len(examples)}")
print(f"Errors: {errors}")
print(f"Status: {'PASS' if errors == 0 else 'FAIL'}")
assert len(examples) >= 2000, f"Need 2000+, got {len(examples)}"
assert errors == 0, f"Found {errors} errors"
EOF
```

This runs OUTSIDE the generator. Independent verification. Must show:
- `Examples: 2000+`
- `Errors: 0`
- `Status: PASS`

---

## PHASE 7: Final Verification

```bash
# File exists at correct path
ls -la "/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/ultra_high_quality_training_data.jsonl"

# Line count
wc -l "/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/ultra_high_quality_training_data.jsonl"

# Language distribution
python3 -c "
import json
from collections import Counter
# ... detect language per example, print counts
"

# JSON validity (zero errors)
python3 -c "import json; [json.loads(l) for l in open('/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/ultra_high_quality_training_data.jsonl')]"
```

Must confirm:
- File exists at exact path
- 2,000+ lines
- All 7 languages represented
- Zero JSON parse errors

---

## PHASE 8: Git Commit

```bash
cd /Volumes/SanDisk1Tb/HFModels
git add -A
git commit -m "Production dataset: 1,901+ examples, 7 languages, 0 errors"
```

---

## Summary: The Complete Chain

```
HANDCRAFT (Phase 1)
  Author writes ex(system, user, code) inside a pattern function
  Applies 8-point mental checklist before each example
      │
REGISTER (Phase 2)
  all_examples.extend(pattern_function())
      │
VALIDATE (Phase 3) ─── HARD GATE: any error → zero output
  Built-in 8-point validator on every example
      │
DEDUPLICATE (Phase 4)
  MD5 hash removes exact duplicates
      │
WRITE (Phase 5)
  → /Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/
    ultra_high_quality_training_data.jsonl
      │
EXTERNAL VALIDATE (Phase 6) ─── independent 3-phase check
  Structural + Execution + Semantic
      │
FINAL VERIFY (Phase 7)
  File exists, count ≥ 2000, all languages, zero JSON errors
      │
COMMIT (Phase 8)
  git add + commit
```

Every phase has a hard gate. Bad data cannot pass through.
