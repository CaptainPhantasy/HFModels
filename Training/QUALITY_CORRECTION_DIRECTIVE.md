# Quality Correction Directive

You generated 5 test examples. 3 of the 5 contain defects that violate the rules in `agent_buildout_prompt.md`. This directive gives you the exact defects, the exact rules they violate, and the exact fix patterns to apply -- not just to these 5 examples, but to ALL examples you generate going forward.

Read every word. These are not suggestions.

---

## Defect 1: Functions that crash on bad input

**What you did (Example 1, `LogEntry.parse`):**
```python
@classmethod
def parse(cls, line: str) -> 'LogEntry':
    parts = line.strip().split(maxsplit=3)
    ts = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S")
    return cls(timestamp=ts, level=parts[2], message=parts[3])
```

**What happens at runtime:**
- Input `"short"` -> `parts = ["short"]` -> `parts[1]` raises `IndexError`
- Input `"2024-03-29 bad_time INFO x"` -> `strptime` raises `ValueError`
- Input `"2024-03-29 10:15:30 WARN"` -> `parts[3]` raises `IndexError` (only 3 tokens)

**Rule violated:** "Real, executable code. Must run without modification."

Code that crashes on foreseeable input is not executable. A parse function WILL encounter malformed lines. If the function cannot handle them, it is broken.

**The fix pattern -- apply to ALL parsing/decoding functions you write:**
```python
@classmethod
def parse(cls, line: str) -> "LogEntry | None":
    """Parse '2024-03-29 10:15:30 INFO message'. Returns None on bad input."""
    parts = line.strip().split(maxsplit=3)
    if len(parts) < 4:
        return None
    try:
        ts = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return cls(timestamp=ts, level=parts[2], message=parts[3])
```

**The rule going forward:**
- Every function that parses external input (strings, files, JSON, network responses, user input, CLI args) MUST either return `None`/raise a typed exception on bad input, or validate before indexing.
- Never index into a list without checking its length first.
- Never call a conversion function (`strptime`, `int()`, `float()`, `json.loads`) without a `try/except` for the specific exception it raises.
- The caller must then filter: `if entry is not None: yield entry`

---

## Defect 2: `main()` functions that cannot run

**What you did (Example 1):**
```python
def main() -> None:
    log_dir = Path("/var/log/myapp")
    log_files = [
        log_dir / "app.log.1",
        log_dir / "app.log.2",
        log_dir / "app.log.3",
    ]
    for entry in merge_logs(*log_files):
        print(f"[{entry.timestamp}] {entry.level}: {entry.message}")
```

**What happens at runtime:**
- `/var/log/myapp` does not exist -> `FileNotFoundError` on the first `path.open()` call
- This example cannot run on ANY system without manual setup

**Rule violated:** "Must run without modification (aside from installing packages for non-stdlib examples)."

Creating nonexistent filesystem paths is not "installing packages." The example is dead on arrival.

**The fix pattern -- apply to ALL `main()` functions that need external data:**
```python
def main() -> None:
    import tempfile
    import shutil

    tmpdir = Path(tempfile.mkdtemp())
    try:
        # Create real sample data inline
        (tmpdir / "server.log").write_text(
            "2024-03-29 08:00:01 INFO Server started on port 8080\n"
            "2024-03-29 09:15:00 WARN High memory usage detected\n"
            "2024-03-29 10:15:01 ERROR Connection timeout to replica-3\n",
            encoding="utf-8",
        )
        (tmpdir / "access.log").write_text(
            "2024-03-29 07:45:00 INFO Health check passed\n"
            "malformed line without timestamp\n"
            "2024-03-29 09:00:00 INFO Backup completed successfully\n",
            encoding="utf-8",
        )

        merged = merge_logs(*sorted(tmpdir.glob("*.log")))
        for entry in merged:
            print(f"[{entry.timestamp:%H:%M:%S}] {entry.level:5s} {entry.message}")
    finally:
        shutil.rmtree(tmpdir)
```

**The rule going forward:**
- If `main()` needs files, databases, or network resources: create them inline with `tempfile`, hardcoded data, or `io.StringIO`. Clean up in a `finally` block.
- If `main()` demonstrates a pure function (math, data structures, algorithms): use hardcoded literals directly -- no filesystem needed.
- NEVER reference paths like `/var/log/`, `/etc/`, `/home/`, `/tmp/myapp/`, `~/data/`, `./input.txt`, or any path that does not exist on a clean machine.
- Test: imagine running `python3 example.py` on a brand-new machine with only Python installed. If it crashes, the example is broken.

---

## Defect 3: Dead code

