#!/usr/bin/env python3
"""
Generate error recovery chain training examples.
Model encounters errors, diagnoses, self-corrects within conversation.
"""
import json
from pathlib import Path


SYSTEM_PROMPT = (
    "You are an elite live coding assistant. You strictly adhere to "
    "canonical patterns. When errors occur: diagnose first, fix second. "
    "Never assume the error is what it appears to be. Trace to root cause."
)


def make_record(system_prompt: str, messages: list) -> dict:
    return {"messages": [{"role": "system", "content": system_prompt}] + messages}


ERROR_RECOVERY_EXAMPLES = [

    # -------------------------------------------------------------------------
    # 1. Type error after edit - self-correct
    # -------------------------------------------------------------------------
    {
        "id": "error_001_type_mismatch",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Add a sanitizeHtml function that takes a string and returns a sanitized string."},
            {"role": "assistant", "content": "Writing the function:\n```typescript\nexport function sanitizeHtml(input: string): string {\n  return input.replace(/</g, '&lt;').replace(/>/g, '&gt;');\n}\n```"},
            {"role": "assistant", "content": "Editing src/utils/sanitize.ts..."},
            {"role": "tool_result", "content": "Error: Type 'string' is not assignable to type 'ReturnType<string>'. src/utils/sanitize.ts:3"},
            {"role": "assistant", "content": "Type error on return type. Let me read the file to see the full context."},
            {"role": "tool_result", "content": "// src/utils/sanitize.ts\nexport function sanitizeHtml(input: string): ReturnType<string> {\n  return input.replace(/</g, '&lt;').replace(/>/g, '&gt;');\n}\n```"},
            {"role": "assistant", "content": "I wrote `ReturnType<string>` which is nonsensical - `ReturnType<string>` resolves to `any`. The correct return type is `string` since `.replace()` always returns a string.\n\nFixing:\n```typescript\nexport function sanitizeHtml(input: string): string {\n  return input.replace(/</g, '&lt;').replace(/>/g, '&gt;');\n}\n```"},
            {"role": "tool_result", "content": "Build successful."},
            {"role": "assistant", "content": "Error resolved. Root cause: incorrect return type annotation. Lesson: `.replace()` always returns `string`."}
        ]
    },

    # -------------------------------------------------------------------------
    # 2. Test failure after refactor - analyze and fix
    # -------------------------------------------------------------------------
    {
        "id": "error_002_test_failure",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "The tests are failing after the UserService refactor."},
            {"role": "tool_result", "content": "FAIL src/tests/user_service.test.ts\n  expect(received).toBe(expected)\n\n  Expected: {\"id\": \"user-1\", \"email\": \"alice@example.com\"}\n  Received: undefined"},
            {"role": "assistant", "content": "Test fails - method returns undefined for a user that should exist. Let me trace the execution."},
            {"role": "tool_result", "content": "src/services/user_service.ts:\nfindById(id: string): User | undefined {\n  return this.users.find(u => u.id === id);\n}\n\nsrc/tests/user_service.test.ts:\nconst service = new UserService();\nconst user = service.findById('user-1');\nexpect(user).toBeDefined();  // FAILS - user is undefined"},
            {"role": "assistant", "content": "The method is correct. The issue is the test setup - `this.users` is an empty array. The UserService was instantiated without mock data.\n\nFixing the test setup:\n```typescript\nconst service = new UserService();\nservice.users = [\n  { id: 'user-1', email: 'alice@example.com' }\n];\nconst user = service.findById('user-1');\nexpect(user).toBeDefined();\n```"},
            {"role": "tool_result", "content": "PASS  src/tests/user_service.test.ts\n  3/3 tests passing"},
            {"role": "assistant", "content": "Test fixed. Root cause: missing mock data in test setup, not a code bug. Error resolution: found the actual problem was in the test, not the source."}
        ]
    },

    # -------------------------------------------------------------------------
    # 3. Build cascade - group by root cause
    # -------------------------------------------------------------------------
    {
        "id": "error_003_cascade",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Run the build."},
            {"role": "tool_result", "content": "error TS2307: Cannot find module '../utils/helpers'\nerror TS2307: Cannot find module '../utils/helpers'\nerror TS2305: Cannot find name 'formatDate'\nerror TS2305: Cannot find name 'formatDate'\nerror TS2305: Cannot find name 'formatDate'"},
            {"role": "assistant", "content": "5 errors across 3 files. Pattern recognition: 2 unique error types.\n\nGrouping by root cause:\n1. TS2307: Cannot find module '../utils/helpers' - 2 files\n2. TS2305: Cannot find name 'formatDate' - 3 files\n\nRoot cause hypothesis: `helpers.ts` was renamed but imports weren't updated."},
            {"role": "tool_result", "content": "ls src/utils/ | grep help"},
            {"role": "assistant", "content": "`helpers.ts` does not exist. Let me find what it's called now."},
            {"role": "tool_result", "content": "src/utils/datetime.ts\nsrc/utils/string.ts"},
            {"role": "assistant", "content": "`helpers.ts` split into `datetime.ts` and `string.ts`. `formatDate` is in `datetime.ts`.\n\nFixing imports in both files..."},
            {"role": "tool_result", "content": "Build successful. 0 errors."},
            {"role": "assistant", "content": "Cascade resolved. 5 errors fixed by updating 2 import statements. Root cause: file rename not propagated to importers."}
        ]
    },

    # -------------------------------------------------------------------------
    # 4. Wrong approach - recognize and switch
    # -------------------------------------------------------------------------
    {
        "id": "error_004_wrong_approach",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Implement a debounce function for API calls."},
            {"role": "assistant", "content": "Writing a custom debounce implementation:\n```typescript\nfunction debounce<T extends (...args: any[]) => any>(\n  fn: T,\n  delay: number\n): (...args: Parameters<T>) => void {\n  let timeoutId: ReturnType<typeof setTimeout>;\n  return (...args) => {\n    clearTimeout(timeoutId);\n    timeoutId = setTimeout(() => fn(...args), delay);\n  };\n}\n```"},
            {"role": "tool_result", "content": "Implementation complete."},
            {"role": "assistant", "content": "Let me verify edge cases..."},
            {"role": "tool_result", "content": "Edge case issue: If fn is called after clearTimeout but before the timeout fires, there's a race condition. Also missing: cancel method, leading/trailing options.\n\nRecognizing: Custom implementation is getting complex. This is a solved problem. Lodash debounce handles all these edge cases."},
            {"role": "assistant", "content": "**Switching approach:**\nUsing lodash debounce instead. It's battle-tested and handles all edge cases.\n\n```typescript\nimport debounce from 'lodash/debounce';\n\nconst debouncedFetch = debounce(\n  (url: string) => fetch(url),\n  300,\n  { leading: false, trailing: true }\n);\n\nexport { debouncedFetch };\n```"},
            {"role": "assistant", "content": "Approach corrected. Custom implementation had edge cases. Lodash debounce is the correct solution."}
        ]
    },

    # -------------------------------------------------------------------------
    # 5. Completion Fortress rejection - address quality gaps
    # -------------------------------------------------------------------------
    {
        "id": "error_005_fortress_reject",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Mark the user service as complete."},
            {"role": "assistant", "content": "**Completion Fortress: Quality Gate**\n\nScoring against thresholds:\n- correctness: 0.95 (tests pass)\n- security: 0.60 (NOT MET - no input validation on email)\n- performance: 0.90\n- test_coverage: 0.75 (NOT MET - only happy path tested)\n\n**BLOCKED: 2 dimensions below threshold**"},
            {"role": "assistant", "content": "Security gap: `createUser` accepts any string for email without validation.\nTest gap: no tests for edge cases (empty string, duplicate email)."},
            {"role": "assistant", "content": "Addressing security gap:\n```typescript\nasync createUser(email: string, name: string): Promise<User> {\n  if (!email || !email.includes('@')) {\n    throw new ValidationError('Invalid email format');\n  }\n  if (await this.emailExists(email)) {\n    throw new ValidationError('Email already registered');\n  }\n  // ... rest of implementation\n}\n```"},
            {"role": "assistant", "content": "Addressing test gap:\n```typescript\ntest('rejects invalid email', () => {\n  const service = new UserService();\n  expect(() => service.createUser('not-an-email', 'Bob'))\n    .toThrow(ValidationError);\n});\n\ntest('rejects duplicate email', async () => {\n  // ... setup existing user ...\n  expect(() => service.createUser('alice@example.com', 'Bob'))\n    .toThrow(ValidationError);\n});\n```"},
            {"role": "tool_result", "content": "Tests: 5/5 passing. Coverage: 88%."},
            {"role": "assistant", "content": "**Completion Fortress: PASSED**\n- security: 0.92 >= 0.90\n- test_coverage: 0.88 >= 0.80\n\nTask marked complete. Both blocking dimensions addressed."}
        ]
    },

    # -------------------------------------------------------------------------
    # 6. Silent failure - caught by verification
    # -------------------------------------------------------------------------
    {
        "id": "error_006_silent_fail",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Write a function that validates credit card numbers using the Luhn algorithm."},
            {"role": "assistant", "content": "Writing the Luhn validator:\n```typescript\nexport function isValidCard(cardNumber: string): boolean {\n  const digits = cardNumber.replace(/\\D/g, '');\n  let sum = 0;\n  let isEven = false;\n  for (let i = digits.length - 1; i >= 0; i--) {\n    let digit = parseInt(digits[i], 10);\n    if (isEven) {\n      digit *= 2;\n      if (digit > 9) digit -= 9;\n    }\n    sum += digit;\n    isEven = !isEven;\n  }\n  return sum % 10 === 0;\n}\n```"},
            {"role": "assistant", "content": "Verifying with known test values..."},
            {"role": "tool_result", "content": "isValidCard('4532015112830366')  // Expected: true\nisValidCard('4532015112830367')  // Expected: false (wrong check digit)"},
            {"role": "assistant", "content": "FAIL - the second card (wrong check digit) also returned true. The algorithm is wrong.\n\nTracing through: when doubling 6 -> 12 -> subtract 9 = 3. The math is correct. Let me check the input parsing..."},
            {"role": "assistant", "content": "Found the bug: `parseInt` is parsing `'0'` as `0` which is falsy, causing incorrect behavior in the loop. Also, the `isEven` toggle is inverted from standard Luhn.\n\nCorrected implementation:\n```typescript\nexport function isValidCard(cardNumber: string): boolean {\n  const digits = cardNumber.replace(/\\D/g, '');\n  if (digits.length < 13 || digits.length > 19) return false;\n  \n  let sum = 0;\n  for (let i = 0; i < digits.length; i++) {\n    let digit = parseInt(digits[digits.length - 1 - i], 10);\n    if (i % 2 === 1) {\n      digit *= 2;\n      if (digit > 9) digit -= 9;\n    }\n    sum += digit;\n  }\n  return sum % 10 === 0;\n}\n```"},
            {"role": "tool_result", "content": "PASS: isValidCard('4532015112830366') = true\nPASS: isValidCard('4532015112830367') = false"},
            {"role": "assistant", "content": "Silent failure avoided. The first implementation compiled but produced incorrect output. Verification caught it."}
        ]
    },

    # -------------------------------------------------------------------------
    # 7. Null deref - caught by Predictive Analyzer
    # -------------------------------------------------------------------------
    {
        "id": "error_007_null_deref",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Write a function that gets the user's display name from a nested object."},
            {"role": "assistant", "content": "Writing the accessor function:\n```typescript\nfunction getDisplayName(user: { profile?: { name?: string } }): string {\n  return user.profile.name.toUpperCase();\n}\n```"},
            {"role": "assistant", "content": "**Predictive Analyzer: Pre-execution analysis**\n\nNULL DEREFERENCE RISK: `user.profile.name.toUpperCase()`\n- `user.profile` is optional (`?`)\n- `user.profile.name` is optional (`?`)\n\nIf either is undefined, this throws `TypeError: Cannot read property 'name' of undefined`."},
            {"role": "assistant", "content": "Fixing null deref:\n```typescript\nfunction getDisplayName(user: { profile?: { name?: string } }): string {\n  if (!user?.profile?.name) {\n    return 'Anonymous';\n  }\n  return user.profile.name.toUpperCase();\n}\n```"},
            {"role": "assistant", "content": "Null deref prevented. Optional chaining with fallback value. Safe to execute."}
        ]
    },

    # -------------------------------------------------------------------------
    # 8. N+1 query - caught by analysis
    # -------------------------------------------------------------------------
    {
        "id": "error_008_n_plus_one",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Write a function that gets all users with their role names."},
            {"role": "assistant", "content": "Writing the function:\n```typescript\nasync function getUsersWithRoles(): Promise<UserWithRole[]> {\n  const users = await db.query('SELECT * FROM users');\n  const result: UserWithRole[] = [];\n  for (const user of users) {\n    const role = await db.query(\n      'SELECT name FROM roles WHERE id = ?',\n      [user.role_id]\n    );\n    result.push({ ...user, roleName: role.name });\n  }\n  return result;\n}\n```"},
            {"role": "assistant", "content": "**Predictive Analyzer: Performance profiling**\n\nN+1 QUERY DETECTED:\n- 1 query to get all users\n- N queries (one per user) to get each role\n- For 1000 users: 1001 queries total\n\nThis is a performance anti-pattern."},
            {"role": "assistant", "content": "Fixing with a JOIN:\n```typescript\nasync function getUsersWithRoles(): Promise<UserWithRole[]> {\n  const rows = await db.query(`\n    SELECT u.id, u.email, r.name as roleName\n    FROM users u\n    JOIN roles r ON u.role_id = r.id\n  `);\n  return rows;\n}\n```"},
            {"role": "assistant", "content": "Fixed: 2 queries total regardless of user count. N+1 eliminated."}
        ]
    },

    # -------------------------------------------------------------------------
    # 9. Regex mistake - caught by test
    # -------------------------------------------------------------------------
    {
        "id": "error_009_regex",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Write a function that validates US phone numbers."},
            {"role": "assistant", "content": "Writing phone validator:\n```typescript\nexport function isValidPhone(phone: string): boolean {\n  return /^\\d{3}-\\d{4}-\\d{4}$/.test(phone);\n}\n```"},
            {"role": "assistant", "content": "Verifying with edge cases..."},
            {"role": "tool_result", "content": "Test: isValidPhone('555-1234-5678') = true  // Should be valid\nTest: isValidPhone('(555) 123-4567') = true  // Should be valid\nTest: isValidPhone('5551234567') = true     // Should be valid"},
            {"role": "assistant", "content": "FAIL - 2 of 3 valid formats rejected. The regex only accepts `###-####-####` format.\n\nUS phone numbers have multiple valid formats. The regex is too restrictive."},
            {"role": "assistant", "content": "Fixed with flexible regex:\n```typescript\nexport function isValidPhone(phone: string): boolean {\n  const cleaned = phone.replace(/[\\s\\-\\(\\)]/g, '');\n  return /^\\d{10}$/.test(cleaned) || /^\\d{11}$/.test(cleaned);\n}\n```\nNormalizes common formats first, then checks digit count."},
            {"role": "tool_result", "content": "PASS: all 3 formats validated correctly"},
            {"role": "assistant", "content": "Regex error corrected. Lesson: normalize input before matching, not every format as a separate pattern."}
        ]
    },

    # -------------------------------------------------------------------------
    # 10. Off-by-one - caught by boundary test
    # -------------------------------------------------------------------------
    {
        "id": "error_010_off_by_one",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Write a function that gets the first N items from an array."},
            {"role": "assistant", "content": "Writing take function:\n```typescript\nexport function take<T>(arr: T[], n: number): T[] {\n  return arr.filter((_, i) => i < n);\n}\n```"},
            {"role": "assistant", "content": "Testing boundary cases..."},
            {"role": "tool_result", "content": "take([1,2,3,4,5], 3) = [1,2,3]  // PASS\ntake([1,2], 3) = [1,2]        // PASS\ntake([], 3) = []               // PASS\ntake([1,2,3], 0) = [1,2,3]    // FAIL - should be []"},
            {"role": "assistant", "content": "Off-by-one error: `i < n` should be `i >= 0 && i < n` but actually the filter approach is wrong. When n=0, the condition `i < 0` is always false, so nothing should be filtered. But the test shows [1,2,3]...\n\nWait - the condition is `i < n`. For n=0, this is `i < 0` which is never true. Filter should return empty. Let me re-read the test output."},
            {"role": "tool_result", "content": "The test was wrong. Let me re-check:\ntake([1,2,3], 0) should return []\nActual output: [1,2,3]\n\nThe filter is returning everything, which means n is not 0. Test setup issue."},
            {"role": "assistant", "content": "Confirmed: test had incorrect setup. Function is correct. Returning empty array when n=0 would be:\n```typescript\nexport function take<T>(arr: T[], n: number): T[] {\n  if (n <= 0) return [];\n  return arr.slice(0, n);\n}\n```\nUsing slice instead of filter - more idiomatic and O(1) not O(n)."},
            {"role": "tool_result", "content": "take([1,2,3,4,5], 3) = [1,2,3]\ntake([1,2], 3) = [1,2]\ntake([], 3) = []\ntake([1,2,3], 0) = []\n\nAll tests passing."},
            {"role": "assistant", "content": "Off-by-one avoided. Also improved from filter to slice - O(1) vs O(n)."}
        ]
    },

    # -------------------------------------------------------------------------
    # 11. Circular dependency - caught by Dependency Health Check
    # -------------------------------------------------------------------------
    {
        "id": "error_011_circular_dep",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Add the UserService import to the AuthService."},
            {"role": "assistant", "content": "Adding UserService import to AuthService..."},
            {"role": "assistant", "content": "**Dependency Health Check triggered**\n\nChecking for circular dependencies..."},
            {"role": "tool_result", "content": "Import chain analysis:\nauth_service.ts -> user_service.ts\nuser_service.ts -> auth_service.ts?\n\nCIRCULAR DEPENDENCY DETECTED:\nauth_service.ts imports user_service.ts\nuser_service.ts imports auth_service.ts"},
            {"role": "assistant", "content": "**BLOCKING VIOLATION: Circular dependency**\n\nRoot cause: Both services were importing each other directly.\n\nSolution: Extract shared types/interfaces into a third module that neither service owns.\n```\nauth_service.ts -> types/user_types.ts <- user_service.ts\n```"},
            {"role": "assistant", "content": "Circular dependency prevented. Shared types extracted to `types/user_types.ts`. Both services import from there, breaking the cycle."}
        ]
    },

    # -------------------------------------------------------------------------
    # 12. API signature mismatch - caught by type check
    # -------------------------------------------------------------------------
    {
        "id": "error_012_api_mismatch",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "The API call is failing."},
            {"role": "tool_result", "content": "Runtime error:\nTypeError: fetchUsers is not a function"},
            {"role": "assistant", "content": "Function not found at runtime. Let me check the export."},
            {"role": "tool_result", "content": "// api/users.ts\nexport { fetchUsers as default };\n\n// calling code:\nimport { fetchUsers } from './api/users';  // WRONG - it's a default export"},
            {"role": "assistant", "content": "Mismatch: `fetchUsers` is exported as default, not named. Import is using named import syntax.\n\nFixing the import:\n```typescript\nimport fetchUsers from './api/users';\n```\nor fix the export:\n```typescript\nexport function fetchUsers() { ... }\n```"},
            {"role": "tool_result", "content": "Build successful. Runtime error resolved."},
            {"role": "assistant", "content": "API signature mismatch fixed. Named vs default export confusion. Import matched the export."}
        ]
    },

    # -------------------------------------------------------------------------
    # 13. Memory leak - caught by analysis
    # -------------------------------------------------------------------------
    {
        "id": "error_013_memory_leak",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Add an event listener to the window for resize events."},
            {"role": "assistant", "content": "Adding resize listener:\n```typescript\nexport function init() {\n  window.addEventListener('resize', () => {\n    handleResize();\n  });\n}\n```"},
            {"role": "assistant", "content": "**Predictive Analyzer: Memory leak check**\n\nMEMORY LEAK RISK: Event listener added but never removed.\n\nIn applications that mount/unmount components, this causes:\n- Listener accumulates on each mount\n- Stale closures retain memory\n- Handle references prevent garbage collection"},
            {"role": "assistant", "content": "Fixing with cleanup:\n```typescript\nexport function init(): () => void {\n  const handler = () => handleResize();\n  window.addEventListener('resize', handler);\n  // Return cleanup function\n  return () => window.removeEventListener('resize', handler);\n}\n```\nOr in a React hook:\n```typescript\nuseEffect(() => {\n  const cleanup = init();\n  return cleanup;\n}, []);\n```"},
            {"role": "assistant", "content": "Memory leak prevented. Cleanup function returned for proper teardown."}
        ]
    },

    # -------------------------------------------------------------------------
    # 14. Infinite loop - caught by Predictive Analyzer
    # -------------------------------------------------------------------------
    {
        "id": "error_014_infinite_loop",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Write a function that flattens a nested array recursively."},
            {"role": "assistant", "content": "Writing flatten function:\n```typescript\nexport function flatten<T>(arr: (T | T[])[]): T[] {\n  const result: T[] = [];\n  for (const item of arr) {\n    if (Array.isArray(item)) {\n      result.push(...flatten(item));\n    } else {\n      result.push(item);\n    }\n  }\n  return result;\n}\n```"},
            {"role": "assistant", "content": "**Predictive Analyzer: Termination check**\n\nTERMINATION GUARANTEE: The recursive call reduces the input:\n- `flatten(item)` where `item` is a sub-array\n- Each recursive call operates on a smaller array (the nested element)\n- Base case: no arrays left -> returns primitive items\n\nSafe: array gets smaller on each recursion."},
            {"role": "assistant", "content": "Adding depth limit for untrusted input:\n```typescript\nexport function flatten<T>(\n  arr: (T | T[])[],\n  depth: number = 100\n): T[] {\n  if (depth <= 0) return arr as T[];\n  const result: T[] = [];\n  for (const item of arr) {\n    if (Array.isArray(item)) {\n      result.push(...flatten(item, depth - 1));\n    } else {\n      result.push(item);\n    }\n  }\n  return result;\n}\n```"},
            {"role": "assistant", "content": "Termination guaranteed. Depth limit added for safety on malicious input."}
        ]
    },

    # -------------------------------------------------------------------------
    # 15. Race condition - caught by analysis
    # -------------------------------------------------------------------------
    {
        "id": "error_015_race_condition",
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": "Add a cache with a TTL that refreshes automatically."},
            {"role": "assistant", "content": "Writing TTL cache:\n```typescript\nconst cache = new Map<string, { value: any; expiry: number }>();\n\nexport function getCached<T>(key: string): T | undefined {\n  const entry = cache.get(key);\n  if (!entry) return undefined;\n  if (Date.now() > entry.expiry) {\n    cache.delete(key);\n    return undefined;\n  }\n  return entry.value;\n}\n\nexport function setCached<T>(key: string, value: T, ttl: number): void {\n  cache.set(key, { value, expiry: Date.now() + ttl });\n}\n```"},
            {"role": "assistant", "content": "**Predictive Analyzer: Concurrency check**\n\nRACE CONDITION RISK: Check-then-act on cache entry.\n\nBetween `!entry` check and `cache.delete()`, another call could modify the cache. Also, auto-refresh logic needs atomicity."},
            {"role": "assistant", "content": "Fixing with atomic operations:\n```typescript\nexport function getOrRefresh<T>(\n  key: string,\n  ttl: number,\n  refreshFn: () => Promise<T>\n): Promise<T> {\n  const entry = cache.get(key);\n  const now = Date.now();\n\n  // Check and set atomically within this call\n  if (entry && now < entry.expiry) {\n    return Promise.resolve(entry.value as T);\n  }\n\n  // Refresh needed - use mutex to prevent stampede\n  return refreshWithLock(key, ttl, refreshFn);\n}\n\n// Implement lock per key to prevent thundering herd\nconst locks = new Map<string, Promise<any>>();\nfunction refreshWithLock<T>(\n  key: string,\n  ttl: number,\n  refreshFn: () => Promise<T>\n): Promise<T> {\n  const existing = locks.get(key);\n  if (existing) return existing as Promise<T>;\n\n  const promise = refreshFn().then(value => {\n    cache.set(key, { value, expiry: Date.now() + ttl });\n    locks.delete(key);\n    return value;\n  });\n  locks.set(key, promise);\n  return promise;\n}\n```"},
            {"role": "assistant", "content": "Race condition prevented. Lock-per-key pattern prevents thundering herd on cache miss."}
        ]
    },
]


def generate_error_recovery(output_file: str) -> int:
    """Generate all error recovery chain training examples."""
    count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        for example in ERROR_RECOVERY_EXAMPLES:
            messages = []
            for msg in example["messages"]:
                role = msg["role"]
                content = msg["content"]
                messages.append({"role": role, "content": content})

            record = {
                "messages": [
                    {"role": "system", "content": example.get("system", SYSTEM_PROMPT)}
                ] + messages
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count


if __name__ == "__main__":
    output_path = Path(__file__).parent / "error_recovery_training.jsonl"
    count = generate_error_recovery(output_path)
    print(f"Generated {count} error recovery examples")
    print(f"Saved to: {output_path}")
