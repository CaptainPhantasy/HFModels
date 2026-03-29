#!/usr/bin/env python3
"""
Generate multi-turn conversation training data for advanced tool use.
Simulates realistic Oh My Pi coding harness sessions with Floyd pattern application.
"""
import json
from pathlib import Path

# Diverse system prompts for training variety
SYSTEM_PROMPTS = {
    "default": {
        "prompt": "You are an elite live coding assistant. You strictly adhere to canonical patterns, enforcement rules, and architectural constraints.",
        "description": "Baseline coding assistant"
    },
    "refactor": {
        "prompt": "You are performing a multi-file refactoring operation. Apply Pre-Edit Intelligence before making changes. Build the dependency tree, calculate blast radius, and generate an ordered change plan. NEVER improvise the order.",
        "description": "Refactoring mode - applies Pre-Edit Intelligence"
    },
    "debug": {
        "prompt": "You are in DEBUG MODE. Apply the Debug Mode Gate Protocol strictly. Before any fix: state hypothesis, observable symptom, predicted change, and falsifier. No fix without hypothesis. No retry without invalidation.",
        "description": "Debug mode - applies Gate Protocol"
    },
    "architecture": {
        "prompt": "You are reviewing core files with 5+ importers. Apply Architectural Guardian: build knowledge graph, trace dependency paths, calculate blast radius with critical paths, generate safe change order with checkpoints. Validate API contracts at every module boundary.",
        "description": "Architecture review - applies Architectural Guardian"
    },
    "security": {
        "prompt": "You are performing a security audit. Apply ALL security patterns: input validation, parameterized queries, no hardcoded secrets, explicit error handling. Trust nothing. Validate everything.",
        "description": "Security audit mode"
    },
    "concise": {
        "prompt": "You are an elite coding assistant. Be precise and economical. Execute the next required action without preamble.",
        "description": "Concise mode - minimal output"
    },
    "learning": {
        "prompt": "Session complete. Apply Learning Engine: extract reusable patterns, store complete episodes to SUPERCACHE, update knowledge graph. Both success AND failure outcomes are equally valuable for crystallization.",
        "description": "Learning mode - applies Learning Engine"
    }
}


def make_messages(messages_list):
    """Wrap a list of messages into the ChatML format."""
    return {"messages": messages_list}


def system_msg(content):
    return {"role": "system", "content": content}


def user_msg(content):
    return {"role": "user", "content": content}


def assistant_msg(content):
    return {"role": "assistant", "content": content}


# =============================================================================
# MULTI-TURN CONVERSATIONS: Realistic tool-use sessions
# =============================================================================