**What you did (Example 4, `DeploymentConfig.to_dict`):**
```python
@dataclass(frozen=True)
class DeploymentConfig:
    environment: str
    region: str
    instance_type: str
    replicas: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "environment": self.environment,
            "region": self.region,
            "instance_type": self.instance_type,
            "replicas": self.replicas,
        }
```

`to_dict()` is defined but NEVER CALLED anywhere in the example. Not in `main()`. Not in any other function. It exists for no reason.

**Why this matters for training data:**
Dead code teaches the model to generate methods that nothing uses. When the fine-tuned model later generates code for a user, it will include unused methods -- bloating the output and confusing the user. Every line in a training example trains a habit. Dead code trains the habit of dead code.

**The fix pattern:**
- Before finishing any example, grep your own code: is every function/method called at least once?
- If a method exists, it must be exercised in `main()` or by another function in the example.
- If you cannot find a caller for it, delete it.

**Applied to Example 4:** Remove `to_dict()` entirely. The `@dataclass` already generates `__repr__` which is what `main()` uses to print.

---

## Defect 4: O(n^2) algorithms where O(n) is trivial

**What you did (Example 5, peak balance calculation):**
```python
balances = [initial] + [initial + sum(t.amount for t in transactions[:i+1])
                        for i in range(len(transactions))]
```

**What this does:**
- For `i=0`: sums 1 element
- For `i=1`: sums 2 elements
- For `i=2`: sums 3 elements
- ...
- For `i=n-1`: sums n elements
- Total operations: `1 + 2 + 3 + ... + n = n(n+1)/2 = O(n^2)`

This is in an example ABOUT `itertools.accumulate` -- a function that does exactly this in O(n). Using O(n^2) to recompute what accumulate gives you in O(n) is the opposite of what the example should teach.

**The fix:**
```python
all_balances = list(itertools.accumulate(
    [initial] + [t.amount for t in transactions], operator.add
))
```

One call to `accumulate`. O(n). Same result.

**The rule going forward:**
- In an example about `itertools.accumulate`, use `itertools.accumulate` for ALL cumulative computations. Do not hand-roll what the featured function does.
- More broadly: never use O(n^2) when O(n) is available and obvious. Training data that teaches O(n^2) patterns when O(n) exists trains the model to write slow code.

---

## Defect 5: Redundant computation that teaches the wrong lesson

**What you did (Example 5):**
```python
max_balance = max(itertools.accumulate(balances, max))
```

`itertools.accumulate(balances, max)` produces a running maximum: `[1000, 1500, 1500, 1530, 1530, ...]`. Then `max()` of that list returns the last element (since a running max is monotonically non-decreasing). This is identical to `max(balances)`.

Using `accumulate` + `max` to get a single number that `max` alone returns is not teaching `accumulate` -- it is teaching unnecessary complexity.

**The fix -- make accumulate-with-max earn its place:**
```python
# Peak balance via running high-water mark
all_balances = list(itertools.accumulate(
    [initial] + [t.amount for t in transactions], operator.add
))
running_peak = list(itertools.accumulate(all_balances, max))
print(f"Peak Balance: ${running_peak[-1]:.2f}")
print(f"High-water mark per step: {['${:.0f}'.format(b) for b in running_peak]}")
```

Now `running_peak` is printed per-step, showing the high-water mark OVER TIME -- information that `max(balances)` alone cannot give. The `accumulate(b, max)` call is justified because the intermediate values are used, not just the final one.

**The rule going forward:**
- Every function call must produce a result that is USED. If you call `accumulate(data, func)` but only use the final element, you should have called `func` directly.
- When demonstrating a function, show why the INTERMEDIATE results matter, not just the final value.

---

## Summary Checklist for Every Example You Generate

Before emitting any example, verify ALL of the following:

1. **Crash test**: Does every parse/decode function handle bad input without raising? Test mentally with: empty string, short string, wrong format, wrong type.
2. **Runnable test**: Can `python3 example.py` (or equivalent) run on a clean machine with only the language runtime installed? No filesystem paths, no running services, no prior state.
3. **Dead code test**: Is every function/method/class called at least once? If not, delete it.
4. **Complexity test**: Is there an O(n^2) loop where O(n) is available? Especially: nested `sum()` inside a list comprehension is almost always O(n^2).
5. **Redundancy test**: Does every intermediate computation get used? If you compute a list but only use the last element, you should have computed the scalar directly.
6. **Import test**: Is every module referenced in the code imported at the top?
7. **Type test**: Does every generic type have its type parameter? `Iterator[T]`, not bare `Iterator`.
8. **Placeholder test**: Search for `...`, `# TODO`, `pass`, `NotImplementedError`, `// ...`. If found, replace with real implementation.

If ANY check fails, fix the example before emitting it. Do not emit and hope for the best.
