#!/usr/bin/env python3
"""
Generate anti-pattern training data with negative examples and consequences.
Outputs ChatML format with enhanced system prompt emphasizing correctness verification.
"""
import json
from pathlib import Path

SYSTEM_PROMPT = (
    "You are an elite live coding assistant. You strictly adhere to "
    "canonical patterns, enforcement rules, and architectural constraints. "
    "NEVER assume code compiles. ALWAYS validate coverage. Explore edge cases, "
    "not from edge cases. If wrong, fix immediately. If coverage declines, address it."
)

ANTI_PATTERNS = [
    # Silent Failure Prevention
    {
        "pattern_name": "Silent Failure Prevention - Never Delete Failing Tests",
        "trigger": "When tests fail after code changes",
        "enforcement_rule": "NEVER delete or skip failing tests. MANDATORY: (1) Investigate root cause, (2) Fix the underlying bug, (3) Document the fix, (4) Verify test passes. Deleting tests creates false confidence.",
        "canonical_implementation": "# Silent failure prevention\ndef handle_failing_test(test_result):\n    # Step 1: Investigate root cause\n    root_cause = analyze_failure(test_result)\n    # Step 2: Fix the bug\n    fix = develop_fix(root_cause)\n    apply_fix(fix)\n    # Step 3: Document the fix\n    document_fix(root_cause, fix)\n    # Step 4: Verify\n    assert test_passes(test_result), f'Test still fails: {test_result.name}'",
        "negative_example": "# WRONG - Silent failure\nif test_fails():\n    delete_test(failed_test)  # NO - masks bugs\n    print('Test removed')  # Creates false confidence",
        "consequences": "Deleting tests hides bugs, creates false confidence in code quality, leads to production incidents, and erodes trust."
    },
    {
        "pattern_name": "Silent Failure Prevention - Always Verify Observables",
        "trigger": "After implementing any code change",
        "enforcement_rule": "NEVER assume code works because it compiles. MANDATORY: (1) Run the code, (2) Check return values, (3) Verify side effects, (4) Test with real inputs.",
        "canonical_implementation": "# Always verify observables\ndef verify_implementation(code_change):\n    result = execute(code_change)\n    assert result.return_value is not None\n    assert logs_contain(expected_messages)\n    assert state_changed_as_expected()\n    real_input = load_real_test_data()\n    output = code_change(real_input)\n    assert output_matches_expected(output)",
        "negative_example": "# WRONG - No verification\nif compiles(code):\n    commit(code)  # NO - compilation != correctness\n    print('Done!')  # Silent failure risk",
        "consequences": "Code that compiles but produces incorrect behavior is the most dangerous failure mode."
    },
    {
        "pattern_name": "Silent Failure Prevention - Handle Null Edge Cases",
        "trigger": "When implementing any function that accepts inputs",
        "enforcement_rule": "NEVER assume inputs are valid. MANDATORY: (1) Check for null/undefined, (2) Handle empty collections, (3) Validate ranges, (4) Provide explicit error messages.",
        "canonical_implementation": "# Handle null edge cases\ndef process_data(data):\n    if data is None:\n        raise ValueError('data cannot be None')\n    if not data:\n        return []\n    if len(data) > MAX_SIZE:\n        raise ValueError(f'data exceeds max size: {MAX_SIZE}')\n    return [transform(item) for item in data]",
        "negative_example": "# WRONG - No null check\ndef process_data(data):\n    return data.transform()  # Crashes on None",
        "consequences": "Missing null checks cause runtime crashes, silent data corruption, and undefined behavior."
    },
    {
        "pattern_name": "Silent Failure Prevention - Never Mask Exceptions",
        "trigger": "When implementing error handling",
        "enforcement_rule": "NEVER use bare except clauses that swallow exceptions. MANDATORY: (1) Catch specific exception types, (2) Log the error with context, (3) Either re-raise, return error, or handle explicitly.",
        "canonical_implementation": "# Never mask exceptions\ntry:\n    result = risky_operation()\nexcept SpecificException as e:\n    logger.error(f'Operation failed: {e}', exc_info=True)\n    raise\nexcept AnotherException as e:\n    logger.warning(f'Recoverable error: {e}')\n    return fallback_value()",
        "negative_example": "# WRONG - Masking exceptions\ntry:\n    result = risky_operation()\nexcept:  # NO - catches everything\n    pass  # Silent failure - error is lost",
        "consequences": "Masked exceptions hide errors, make debugging impossible, and create silent failures that corrupt state."
    },
    {
        "pattern_name": "Silent Failure Prevention - Validate Against Documentation",
        "trigger": "After implementing any feature",
        "enforcement_rule": "NEVER assume implementation matches spec. MANDATORY: (1) Read requirements, (2) Implement, (3) Verify each requirement explicitly, (4) Document any deviations.",
        "canonical_implementation": "# Validate against documentation\ndef validate_implementation(feature, requirements):\n    for req in requirements:\n        actual = feature.get_behavior(req.description)\n        expected = req.expected_behavior\n        if actual != expected:\n            raise ValidationError(\n                f'Requirement not met: {req.id}\\n'\n                f'Expected: {expected}\\n'\n                f'Actual: {actual}'\n            )\n    return True",
        "negative_example": "# WRONG - No validation\ndef implement_feature(req):\n    code = write_code(req.description)\n    return code  # No verification against spec",
        "consequences": "Implementation that doesn't match requirements is a silent failure. Always validate against documented requirements."
    },
    # Context Drift Prevention
    {
        "pattern_name": "Context Drift Prevention - Re-state Constraints Periodically",
        "trigger": "After 10+ tool calls or when context approaches 50% capacity",
        "enforcement_rule": "NEVER assume earlier constraints are remembered. MANDATORY: (1) Re-state critical constraints, (2) Confirm no conflicts introduced, (3) Log explicit 'what I know' summary.",
        "canonical_implementation": "# Context drift prevention\ndef context_checkpoint(session):\n    constraints = session.get_active_constraints()\n    for constraint in constraints:\n        logger.info(f'Active constraint: {constraint}')\n    conflicts = find_conflicting_assumptions(session.history)\n    if conflicts:\n        raise ConflictError(f'Conflicting assumptions: {conflicts}')\n    logger.info(f'Current knowledge: {session.knowledge_summary()}')",
        "negative_example": "# WRONG - No checkpoint\n# After 50 turns...\ndef continue_work():\n    implement_feature()  # May violate forgotten constraints",
        "consequences": "Context drift causes models to forget constraints, hallucinate facts, and compound errors."
    },
    {
        "pattern_name": "Context Drift Prevention - Verify Version Constraints",
        "trigger": "When implementing any code that depends on libraries or runtimes",
        "enforcement_rule": "NEVER assume default versions. MANDATORY: (1) Check documented version requirements, (2) Use version-appropriate APIs, (3) Test in target environment.",
        "canonical_implementation": "# Version constraint verification\ndef check_version_constraints(requirements):\n    for dep in requirements.dependencies:\n        actual = get_installed_version(dep.name)\n        if not version_matches(actual, dep.constraint):\n            raise VersionError(f'{dep.name}: {actual} does not match {dep.constraint}')\n    if version_lt(runtime_version, '3.11'):\n        return legacy_implementation()\n    return modern_implementation()",
        "negative_example": "# WRONG - No version check\nimport some_library\nresult = some_library.new_method()  # May not exist in target version",
        "consequences": "Version mismatches cause runtime errors in production that don't appear in development."
    },
    {
        "pattern_name": "Context Drift Prevention - Detect Hallucinated Imports",
        "trigger": "When adding any import statement",
        "enforcement_rule": "NEVER import packages that may not exist. MANDATORY: (1) Verify package exists in requirements, (2) Check package name spelling, (3) Confirm the imported symbol exists.",
        "canonical_implementation": "# Detect hallucinated imports\ndef verify_import(module_name, symbol=None):\n    if not package_exists(module_name):\n        raise ImportError(f'Package does not exist: {module_name}')\n    if not in_requirements(module_name):\n        raise ImportError(f'Package not in requirements: {module_name}')\n    if symbol and not symbol_exists(module_name, symbol):\n        raise ImportError(f'Symbol not found: {module_name}.{symbol}')\n    return True",
        "negative_example": "# WRONG - Hallucinated import\nimport fancy_utils  # Package doesn't exist\nfrom lodash import debounce  # Wrong package name",
        "consequences": "Hallucinated imports cause immediate runtime failures. Always verify imports exist."
    },
    # Almost-Right Prevention
    {
        "pattern_name": "Almost-Right Prevention - Test Boundary Conditions",
        "trigger": "After implementing any algorithm or loop",
        "enforcement_rule": "NEVER trust off-by-one assumptions. MANDATORY: (1) Test first element, (2) Test last element, (3) Test empty input, (4) Test single element, (5) Verify loop boundaries.",
        "canonical_implementation": "# Test boundary conditions\ndef test_boundaries(algorithm):\n    assert algorithm([]) == expected_empty_result\n    assert algorithm([1]) == expected_single_result\n    result = algorithm([1, 2, 3])\n    assert first_element_correct(result)\n    assert last_element_correct(result)\n    assert len(result) == expected_length",
        "negative_example": "# WRONG - No boundary tests\ndef process_items(items):\n    for i in range(len(items)):  # Off-by-one risk\n        process(items[i])",
        "consequences": "Off-by-one errors work in most cases but fail at boundaries. These bugs often only appear in production."
    },
    {
        "pattern_name": "Almost-Right Prevention - Handle Empty Collections",
        "trigger": "When iterating over or processing collections",
        "enforcement_rule": "NEVER assume collections are non-empty. MANDATORY: (1) Check if empty, (2) Return appropriate empty result, (3) Document empty behavior.",
        "canonical_implementation": "# Handle empty collections\ndef process_collection(items):\n    if not items:\n        return []\n    return [transform(item) for item in items]",
        "negative_example": "# WRONG - No empty check\ndef process_collection(items):\n    first = items[0]  # IndexError on empty\n    return process(first)",
        "consequences": "Empty collection bugs crash at runtime with IndexError. Always handle empty explicitly."
    },
    {
        "pattern_name": "Almost-Right Prevention - Verify API Signatures",
        "trigger": "When calling any external API or library function",
        "enforcement_rule": "NEVER assume API signatures from memory. MANDATORY: (1) Check documentation for exact signature, (2) Verify parameter types and order, (3) Check return type.",
        "canonical_implementation": "# Verify API signatures\ndef call_external_api(api, params):\n    expected_params = get_documented_params(api)\n    for param in params:\n        assert param in expected_params, f'Unknown param: {param}'\n    for param, value in params.items():\n        expected_type = expected_params[param].type\n        assert isinstance(value, expected_type)\n    return api(**params)",
        "negative_example": "# WRONG - Assumed signature\nresult = api.fetch(id=user_id, limit=10)  # Wrong param order or name",
        "consequences": "Wrong API signatures cause runtime errors or silent incorrect behavior."
    },
    # Implicit Defaults Prevention
    {
        "pattern_name": "Implicit Defaults Prevention - Explicit Timezone Handling",
        "trigger": "When working with dates, times, or timestamps",
        "enforcement_rule": "NEVER rely on implicit timezone defaults. MANDATORY: (1) Explicitly set timezone, (2) Document timezone assumptions, (3) Convert at boundaries.",
        "canonical_implementation": "# Explicit timezone handling\nfrom datetime import datetime, timezone\n\ndef process_timestamp(ts, input_tz='UTC'):\n    if isinstance(ts, str):\n        dt = datetime.fromisoformat(ts)\n        if dt.tzinfo is None:\n            dt = dt.replace(tzinfo=timezone.utc)\n    working_tz = get_working_timezone()\n    dt = dt.astimezone(working_tz)\n    return transform(dt)",
        "negative_example": "# WRONG - Implicit timezone\ndef process_timestamp(ts):\n    dt = datetime.parse(ts)  # No timezone\n    return dt.hour  # Ambiguous",
        "consequences": "Implicit timezone bugs only appear in production with real user data across timezones."
    },
    {
        "pattern_name": "Implicit Defaults Prevention - Explicit Pagination Order",
        "trigger": "When implementing pagination queries",
        "enforcement_rule": "NEVER use LIMIT without ORDER BY. MANDATORY: (1) Always include deterministic ORDER BY, (2) Use cursor-based pagination when possible.",
        "canonical_implementation": "# Explicit pagination with ORDER BY\nquery = '''\nSELECT * FROM items\nWHERE created_at > :cursor\nORDER BY created_at ASC, id ASC\nLIMIT :page_size\n'''",
        "negative_example": "# WRONG - No ORDER BY\nquery = 'SELECT * FROM items LIMIT 10 OFFSET 0'\n# Non-deterministic results on replica clusters",
        "consequences": "LIMIT without ORDER BY returns non-deterministic results, especially on replica clusters."
    },
    # Security Prevention
    {
        "pattern_name": "Security Prevention - Parameterized Queries",
        "trigger": "When building any database query with user input",
        "enforcement_rule": "NEVER use string concatenation for queries. MANDATORY: (1) Use parameterized queries, (2) Validate input type/length, (3) Use ORM when available.",
        "canonical_implementation": "# Parameterized queries\nquery = 'SELECT * FROM users WHERE id = ?'\ncursor.execute(query, (user_id,))\n\nquery = 'SELECT * FROM users WHERE email = :email'\ncursor.execute(query, {'email': user_email})",
        "negative_example": "# WRONG - SQL injection\nquery = f'SELECT * FROM users WHERE id = {user_id}'\ncursor.execute(query)",
        "consequences": "SQL injection allows attackers to execute arbitrary database commands."
    },
    {
        "pattern_name": "Security Prevention - Never Hardcode Secrets",
        "trigger": "When implementing authentication or API access",
        "enforcement_rule": "NEVER hardcode credentials. MANDATORY: (1) Use environment variables, (2) Use secret management, (3) Never log secrets, (4) Rotate regularly.",
        "canonical_implementation": "# Secure credential handling\nimport os\nAPI_KEY = os.environ.get('API_KEY')\nif not API_KEY:\n    raise ValueError('API_KEY environment variable not set')",
        "negative_example": "# WRONG - Hardcoded secret\nAPI_KEY = 'sk-1234567890abcdef'\npassword = 'admin123'",
        "consequences": "Hardcoded secrets are exposed in source control, logs, and error messages."
    },
    {
        "pattern_name": "Security Prevention - Input Validation",
        "trigger": "When accepting any user input",
        "enforcement_rule": "NEVER trust user input. MANDATORY: (1) Validate type, (2) Validate length/range, (3) Validate format, (4) Sanitize for output context.",
        "canonical_implementation": "# Input validation\ndef validate_user_input(data):\n    if not isinstance(data.get('id'), int):\n        raise ValidationError('id must be integer')\n    if not 1 <= data['id'] <= MAX_ID:\n        raise ValidationError('id out of range')\n    if not re.match(r'^[a-zA-Z0-9]+$', data.get('name', '')):\n        raise ValidationError('name contains invalid characters')\n    return data",
        "negative_example": "# WRONG - No validation\ndef process_user(data):\n    user_id = data['id']  # Trusts input",
        "consequences": "Unvalidated input leads to injection attacks, data corruption, and crashes."
    },
    # Recursive Logic Prevention
    {
        "pattern_name": "Recursive Logic Prevention - Guarantee Termination",
        "trigger": "When implementing any recursive function",
        "enforcement_rule": "NEVER implement recursion without termination guarantee. MANDATORY: (1) Identify base case(s), (2) Ensure state changes toward base case, (3) Add maximum depth limit.",
        "canonical_implementation": "# Recursive with termination guarantee\ndef recursive_process(data, depth=0, max_depth=100):\n    if is_base_case(data):\n        return base_result(data)\n    if depth >= max_depth:\n        raise RecursionError(f'Max depth exceeded: {max_depth}')\n    smaller_data = reduce(data)\n    return recursive_process(smaller_data, depth + 1, max_depth)",
        "negative_example": "# WRONG - No termination\ndef process(data):\n    if data is None:\n        return None\n    return process(data)  # Infinite recursion!",
        "consequences": "Infinite recursion causes stack overflow crashes. Every recursive function MUST have provable termination."
    },
    {
        "pattern_name": "Recursive Logic Prevention - Add Depth Limits",
        "trigger": "When implementing recursion on untrusted input",
        "enforcement_rule": "NEVER allow unbounded recursion depth. MANDATORY: (1) Set maximum depth, (2) Return error when exceeded, (3) Consider iterative alternative.",
        "canonical_implementation": "# Recursion with depth limit\ndef traverse_tree(node, depth=0, max_depth=50):\n    if depth > max_depth:\n        logger.warning(f'Depth limit reached: {max_depth}')\n        return None\n    result = process(node)\n    for child in node.children:\n        result += traverse_tree(child, depth + 1, max_depth)\n    return result",
        "negative_example": "# WRONG - No depth limit\ndef traverse_tree(node):\n    result = process(node)\n    for child in node.children:\n        result += traverse_tree(child)  # Stack overflow on deep trees",
        "consequences": "Unbounded recursion causes stack overflow on deep inputs. Always add depth limits."
    },
    # Over-Engineering Prevention
    {
        "pattern_name": "Over-Engineering Prevention - Justify Abstractions",
        "trigger": "When creating any new abstraction, interface, or pattern",
        "enforcement_rule": "NEVER create abstractions without proven need. MANDATORY: (1) Count implementations - if only 1, don't abstract, (2) Wait for 2nd use case, (3) Prefer composition over inheritance.",
        "canonical_implementation": "# Good abstraction (2+ implementations)\nclass DataProcessor:\n    def process(self, data): raise NotImplementedError\n\nclass JsonProcessor(DataProcessor): ...\nclass XmlProcessor(DataProcessor): ...\n\n# Bad abstraction (only 1 implementation)\nclass SingletonProcessor:\n    def process(self, data): ...  # Why abstract?",
        "negative_example": "# WRONG - Premature abstraction\ninterface IUserService {\n    getUser(id: string): User\n}\nclass UserService implements IUserService {  # Only implementation\n    getUser(id) { return db.find(id) }\n}",
        "consequences": "Premature abstractions increase complexity without benefit. DRY at 2."
    },
    {
        "pattern_name": "Over-Engineering Prevention - Prefer Specific Solutions",
        "trigger": "When choosing between specific and generic solutions",
        "enforcement_rule": "NEVER build generic framework for specific problem. MANDATORY: (1) Solve specific problem first, (2) Only generalize when 2nd use case appears.",
        "canonical_implementation": "# SPECIFIC (good):\ndef format_currency(amount: float) -> str:\n    return f'${amount:,.2f}'\n\n# GENERIC (over-engineered for single use):\nclass GenericFormatter:\n    def __init__(self, symbol, decimals): ...\n    def format(self, amount): ...",
        "negative_example": "# WRONG - Generic framework for simple problem\nframework = ConfigurationFramework()\nframework.register('currency', CurrencyFormatter())\n# But we only need currency formatting...",
        "consequences": "Generic frameworks for specific problems increase cognitive load and bug surface area."
    },
    # Trust Erosion Prevention
    {
        "pattern_name": "Trust Erosion Prevention - Verify AI Output",
        "trigger": "When reviewing any AI-generated code",
        "enforcement_rule": "NEVER blindly trust AI-generated code. MANDATORY: (1) Read and understand the code, (2) Check edge cases, (3) Verify against requirements, (4) Test with real inputs.",
        "canonical_implementation": "# Verify AI output\ndef review_ai_code(code, requirements):\n    if not code_is_understandable(code):\n        request_explanation()\n    for edge_case in identify_edge_cases(requirements):\n        assert code_handles(edge_case)\n    for req in requirements:\n        assert requirement_satisfied(code, req)\n    test_with_real_data(code)",
        "negative_example": "# WRONG - Blind trust\nai_code = generate_code(requirements)\ncommit(ai_code)  # No review, no testing",
        "consequences": "Blind trust in AI leads to subtle bugs that take longer to fix than writing from scratch."
    },
    {
        "pattern_name": "Trust Erosion Prevention - Maintain Critical Thinking",
        "trigger": "When using AI assistance for complex decisions",
        "enforcement_rule": "NEVER disengage critical thinking. MANDATORY: (1) Question suggestions, (2) Verify reasoning, (3) Consider alternatives, (4) Make final decision yourself.",
        "canonical_implementation": "# Maintain critical thinking\ndef evaluate_ai_suggestion(suggestion):\n    why_valid = analyze_reasoning(suggestion.reasoning)\n    independently_verify(suggestion.solution)\n    alternatives = generate_alternatives(suggestion.problem)\n    return choose_best(suggestion, alternatives)",
        "negative_example": "# WRONG - Cognitive disengagement\nai_suggestion = get_ai_suggestion(problem)\nimplement(ai_suggestion)  # No critical thought",
        "consequences": "Cognitive disengagement erodes skills and leads to poor decisions."
    },
]


def generate_chatml_examples(output_file: str):
    """Generate ChatML format training examples from anti-patterns."""
    count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        for pattern in ANTI_PATTERNS:
            user_content = (
                f"Pattern: {pattern['pattern_name']}\n"
                f"Trigger: {pattern['trigger']}\n\n"
                f"Enforcement Rule: {pattern['enforcement_rule']}\n\n"
                f"Negative Example (NEVER do this):\n{pattern.get('negative_example', 'N/A')}\n\n"
                f"Consequences: {pattern.get('consequences', 'N/A')}"
            )
            assistant_content = (
                f"# {pattern['pattern_name']}\n\n"
                f"{pattern['canonical_implementation']}"
            )
            record = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content},
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


if __name__ == "__main__":
    output_path = Path(__file__).parent / "anti_patterns_training.jsonl"
    count = generate_chatml_examples(output_path)
    print(f"Generated {count} anti-pattern examples")
    print(f"Saved to: {output_path}")