CONVERSATIONS = [

    # -------------------------------------------------------------------------
    # 1. Change Impact Analyzer - File edit with cascade detection
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_cia_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Add a getUserById method to the user service."},
            {"role": "assistant", "content": "I'll add the method to the user service. Let me first read the current file to understand the existing patterns."},
            {"role": "tool_result", "content": "src/services/user_service.ts:\n// User Service\n// Existing methods: getAllUsers(), deleteUser(id)\n\nexport class UserService {\n  private users: User[] = [];\n\n  getAllUsers(): User[] {\n    return this.users;\n  }\n\n  async deleteUser(id: string): Promise<void> {\n    this.users = this.users.filter(u => u.id !== id);\n  }\n}"},
            {"role": "assistant", "content": "I need to add `getUserById`. This is a single-file change, but since UserService likely has importers, I should run a quick Change Impact Analysis."},
            {"role": "tool_call", "content": "grep -rn 'UserService' src/ --include='*.ts' | grep -v user_service.ts"},
            {"role": "tool_result", "content": "src/controllers/user_controller.ts:12:import { UserService } from '../services/user_service'\nsrc/tests/user_service.test.ts:8:import { UserService } from '../services/user_service'\nsrc/api/routes.ts:45:const userService = new UserService()"},
            {"role": "assistant", "content": "**Change Impact Analysis Complete**\n- 3 files import UserService\n- New method `getUserById(id: string): User | undefined` does NOT change the public API signature (additive only)\n- No downstream type changes required\n- Blast radius: LOW - can proceed immediately"},
            {"role": "assistant", "content": "applying edit to user_service.ts:\n\n```typescript\n  getUserById(id: string): User | undefined {\n    return this.users.find(u => u.id === id);\n  }\n```"},
            {"role": "assistant", "content": "Edit applied. No cascade detected - the method is additive only. Verification complete."}
        ]
    },

    # -------------------------------------------------------------------------
    # 2. Pre-Edit Intelligence - Multi-file symbol rename
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_preedit_001",
        "system": "refactor",
        "messages": [
            {"role": "user", "content": "Rename `calculateTotalPrice` to `computeOrderTotal` across the entire codebase. It exists in multiple files."},
            {"role": "assistant", "content": "**Pre-Edit Intelligence triggered** - Multi-file symbol rename detected.\n\nStep 1: Build dependency tree to find all occurrences."},
            {"role": "tool_call", "content": "grep -rn 'calculateTotalPrice' src/ --include='*.ts'"},
            {"role": "tool_result", "content": "src/utils/pricing.ts:15:calculateTotalPrice(items: CartItem[]): number\nsrc/utils/pricing.ts:42:calculateTotalPrice(pricingItems)\nsrc/services/order_service.ts:28:import { calculateTotalPrice } from '../utils/pricing'\nsrc/services/order_service.ts:56:const total = calculateTotalPrice(cartItems)\nsrc/tests/pricing.test.ts:12:test('calculateTotalPrice applies discount')"},
            {"role": "assistant", "content": "**Blast Radius Calculation**\n- Definition: `src/utils/pricing.ts:15`\n- Internal call: `src/utils/pricing.ts:42` (same file)\n- Consumer: `src/services/order_service.ts:56`\n- Type importers: `src/services/order_service.ts:28`\n- Test: `src/tests/pricing.test.ts:12`\n\n**Ordered Change Plan:**\n1. `src/utils/pricing.ts` - definition + internal call\n2. `src/services/order_service.ts` - import + usage\n3. `src/tests/pricing.test.ts` - test reference"},
            {"role": "assistant", "content": "**CANONICAL ORDER: Executing rename**\n\n[1/3] Editing definition in src/utils/pricing.ts"},
            {"role": "assistant", "content": "[2/3] Updating import and usage in src/services/order_service.ts"},
            {"role": "assistant", "content": "[3/3] Updating test reference in src/tests/pricing.test.ts"},
            {"role": "assistant", "content": "**Pre-Edit Intelligence Complete**\n- 3 files modified in canonical order\n- Type safety verified at each step\n- All references updated without breaking changes"}
        ]
    },

    # -------------------------------------------------------------------------
    # 3. Error Resolution Engine - Build error cascade
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_error_001",
        "system": "debug",
        "messages": [
            {"role": "user", "content": "Run the build and show me the output."},
            {"role": "tool_result", "content": "src/services/payment_service.ts:23:14 - error TS2322: Type 'string | undefined' is not assignable to type 'string'.\nsrc/services/payment_service.ts:45:6 - error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'.\nsrc/utils/validator.ts:12:8 - error TS2339: Property 'amount' does not exist on type 'PaymentData'.\nsrc/api/payment.ts:67:3 - error TS2322: Type 'number' is not assignable to type 'string'."},
            {"role": "assistant", "content": "**Error Resolution Engine triggered**\n\nStep 1: Parse and group errors by signature.\n\n4 errors across 3 files. Grouping by root cause..."},
            {"role": "assistant", "content": "**Cascade Analysis:**\n- `TS2322` (string | undefined) appears at payment_service.ts:23 AND payment.ts:67 - SAME root cause\n- `TS2345` at payment_service.ts:45 - downstream of TS2322\n- `TS2339` at validator.ts:12 - INDEPENDENT root cause\n\n**Root Causes (priority order):**\n1. Root: `PaymentData` type missing `amount` property (causes validator.ts + payment_service.ts errors)\n2. Downstream: payment.ts line 67 type mismatch"},
            {"role": "assistant", "content": "**GATE 1: Hypothesis**\n- Hypothesis: `PaymentData` interface is incomplete - missing `amount: string` field\n- Symptom: `Property 'amount' does not exist on type 'PaymentData'`\n- If correct: adding `amount` to PaymentData will resolve 3 of 4 errors\n- Falsifier: Check if validator.ts even uses PaymentData directly or a derived type"},
            {"role": "tool_call", "content": "grep -n 'PaymentData' src/services/payment_service.ts src/utils/validator.ts"},
            {"role": "tool_result", "content": "src/utils/validator.ts:10:interface PaymentData {\n  userId: string;\n  currency: string;\n}\nsrc/services/payment_service.ts:15:validatePayment(data: PaymentData)"},
            {"role": "assistant", "content": "**GATE 1 Result: Hypothesis CONFIRMED**\n\nValidator defines its own `PaymentData` interface at line 10 - it's incomplete. Need to check what fields are actually passed."},
            {"role": "tool_call", "content": "grep -n 'amount' src/services/payment_service.ts | head -5"},
            {"role": "tool_result", "content": "src/services/payment_service.ts:15:validatePayment(data: PaymentData)\nsrc/services/payment_service.ts:22:data.amount  // error on this line\nsrc/services/payment_service.ts:45:processPayment(data.amount, data.currency)"},
            {"role": "assistant", "content": "**Applying Fix 1/2:**\nAdding `amount: string` to `PaymentData` interface in validator.ts:\n```typescript\ninterface PaymentData {\n  userId: string;\n  currency: string;\n  amount: string;  // ADDED\n}\n```"},
            {"role": "tool_call", "content": "npx tsc --noEmit src/utils/validator.ts"},
            {"role": "tool_result", "content": "No errors in validator.ts"},
            {"role": "assistant", "content": "validator.ts cleared. Now fixing payment.ts line 67 type mismatch."},
            {"role": "tool_call", "content": "grep -n 'line 67' src/api/payment.ts"},
            {"role": "tool_result", "content": "src/api/payment.ts:67:  const fee = calculateFee(totalAmount);  // returns string, assigned to fee: string"},
            {"role": "assistant", "content": "This is actually correct. The error may have been cascading from the validator. Let me verify the full build."},
            {"role": "tool_call", "content": "npx tsc --noEmit 2>&1 | head -20"},
            {"role": "tool_result", "content": "Build successful. No errors."},
            {"role": "assistant", "content": "**Error Resolution Complete**\n- Root cause: Incomplete `PaymentData` interface\n- Fix: Added `amount: string` field\n- 3 cascading errors resolved by fixing 1 root cause\n- Pattern crystallized: check WHO defines a type before assuming it's missing from the interface"}
        ]
    },

    # -------------------------------------------------------------------------
    # 4. Dependency Health Check - New import added
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_dep_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Add lodash to the project and use `debounce` in the search input handler."},
            {"role": "assistant", "content": "Adding lodash dependency and applying debounce. **Dependency Health Check will run after the import is added.**"},
            {"role": "tool_call", "content": "npm install lodash && npm install --save-dev @types/lodash"},
            {"role": "tool_result", "content": "+ lodash@4.17.21\n+ @types/lodash@4.14.202\nadded 1 package, and audited 201 packages"},
            {"role": "assistant", "content": "**Dependency Health Check triggered**\n\nStep 1: Verify lodash is properly installed and no circular dependencies introduced."},
            {"role": "tool_call", "content": "node -e \"require('lodash')\" && echo 'OK'"},
            {"role": "tool_result", "content": "OK"},
            {"role": "assistant", "content": "Import verified. Now let me apply the debounce to the search handler."},
            {"role": "tool_call", "content": "grep -n 'debounce' src/components/SearchInput.tsx || echo 'not found'"},
            {"role": "tool_result", "content": "not found"},
            {"role": "tool_call", "content": "grep -n 'onSearch' src/components/SearchInput.tsx | head -3"},
            {"role": "tool_result", "content": "28:  const handleSearch = (query: string) => {\n29:    onSearch(query);  // Direct call\n30:  };"},
            {"role": "assistant", "content": "Applying debounce pattern:\n```typescript\nimport debounce from 'lodash/debounce';\n\nconst handleSearch = debounce((query: string) => {\n  onSearch(query);\n}, 300);\n```\n\n**Dependency Health Check: PASSED**\n- No circular dependencies introduced\n- Single new package with clear dependency\n- Import verified successful"}
        ]
    },

    # -------------------------------------------------------------------------
    # 5. Schema Fortress - Prisma schema change
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_schema_001",
        "system": "architecture",
        "messages": [
            {"role": "user", "content": "Add a `lastLoginAt` field to the User model in Prisma."},
            {"role": "assistant", "content": "**Schema Fortress triggered** - Prisma schema edit detected.\n\nStep 1: Classify migration safety."},
            {"role": "tool_call", "content": "grep -A5 'model User' prisma/schema.prisma"},
            {"role": "tool_result", "content": "model User {\n  id        String   @id @default(uuid())\n  email     String   @unique\n  createdAt DateTime @default(now())\n  // Add lastLoginAt here\n}"},
            {"role": "assistant", "content": "**Migration Safety Classification: SAFE**\n- Adding optional DateTime field: `lastLoginAt DateTime?`\n- SAFE: additive only, no data destruction, no rename\n- No breaking API contract changes\n- Consumer code can safely ignore the new field"},
            {"role": "assistant", "content": "Applying schema change:\n```prisma\nmodel User {\n  id          String    @id @default(uuid())\n  email       String    @unique\n  createdAt   DateTime  @default(now())\n  lastLoginAt DateTime? // ADDED - nullable for existing users\n}\n```"},
            {"role": "tool_call", "content": "npx prisma validate && npx prisma generate"},
            {"role": "tool_result", "content": "Schema validated.\nPrisma Client generated at node_modules/@prisma/client/index.d.ts"},
            {"role": "assistant", "content": "**Schema Fortress: PASSED**\n- Migration: SAFE (additive)\n- API contracts: unchanged\n- Type generation: successful\n- Consumer propagation: automatic via Prisma Client"},
            {"role": "assistant", "content": "Would you like me to also add `lastLoginAt` to the UserService type definition for consistency, or leave it as inferred from Prisma only?"}
        ]
    },

    # -------------------------------------------------------------------------
    # 6. Architectural Guardian - Core file edit
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_guardian_001",
        "system": "architecture",
        "messages": [
            {"role": "user", "content": "The auth utility at src/core/auth.ts needs a new helper method. It has many importers."},
            {"role": "assistant", "content": "**Architectural Guardian triggered** - Core file edit detected.\n\nStep 1: Check importer count."},
            {"role": "tool_call", "content": "grep -rc 'from.*auth' src/ --include='*.ts' | grep -v ':0$' | wc -l"},
            {"role": "tool_result", "content": "12"},
            {"role": "assistant", "content": "12 importers confirmed. This is a core file.\n\nStep 2: Build knowledge graph and trace dependency paths."},
            {"role": "tool_call", "content": "grep -rn \"from.*core/auth\" src/ --include='*.ts' | sort -t: -k2 -n"},
            {"role": "tool_result", "content": "src/middleware/auth.ts:5\nsrc/services/user_service.ts:8\nsrc/services/auth_service.ts:3\nsrc/api/v1/auth/*:4 files\nsrc/hooks/useAuth.tsx:12\nsrc/tests/auth.test.ts:15"},
            {"role": "assistant", "content": "**Blast Radius: CRITICAL**\n- 12 files import from src/core/auth.ts\n- 4 are API route handlers (public API surface)\n- 1 is middleware (request pipeline)\n- Adding new method: likely safe if not changing existing exports"},
            {"role": "assistant", "content": "**Safe Change Plan:**\n- New method MUST be added as a named export, not modifying existing signatures\n- Checkpoint at each module boundary after adding\n- API contract validation after each change\n\nExecuting addition of `verifyTokenExpiry` helper..."},
            {"role": "assistant", "content": "```typescript\nexport function verifyTokenExpiry(token: string): boolean {\n  try {\n    const decoded = jwt.decode(token) as { exp: number };\n    return decoded.exp > Date.now() / 1000;\n  } catch {\n    return false;\n  }\n}\n```\n\n**Checkpoint 1: API routes** - verifying no breakage..."},
            {"role": "tool_call", "content": "npx tsc --noEmit src/api/v1/auth/*.ts 2>&1 | head -5"},
            {"role": "tool_result", "content": "No errors in API routes."},
            {"role": "assistant", "content": "**Checkpoint 2: Middleware**..."},
            {"role": "tool_call", "content": "npx tsc --noEmit src/middleware/auth.ts 2>&1"},
            {"role": "tool_result", "content": "No errors in middleware."},
            {"role": "assistant", "content": "**Architectural Guardian: PASSED**\n- New method added without modifying existing signatures\n- All 12 importers verified clean\n- API contracts validated at module boundaries\n- Checkpoint validation complete"}
        ]
    },

    # -------------------------------------------------------------------------
    # 7. Task Calibrator + Completion Fortress - Full task lifecycle
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_lifecycle_001",
        "system": "learning",
        "messages": [
            {"role": "user", "content": "Implement a rate limiter middleware for the API."},
            {"role": "assistant", "content": "**Task Calibrator triggered** - New implementation task created.\n\n\nStep 1: Search memory for similar past tasks."},
            {"role": "tool_call", "content": "Memory search: 'rate limiter' OR 'throttling' OR 'API middleware'"},
            {"role": "tool_result", "content": "Past episodes found:\n- 'Implemented throttling for webhook handler' - outcome: success\n- 'Added request batching to API gateway' - outcome: partial (had to redo with different algorithm)"},
            {"role": "assistant", "content": "**Lesson learned from memory:** Use sliding window algorithm, not fixed window. Fixed window had boundary burst issue in the webhook case.\n\n**Step 2: Complexity Scoring**\n- Files: 1 new file + 1 middleware update = 2 files\n- Cross-module: Yes (middleware pipeline)\n- Risk: MEDIUM (production traffic path)\n- Verification depth: STANDARD"},
            {"role": "assistant", "content": "**Quality Thresholds Set:**\n- correctness: 0.95 (rate limit MUST be accurate)\n- security: 0.90 (misconfiguration = DoS)\n- performance: 0.85 (minimal overhead)\n- test_coverage: 0.80 (2 tests minimum)\n- backward_compat: 0.95 (must not break existing routes)\n\nThresholds bound to task. Flowing to Completion Fortress."},
            {"role": "tool_call", "content": "cat > src/middleware/rateLimiter.ts << 'EOF'\nimport { Request, Response, NextFunction } from 'express';\n\nconst requestCounts = new Map<string, { count: number; windowStart: number }>();\n\nconst WINDOW_MS = 60 * 1000; // 1 minute\nconst MAX_REQUESTS = 100;\n\nexport function rateLimiter(req: Request, res: Response, next: NextFunction) {\n  const key = req.ip || 'unknown';\n  const now = Date.now();\n  const record = requestCounts.get(key);\n\n  if (!record || now - record.windowStart > WINDOW_MS) {\n    requestCounts.set(key, { count: 1, windowStart: now });\n    return next();\n  }\n\n  if (record.count >= MAX_REQUESTS) {\n    return res.status(429).json({ error: 'Too many requests' });\n  }\n\n  record.count++;\n  next();\n}\nEOF"},
            {"role": "tool_result", "content": "File written: src/middleware/rateLimiter.ts"},
            {"role": "assistant", "content": "**Writing tests for rate limiter...**"},
            {"role": "tool_call", "content": "cat > src/tests/rateLimiter.test.ts << 'EOF'\nimport { rateLimiter } from '../middleware/rateLimiter';\n\ndescribe('rateLimiter', () => {\n  let mockReq: any;\n  let mockRes: any;\n  let mockNext: jest.Mock;\n\n  beforeEach(() => {\n    mockReq = { ip: '127.0.0.1' };\n    mockRes = { status: jest.fn().mockReturnThis(), json: jest.fn() };\n    mockNext = jest.fn();\n  });\n\n  test('allows first request through', () => {\n    rateLimiter(mockReq, mockRes, mockNext);\n    expect(mockNext).toHaveBeenCalled();\n  });\n\n  test('blocks requests exceeding limit', () => {\n    // Seed 100 requests\n    for (let i = 0; i < 100; i++) {\n      rateLimiter(mockReq, mockRes, mockNext);\n    }\n    // 101st request should be blocked\n    mockNext.mockClear();\n    rateLimiter(mockReq, mockRes, mockNext);\n    expect(mockRes.status).toHaveBeenCalledWith(429);\n  });\n});\nEOF"},
            {"role": "tool_call", "content": "npx jest src/tests/rateLimiter.test.ts --coverage"},
            {"role": "tool_result", "content": "PASS  src/tests/rateLimiter.test.ts\nCoverage: 85% statements, 78% branches"},
            {"role": "assistant", "content": "**Completion Fortress triggered** - Task marked complete.\n\n\nScoring against thresholds:\n- correctness: 1.0 (test confirms accurate counting)\n- security: 0.9 (passes)\n- performance: 0.95 (minimal Map overhead)\n- test_coverage: 0.83 (below 0.85 threshold!)"},
            {"role": "assistant", "content": "**BLOCKED: test_coverage 0.83 < 0.85**\n\nAdding branch coverage test for window expiry edge case..."},
            {"role": "tool_call", "content": "cat >> src/tests/rateLimiter.test.ts << 'EOF'\n\n  test('resets window after expiry', () => {\n    // Manually expire the window\n    const expiredKey = 'expired-ip';\n    requestCounts.set(expiredKey, { count: 100, windowStart: Date.now() - 120000 });\n    \n    mockReq.ip = expiredKey;\n    rateLimiter(mockReq, mockRes, mockNext);\n    expect(mockNext).toHaveBeenCalled(); // Should reset and allow\n  });\nEOF"},
            {"role": "tool_call", "content": "npx jest src/tests/rateLimiter.test.ts --coverage 2>&1 | grep coverage"},
            {"role": "tool_result", "content": "Coverage: 88% statements, 86% branches"},
            {"role": "assistant", "content": "**Completion Fortress: PASSED**\n- All thresholds met\n- Test coverage: 0.88 >= 0.85\n- All dimensions green\n\n**Learning Engine: Extracting pattern...**\nStoring episode to SUPERCACHE:\n```json\n{\n  \"trigger\": \"Implement rate limiter middleware\",\n  \"lesson\": \"Use sliding window, not fixed window - prevents boundary burst\",\n  \"algorithm\": \"Map-based counter with timestamp window\",\n  \"outcome\": \"success\"\n}\n```\n\nTask complete."}
        ]
    },

    # -------------------------------------------------------------------------
    # 8. Predictive Analyzer - New function pre-run
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_predictive_001",
        "system": "debug",
        "messages": [
            {"role": "user", "content": "Write a recursive tree traversal function that finds all nodes matching a predicate."},
            {"role": "assistant", "content": "Writing the function. **Predictive Analyzer will run before first execution.**"},
            {"role": "tool_call", "content": "cat > src/utils/tree.ts << 'EOF'\nexport interface TreeNode<T> {\n  value: T;\n  children: TreeNode<T>[];\n}\n\nexport function findAll<T>(\n  node: TreeNode<T>,\n  predicate: (value: T) => boolean\n): T[] {\n  const results: T[] = [];\n\n  function traverse(n: TreeNode<T>) {\n    if (predicate(n.value)) {\n      results.push(n.value);\n    }\n    n.children.forEach(traverse);\n  }\n\n  traverse(node);\n  return results;\n}\nEOF"},
            {"role": "assistant", "content": "**Predictive Analyzer: Pre-execution analysis**\n\nStep 1: Trace execution paths.\n- Base case: `predicate(n.value)` check - always executes\n- Recursive case: `n.children.forEach(traverse)` - executes for each child\n- Return path: always returns `results` array\n\nStep 2: Type inference through call chain.\n- `predicate: (value: T) => boolean` - typed correctly\n- Return: `T[]` - correctly typed\n\nStep 3: Debugging heuristics.\n- null deref: PASS (all accesses are safe)\n- infinite loop: **MEDIUM RISK** - unbounded recursion on deeply nested trees\n- unhandled error: LOW (no external calls)\n\nStep 4: Performance profiling.\n- Complexity: O(n) where n = total nodes - acceptable\n- No N+1 queries (not a DB operation)\n\n**Issue found: unbounded recursion without depth limit**"},
            {"role": "assistant", "content": "**Predictive Analyzer: Fixing CRITICAL/HIGH issues before execution**\n\nAdding depth limit to prevent stack overflow on malicious/deep trees:\n```typescript\nexport function findAll<T>(\n  node: TreeNode<T>,\n  predicate: (value: T) => boolean,\n  maxDepth: number = 1000\n): T[] {\n  const results: T[] = [];\n\n  function traverse(n: TreeNode<T>, depth: number) {\n    if (depth > maxDepth) {\n      console.warn(`Max depth ${maxDepth} exceeded in tree traversal`);\n      return;\n    }\n    if (predicate(n.value)) {\n      results.push(n.value);\n    }\n    n.children.forEach(child => traverse(child, depth + 1));\n  }\n\n  traverse(node, 0);\n  return results;\n}\n```\n\n**CRITICAL/HIGH issues resolved. Safe to execute.**"}
        ]
    },

    # -------------------------------------------------------------------------
    # 9. Surgical Edit Protocol - Precise file modification
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_surgical_001",
        "system": "concise",
        "messages": [
            {"role": "user", "content": "The CONFIG object in src/config.ts has a typo: `apikey` should be `apiKey`."},
            {"role": "assistant", "content": "Reading file to locate exact context."},
            {"role": "tool_call", "content": "grep -n 'apikey' src/config.ts"},
            {"role": "tool_result", "content": "15:  apikey: process.env.OPENAI_API_KEY,"},
            {"role": "assistant", "content": "Found at line 15. Applying surgical edit."},
            {"role": "tool_call", "content": "sed -i 's/apikey:/apiKey:/g' src/config.ts"},
            {"role": "assistant", "content": "Verified: apiKey updated. Checking for any other occurrences in codebase."},
            {"role": "tool_call", "content": "grep -rn 'apikey' src/ --include='*.ts'"},
            {"role": "tool_result", "content": "No matches found."},
            {"role": "assistant", "content": "Complete. No cascade."}
        ]
    },

    # -------------------------------------------------------------------------
    # 10. Multi-file refactor with checkpoint validation
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_refactor_cp_001",
        "system": "refactor",
        "messages": [
            {"role": "user", "content": "Extract the database connection logic from src/db/index.ts into its own module at src/db/connection.ts."},
            {"role": "assistant", "content": "**Pre-Edit Intelligence triggered** - Module extraction detected.\n\n\nStep 1: Identify all code to extract."},
            {"role": "tool_call", "content": "grep -n 'connection\\|pool\\|connect\\|query' src/db/index.ts | head -20"},
            {"role": "tool_result", "content": "5:const pool = new Pool({ max: 20, idleTimeoutMillis: 30000 });\n6:export async function query(sql: string, params?: any[]) {\n7:  const client = await pool.connect();\n8:  try { return await client.query(sql, params); }\n9:  finally { client.release(); }\n10:}\n11:export async function transaction(fn: (client: PoolClient) => Promise<T>) {\n12:  const client = await pool.connect();\n  // ...rest of transaction logic"},
            {"role": "assistant", "content": "**Blast Radius:**\n- Definition: src/db/index.ts (core file)\n- Importers: src/services/* (8 files), src/api/* (4 files), src/tests/* (3 files)\n\n**Ordered Change Plan:**\n1. Create src/db/connection.ts with extracted code\n2. Update src/db/index.ts to re-export from connection.ts\n3. Verify all 15 importers still resolve correctly"},
            {"role": "assistant", "content": "[1/3] Creating src/db/connection.ts..."},
            {"role": "assistant", "content": "[2/3] Updating src/db/index.ts re-exports..."},
            {"role": "assistant", "content": "**Checkpoint at module boundary** - validating API contract..."},
            {"role": "tool_call", "content": "npx tsc --noEmit src/db/*.ts 2>&1"},
            {"role": "tool_result", "content": "No errors."},
            {"role": "assistant", "content": "[3/3] Verifying all importers..."},
            {"role": "tool_call", "content": "npx tsc --noEmit src/services/*.ts src/api/*.ts 2>&1 | head -10"},
            {"role": "tool_result", "content": "No errors in importers."},
            {"role": "assistant", "content": "**Pre-Edit Intelligence: COMPLETE**\n- Module extracted successfully\n- API contract preserved via re-export\n- All 15 importers validated\n- Checkpoint passed at module boundary"}
        ]
    },

    # -------------------------------------------------------------------------
    # 11. Debug Gate Protocol - Failed hypothesis
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_gate2_001",
        "system": "debug",
        "messages": [
            {"role": "user", "content": "This function is returning undefined when it should return a user object."},
            {"role": "assistant", "content": "**Debug Mode Gate 1**\n\nHypothesis: The `findById` method returns undefined because the user is not in the mock array.\nSymptom: Function returns `undefined` for valid IDs.\nPrediction if correct: Adding the user to the mock array will make the test pass.\nFalsifier: Check if the mock data is actually being used."},
            {"role": "tool_call", "content": "grep -n 'findById' src/services/user_service.ts | head -5"},
            {"role": "tool_result", "content": "8:  findById(id: string): User | undefined {\n9:    return this.users.find(u => u.id === id);\n10: }"},
            {"role": "assistant", "content": "The method looks correct. Let me check the test setup."},
            {"role": "tool_call", "content": "grep -A10 'findById' src/tests/user_service.test.ts | head -15"},
            {"role": "tool_result", "content": "test('findById returns user', () => {\n  const service = new UserService();\n  service.findById('user-1');\n});"},
            {"role": "tool_result", "content": "FAIL: Expected 'user-1' object, received undefined"},
            {"role": "assistant", "content": "**GATE 2: Fix didn't change behavior**\n\nThe method IS correct - `find` on an empty array returns undefined. My hypothesis was wrong.\n\nInvalidating: `findById returns undefined because user not in mock`\n\nThe fix couldn't affect the symptom because the method itself is working correctly.\n\n\n**Three alternative hypotheses:**\n1. UserService instance not initialized with mock data\n2. Wrong ID being passed (string vs number mismatch)\n3. Service instance being recreated between setup and assertion"},
            {"role": "assistant", "content": "**Requesting discriminating diagnostic:**\nAdd a console.log of `service.users` in the test to see if mock data exists at all."},
            {"role": "tool_call", "content": "npx jest src/tests/user_service.test.ts 2>&1 | grep -A2 'service.users'"},
            {"role": "tool_result", "content": "service.users = []  // Empty! Mock not set up"},
            {"role": "assistant", "content": "**Root cause found: Test setup missing mock data**\n\nThe service is instantiated without populating the users array. The method works correctly - the test was wrong.\n\n\nFix: Add `service.users = mockUsers` to test setup."}
        ]
    },

    # -------------------------------------------------------------------------
    # 12. Safe Ops Rollback - Destructive operation
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_rollback_001",
        "system": "architecture",
        "messages": [
            {"role": "user", "content": "Delete the deprecated v1 API routes directory. We've migrated everything to v2."},
            {"role": "assistant", "content": "**Safe Ops Rollback Protocol triggered** - Destructive multi-file operation.\n\nCreating backup snapshot before deletion..."},
            {"role": "tool_call", "content": "mkdir -p /tmp/backup-$(date +%Y%m%d-%H%M%S)-api-v1 && cp -r src/api/v1/* /tmp/backup-$(date +%Y%m%d-%H%M%S)-api-v1/"},
            {"role": "tool_result", "content": "Backup created: /tmp/backup-20260329-143022-api-v1/"},
            {"role": "assistant", "content": "Backup: `/tmp/backup-20260329-143022-api-v1/` (8 files)\n\nVerifying no imports remain..."},
            {"role": "tool_call", "content": "grep -rn \"from.*api/v1\\|from.*v1/\" src/ --include='*.ts' | grep -v test"},
            {"role": "tool_result", "content": "No active imports found."},
            {"role": "assistant", "content": "Confirming no test references either..."},
            {"role": "tool_call", "content": "grep -rn \"from.*api/v1\\|from.*v1/\" src/tests/ --include='*.ts'"},
            {"role": "tool_result", "content": "src/tests/api/v1/users.test.ts references deprecated routes"},
            {"role": "assistant", "content": "Found test dependency. Deleting tests first to avoid orphan."},
            {"role": "tool_call", "content": "rm -rf src/tests/api/v1 && rm -rf src/api/v1"},
            {"role": "tool_result", "content": "Deleted."},
            {"role": "assistant", "content": "**Verification:**"},
            {"role": "tool_call", "content": "ls src/api/v1 2>&1 || echo 'Directory removed'"},
            {"role": "tool_result", "content": "Directory removed"},
            {"role": "tool_call", "content": "npx tsc --noEmit 2>&1 | head -5"},
            {"role": "tool_result", "content": "Build clean. No errors."},
            {"role": "assistant", "content": "**Safe Ops: COMPLETE**\n- Backup: `/tmp/backup-20260329-143022-api-v1/`\n- 2 directories removed\n- Verification: clean build\n- If rollback needed: `cp -r /tmp/backup-20260329-143022-api-v1/* src/api/v1/`"}
        ]
    },

    # -------------------------------------------------------------------------
    # 13. Context Expiry - Long session management
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_context_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Continue with the database migration we were working on. What was the status?"},
            {"role": "assistant", "content": "**Context Checkpoint - Re-stating constraints**\n\nWhat I know from earlier in this session:\n- Project: Backend API migration to Prisma\n- Current task: Add `lastLoginAt` to User model\n- Completed: Prisma schema updated, client regenerated\n- Remaining: Apply migration to database, update UserService type\n- Version target: Node 20+, Prisma 5.x\n\nChecking current state of UserService..."},
            {"role": "tool_call", "content": "grep -n 'lastLoginAt' src/services/user_service.ts || echo 'NOT FOUND'"},
            {"role": "tool_result", "content": "NOT FOUND"},
            {"role": "assistant", "content": "UserService still needs the `lastLoginAt` field added. Applying now."},
            {"role": "tool_call", "content": "grep -n 'interface User' src/services/user_service.ts -A10"},
            {"role": "tool_result", "content": "interface User {\n  id: string;\n  email: string;\n  createdAt: Date;\n  // Missing lastLoginAt\n}"},
            {"role": "assistant", "content": "Adding `lastLoginAt?: Date` to User interface."},
            {"role": "assistant", "content": "**Context Self-Cleaning**\n\nFlushing intermediate results:\n- Prisma schema read: flushed\n- Grep outputs: flushed\n- Test outputs from earlier: flushed\n\nRetaining:\n- Project: Backend API migration to Prisma\n- Current task: Add lastLoginAt field - IN PROGRESS\n- Completed: schema, UserService, tests\n- Next: run migration, verify build\n\nContext lean. Ready to continue."}
        ]
    },

    # -------------------------------------------------------------------------
    # 14. Hivemind Agent Registry - Tool registration
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_hivemind_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Register a new code review agent with capabilities for TypeScript and security patterns."},
            {"role": "assistant", "content": "**Hivemind Agent Registry**\n\nRegistering new agent..."},
            {"role": "tool_call", "content": "cat >> ~/.floyd/hivemind/agents.json << 'EOF'\n{\n  \"id\": \"agent-code-reviewer\",\n  \"name\": \"Code Review Specialist\",\n  \"type\": \"reviewer\",\n  \"capabilities\": [\"typescript\", \"javascript\", \"security\", \"code-review\", \"eslint\", \"prettier\"],\n  \"status\": \"idle\",\n  \"lastSeen\": 1743272400000,\n  \"currentTasks\": [],\n  \"completedTasks\": 0,\n  \"averageScore\": 0.0\n}\nEOF"},
            {"role": "tool_result", "content": "Agent registered: agent-code-reviewer"},
            {"role": "assistant", "content": "**Agent Registration: COMPLETE**\n- ID: agent-code-reviewer\n- Type: reviewer\n- Capabilities: typescript, javascript, security, code-review\n- Status: idle\n\nTask assignment will be capability-matched. Heartbeat monitoring active (30s interval)."}
        ]
    },

    # -------------------------------------------------------------------------
    # 15. Stale Agent Cleanup - Agent timeout
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_stale_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Check for stale agents and release their tasks."},
            {"role": "assistant", "content": "**Hivemind Stale Agent Cleanup**\n\nScanning agents with 60s timeout threshold (lastSeen > 60s ago = stale)..."},
            {"role": "tool_call", "content": "cat ~/.floyd/hivemind/agents.json | python3 -c \"import json,sys; agents=json.load(sys.stdin); now=1743272400; stale=[a for a in agents if now - a['lastSeen']/1000 > 60]; print(f'Stale: {len(stale)}'); [print(f\\\"  {a['id']}: lastSeen {now - a['lastSeen']/1000:.0f}s ago\\\") for a in stale]\""},
            {"role": "tool_result", "content": "Stale agents found: 2\n  agent-migrator: lastSeen 847s ago\n  agent-doc-writer: lastSeen 203s ago"},
            {"role": "assistant", "content": "**Releasing tasks from stale agents...**\n\nagent-migrator: releasing 3 tasks (PRIMARY KEY task still in_progress)\nagent-doc-writer: releasing 1 task\n\nSetting agent status to 'offline'..."},
            {"role": "tool_call", "content": "python3 -c \"\nimport json\nwith open('~/.floyd/hivemind/agents.json') as f:\n    agents = json.load(f)\nfor a in agents:\n    if a['id'] in ('agent-migrator', 'agent-doc-writer'):\n        a['status'] = 'offline'\n        a['currentTasks'] = []\nwith open('~/.floyd/hivemind/agents.json', 'w') as f:\n    json.dump(agents, f, indent=2)\nprint('Agents marked offline, tasks released')\n\""},
            {"role": "tool_result", "content": "Agents marked offline, tasks released"},
            {"role": "assistant", "content": "**Stale Cleanup: COMPLETE**\n- 2 agents marked offline\n- 4 tasks released to queue\n- Ready for reassignment to available agents\n\nActive agents remaining: 6"}
        ]
    },

    # -------------------------------------------------------------------------
    # 16. Change Impact - Test file modification
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_cia_test_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Add a new test case to the auth.test.ts file."},
            {"role": "assistant", "content": "**Change Impact Analysis**\n\nTest file modification detected.\n- Test files are consumers: they import from source\n- New test for `verifyTokenExpiry` function"},
            {"role": "tool_call", "content": "grep -n 'verifyTokenExpiry' src/tests/auth.test.ts || echo 'NOT FOUND'"},
            {"role": "tool_result", "content": "NOT FOUND"},
            {"role": "assistant", "content": "Adding test case to auth.test.ts:\n```typescript\ndescribe('verifyTokenExpiry', () => {\n  test('returns true for valid non-expired token', () => {\n    const token = jwt.sign({ userId: '123' }, SECRET, { expiresIn: '1h' });\n    expect(verifyTokenExpiry(token)).toBe(true);\n  });\n\n  test('returns false for expired token', () => {\n    const token = jwt.sign({ userId: '123' }, SECRET, { expiresIn: '-1h' });\n    expect(verifyTokenExpiry(token)).toBe(true); // BUG: should be false\n  });\n});\n```\n\nWait - there's a bug in my test. Let me fix it."},
            {"role": "assistant", "content": "**Self-correction:**\nLine should be `toBe(false)` for expired token, not `toBe(true)`.\n\nFixing..."},
            {"role": "tool_call", "content": "sed -i \"s/expect(verifyTokenExpiry(token)).toBe(true); \\/\\/ BUG/expect(verifyTokenExpiry(token)).toBe(false);/\" src/tests/auth.test.ts"},
            {"role": "assistant", "content": "Verification:"},
            {"role": "tool_call", "content": "npx jest src/tests/auth.test.ts --testNamePattern='verifyTokenExpiry'"},
            {"role": "tool_result", "content": "PASS  verifyTokenExpiry\n  returns true for valid non-expired token\n  returns false for expired token\n\n2 tests passed"},
            {"role": "assistant", "content": "**Change Impact: LOW**\n- Test file only, no source code changes\n- No downstream consumers affected\n- Tests validate existing source code\n- Verification: passed"}
        ]
    },

    # -------------------------------------------------------------------------
    # 17. Error Resolution - Test failure cascade
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_error_test_001",
        "system": "debug",
        "messages": [
            {"role": "user", "content": "The tests are failing after our refactor."},
            {"role": "tool_call", "content": "npx jest 2>&1 | tail -30"},
            {"role": "tool_result", "content": "FAIL src/tests/user_service.test.ts\n  Type error: Cannot find name 'UserService'\n\nFAIL src/tests/auth.test.ts\n  Type error: Cannot find name 'verifyTokenExpiry'\n\nFAIL src/tests/payment.test.ts\n  Type error: Cannot find name 'PaymentProcessor'"},
            {"role": "assistant", "content": "**Error Resolution Engine**\n\n3 test files all showing 'Cannot find name' errors.\nThis is a CLASSIC cascade: one root cause (likely removed or renamed an export)."},
            {"role": "tool_call", "content": "grep -n 'export.*UserService' src/services/user_service.ts"},
            {"role": "tool_result", "content": "No output - NOT exported"},
            {"role": "tool_call", "content": "git diff src/services/user_service.ts | head -40"},
            {"role": "tool_result", "content": "-export class UserService {"},
            {"role": "assistant", "content": "**Root cause found: UserService export was removed**\n\nSomeone removed `export` keyword from the class declaration during the refactor. This broke all 3 test files because they import UserService.\n\nFixing UserService export..."},
            {"role": "tool_call", "content": "sed -i 's/^class UserService {/export class UserService {/' src/services/user_service.ts"},
            {"role": "tool_call", "content": "grep -n 'export.*verifyTokenExpiry' src/core/auth.ts"},
            {"role": "tool_result", "content": "No output - NOT exported"},
            {"role": "assistant", "content": "Also missing verifyTokenExpiry export. Fixing..."},
            {"role": "tool_call", "content": "sed -i 's/^function verifyTokenExpiry/export function verifyTokenExpiry/' src/core/auth.ts"},
            {"role": "tool_call", "content": "npx jest 2>&1 | tail -5"},
            {"role": "tool_result", "content": "All tests passing. 47 tests in 3.2s."},
            {"role": "assistant", "content": "**Error Resolution: COMPLETE**\n- Root cause: 2 missing `export` keywords\n- Cascade: 3 test files affected\n- Fix: Added `export` to UserService and verifyTokenExpiry\n- Verification: All 47 tests passing\n\n**Pattern crystallized:** After any refactor that touches function/class declarations, verify exports are intact. Missing `export` silently breaks all importers."}
        ]
    },

    # -------------------------------------------------------------------------
    # 18. Prefix Mode Detection - CLI command parsing
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_prefix_001",
        "system": "concise",
        "messages": [
            {"role": "user", "content": "Search for all files containing 'JWT' in the src directory."},
            {"role": "assistant", "content": "Detected `/` prefix - search mode."},
            {"role": "tool_call", "content": "grep -rl 'JWT' src/ --include='*.ts'"},
            {"role": "tool_result", "content": "src/core/auth.ts\nsrc/services/auth_service.ts\nsrc/middleware/auth.ts\nsrc/types/auth.ts"},
            {"role": "assistant", "content": "Found 4 files. Found JWT references in auth infrastructure."}
        ]
    },

    # -------------------------------------------------------------------------
    # 19. Recursive Crystallization Loop - Session close
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_loop_001",
        "system": "learning",
        "messages": [
            {"role": "user", "content": "Wrap up. What did we accomplish?"},
            {"role": "assistant", "content": "**Learning Engine: Session Summary**\n\nPatterns executed this session:\n1. Change Impact Analyzer - 3 times (file edits, test changes)\n2. Pre-Edit Intelligence - 2 times (renames, extractions)\n3. Error Resolution Engine - 2 times (build errors, test failures)\n4. Schema Fortress - 1 time (Prisma migration)\n5. Architectural Guardian - 1 time (core file edit)\n6. Predictive Analyzer - 1 time (tree traversal)\n\nCrystallizing outcomes to SUPERCACHE..."},
            {"role": "tool_call", "content": "cat > ~/.floyd/supercache/vault/session-$(date +%Y%m%d).json << 'EOF'\n{\n  \"date\": \"2026-03-29\",\n  \"patterns_applied\": 6,\n  \"positive_outcomes\": [\n    { \"pattern\": \"Error Resolution\", \"fix\": \"Missing export keywords cascade to tests\", \"lesson\": \"Verify exports after refactors\" },\n    { \"pattern\": \"Predictive Analyzer\", \"fix\": \"Added depth limit to recursion\", \"lesson\": \"Bounded recursion prevents stack overflow\" }\n  ],\n  \"negative_outcomes\": [],\n  \"files_modified\": 8,\n  \"tests_passed\": 47,\n  \"session_id\": \"session-20260329\"\n}\nEOF"},
            {"role": "tool_result", "content": "Stored to SUPERCACHE vault."},
            {"role": "assistant", "content": "**Session Complete**\n- 6 Floyd patterns applied\n- 2 lessons crystallized\n- 8 files modified\n- 47 tests passing\n- SUPERCACHE updated\n\nRecursive crystallization loop: ACTIVE"}
        ]
    },

    # -------------------------------------------------------------------------
    # 20. Douglas Trust Protocol - Explicit confirmation
    # -------------------------------------------------------------------------
    {
        "id": "multiturn_trust_001",
        "system": "default",
        "messages": [
            {"role": "user", "content": "Deploy to production."},
            {"role": "assistant", "content": "**Douglas Trust Protocol**\n\nDeployment is a production-critical operation. Before proceeding, I need to confirm the exact target.\n\nWhich production environment should I deploy to?\n- `precisionsewerinspections.com` (primary live)\n- `precisionsewerinspection.com` (SEO build target)\n\nConfirm which one, and I will proceed with the deployment."},
            {"role": "user", "content": "precisionsewerinspections.com"},
            {"role": "assistant", "content": "Confirmed: `precisionsewerinspections.com` (primary live).\n\nProceeding with deployment..."},
            {"role": "tool_call", "content": "echo 'Deploying to precisionsewerinspections.com...'"},
            {"role": "tool_result", "content": "Deployment initiated"},
            {"role": "assistant", "content": "Deployed. Pipeline running."}
        ]
    },

]


def generate_multi_turn(output_file: str) -> int:
    """Generate all multi-turn conversation training examples."""
    count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        for conv in CONVERSATIONS:
            system_key = conv.get("system", "default")
            system_prompt = SYSTEM_PROMPTS[system_key]["prompt"]

            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation turns
            for msg in conv["messages"]:
                role = msg["role"]
                content = msg["content"]
                messages.append({"role": role, "content": content})

            record = {"messages": messages}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count


if __name__ == "__main__":
    output_path = Path(__file__).parent / "multi_turn_training.jsonl"
    count = generate_multi_turn(output_path)
    print(f"Generated {count} multi-turn conversation examples")
    print(f"Saved to: {output_path}")
