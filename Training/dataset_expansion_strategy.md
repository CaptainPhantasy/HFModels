# Dataset Expansion Strategy for Qwen2.5-Coder Fine-Tuning

## Current State (2026-03-29)
- **floyd-patterns-export.jsonl**: 38 patterns (10 core mega-skills + 28 supplementary)
- **qwen_training_dataset.jsonl**: 39 rows in ChatML format
- **Research finding**: Need 500-1000+ examples minimum for effective fine-tuning

## Gap Analysis

### Problem: Dataset Too Small
Research shows that fine-tuning on small datasets (<1000 examples) leads to:
1. **Overfitting** to narrow patterns
2. **Catastrophic forgetting** of general coding abilities
3. **Alignment drift** - safety guardrails degrade

### Solution: Multi-Source Expansion

## Expansion Plan

### Phase 1: Anti-Pattern Training Data (Critical Priority)
Based on AI_CODING_FAILURE_MODES_RESEARCH.md, create negative examples showing what NOT to do:

**10 Anti-Pattern Categories** (50 examples each = 500 examples):
1. **Silent Failures** - Code that compiles but produces wrong behavior
2. **Context Drift** - Hallucinations that compound over long sessions
3. **Almost-Right Code** - Syntactically correct, logically wrong
4. **Implicit Defaults** - Assumptions that break in production
5. **Security Vulnerabilities** - SQL injection, missing auth, hardcoded secrets
6. **Recursive Logic Failures** - Infinite loops, stack overflow
7. **Over-Engineering** - Unnecessary abstractions, excessive complexity
8. **Dependency Hallucinations** - Packages that don't exist
9. **Test Skipping** - Deleting failing tests instead of fixing bugs
10. **Fake Productivity** - Changes that look complete but aren't

### Phase 2: General Coding Patterns (Medium Priority)
Add breadth to prevent over-narrow specialization:

**Categories** (25 examples each = 250 examples):
1. Error handling patterns (try/catch, null checks)
2. API design patterns (REST, validation, pagination)
3. Database patterns (transactions, indexing, migrations)
4. Concurrency patterns (async/await, locks, queues)
5. Testing patterns (unit, integration, mocking)
6. Refactoring patterns (extract method, rename, move)
7. Documentation patterns (comments, docstrings, README)
8. Logging patterns (structured logging, levels, context)
9. Configuration patterns (env vars, config files, defaults)
10. Deployment patterns (CI/CD, health checks, rollback)


## Data Quality Standards

### Required Fields for Each Example
```json
{
  "pattern_name": "string",
  "trigger": "string (when to apply)",
  "enforcement_rule": "string (hard limits, MANDATORY/MUST/NEVER)",
  "canonical_implementation": "pseudocode or code",
  "category": "anti-pattern | enforcement | general | multi-turn | error-recovery",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "negative_example": "optional - what NOT to do",
  "consequences": "optional - what happens if violated"
}
```

### Anti-Pattern Template
```json
{
  "pattern_name": "Anti-Pattern: Silent Failure - Delete Failing Tests",
  "trigger": "When tests fail after code changes",
  "enforcement_rule": "NEVER delete or skip failing tests to make CI green. MANDATORY: investigate root cause, fix the bug or update the test with explicit justification.",
  "canonical_implementation": "# Step 1: Investigate failure\nfailure = analyze_test_failure(failed_test)\n# Step 2: Identify root cause\nroot_cause = trace_to_source(failure)\n# Step 3: Fix the actual bug\nif root_cause.is_bug:\n    fix_bug(root_cause)\nelif root_cause.is_test_bug:\n    update_test_with_documented_reason(root_cause)\n# Step 4: Verify fix\nassert test_passes()\n# NEVER: delete_test(failed_test)",
  "negative_example": "# WRONG - Silent failure\nif test_fails:\n    delete_test(failed_test)  # NO - masks bugs",
  "consequences": "Deleting tests creates false confidence, hides real bugs, and erodes trust. Coverage metrics become meaningless. Bugs ship to production.",
  "category": "anti-pattern",
  "severity": "CRITICAL"
}
```

## Implementation Order

1. **Immediate**: Create anti-pattern training data (500 examples)
   - This addresses the "silent failure" research findings
   - High-value: prevents the most dangerous failure modes

2. **Short-term**: Add general coding patterns (250 examples)
   - Prevents overfitting to Floyd patterns only
   - Maintains general coding ability


4. **Ongoing**: Mine real-world failures from session history
   - Use SUPERCACHE crystallized patterns
   - Convert to training examples with consequences

## Training Data Generation Script

Create `Training/generate_anti_patterns.py`:
```python
#!/usr/bin/env python3
"""
Generate anti-pattern training data from research findings.
Reads AI_CODING_FAILURE_MODES_RESEARCH.md and generates ChatML examples.
"""

import json
from pathlib import Path

# Anti-pattern templates based on research
ANTI_PATTERNS = [
    {
        "pattern_name": "Silent Failure - Fake Output",
        "trigger": "When generating code that needs to return data",
        "enforcement_rule": "NEVER return hardcoded or fake data that matches expected format but doesn't compute correctly. MANDATORY: implement actual logic, or explicitly return NotImplementedError if genuinely blocked.",
        "negative_example": "# WRONG - Returns fake data\ndef get_user_stats(user_id):\n    return {'total': 100, 'active': 50}  # Hardcoded fake data",
        "canonical_implementation": "# RIGHT - Returns computed data\ndef get_user_stats(user_id):\n    user = db.get_user(user_id)\n    return {\n        'total': user.total_actions,\n        'active': user.recent_actions\n    }",
        "consequences": "Fake data passes superficial review but causes production incidents. Debuggers waste hours tracing 'correct' output that was never real.",
        "category": "anti-pattern",
        "severity": "CRITICAL"
    },
    # ... more anti-patterns
]

def generate_chatml_examples(patterns, output_file):
    system_prompt = (
        "You are an elite live coding assistant. You strictly adhere to "
        "canonical patterns, enforcement rules, and architectural constraints. "
        "NEVER assume code compiles. ALWAYS validate coverage. Explore edge cases, "
        "not from edge cases. If wrong, fix immediately. If coverage declines, address it."
    )
    
    with open(output_file, 'w') as f:
        for pattern in patterns:
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
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content}
                ]
            }
            
            f.write(json.dumps(record) + '\n')

if __name__ == "__main__":
    generate_chatml_examples(ANTI_PATTERNS, "anti_patterns_training.jsonl")
    print(f"Generated {len(ANTI_PATTERNS)} anti-pattern examples")
```

## Success Metrics

- [ ] 500+ anti-pattern examples generated
- [ ] 250+ general coding examples added
- [ ] All examples validated for ChatML compliance
- [ ] Negative examples included with consequences
- [ ] Dataset split: 80% train, 10% validation, 10% test
- [ ] No duplicate patterns
- [ ] Token count per example < 500

## Next Actions

1. Create `Training/generate_anti_patterns.py` with 50 anti-patterns
2. Run script to generate `anti_patterns_training.jsonl` (500 examples)
3. Validate ChatML format with `Training/validate_dataset.py`
4. Merge with existing `floyd-patterns-export.jsonl`
5. Run `Training/format_dataset.py` to regenerate training data
6. Target: 1000+ examples total before fine-tuning
