# Repository Guidelines

## Overview

ML training data preparation project for fine-tuning Qwen-based coding assistant models. Transforms "Floyd patterns" (code quality enforcement rules) into ChatML training format.

 
## Purpose

Build a personal coding assistant model fine-tuned on Qwen architecture that strictly adheres to the10 "Floyd patterns" - canonical enforcement rules for code quality throughout the development lifecycle.

- Change impact analysis before editing
- error resolution after build failures
- dependency health validation after refactoring
- schema changes
- task complexity scoring
- completion quality gates
- pre-execution bug detection
- post-task knowledge extraction

 ## Architecture & Data flow

 ```
`
┌─────────────┐      ┌──────────────────────┐      ┌────────────┐
 │             │                      │                        │                  │
 │  floyd-  │  JSONL (10)   │  format_dataset.py  │  ChatML (JSONL) │  qwen-   │
 │ patterns │                      │                        │                  │
 └─────────┘      └──────────────────────┘      └────────────┘
                    │                      │                        │                  │
```
 **Data transformation:**
  - Input: `Training/floyd-patterns-export.jsonl` (10 Floyd patterns)
  - Output: `Training/qwen_training_dataset.jsonl` (ChatML training dataset)
 
 **Floyd patterns are executed in this order:**
  1. Change Impact analyzer (post-edit validation)
  2. Error resolution engine (build errors)
  3. Dependency health check (import validation)
  4. Pre-edit intelligence (refactoring planning)
  5. Architectural guardian (core file protection)
  6. Schema fortress (schema changes)
  7. Task calibrator (complexity scoring)
  8. Completion fortress (completion quality gates)
  9. Predictive analyzer (pre-execution bug detection)
  10. Learning engine (post-task knowledge extraction)
 
 **Each pattern has:**
  - `pattern_name`: Identifier
  - `trigger`: When to invoke
  - `enforcement_rule`: Hard limits/non-negotiables
  - `canonical_implementation`: Pseudocode implementation
 
 ## Key directories
 | Directory | Purpose |
|-----------|---------|
 | `Training/` | Data transformation scripts and datasets |
 | `.omp/agents/` | Oh My Pi agent configuration |
 
 ## Development commands
 | Command | Description |
|---------|-------------|
 | `python Training/format_dataset.py` | Transform raw patterns into ChatML format |
 | `cd Training && python format_dataset.py` | Run from Training directory |
 
 **Note:** No package.json or Makefile, or other build configuration. Project uses Python stdlib only (json module only).
 
 ## Code conventions
 **Language:** Python 3.x (stdlib only, no external dependencies)
 
 **Formatting:**
 - 4-space indentation
 - Double quotes for strings
 - Snake_case for function names
 - Descriptive variable names
 - Inline comments for non-obvious logic
 - Docstrings for module and function documentation
 
 **File naming:**
 - Python scripts: `snake_case.py`
 - Data files: `kebab-case.jsonl` (JSONL format)
 - Agent configs: `kebab-case.md`
 
 **Error handling:**
 - Try/except blocks for JSON parsing
 - Graceful handling of malformed input
 - Skip invalid lines with warning message
 - Print summary at completion
 
 ## Important files
 | File | Purpose |
|------|---------|
 | `Training/format_dataset.py` | Main entry point - transforms patterns to ChatML |
 | `Training/floyd-patterns-export.jsonl` | Source data - 10 Floyd patterns |
 | `Training/qwen_training_dataset.jsonl` | Output - ChatML training dataset |
 | `.omp/agents/floyd-slm-architect.md` | Agent configuration for SLM pipeline governance |
 
 ## Runtime/tooling preferences
 - **Python:** 3.x required
 - **Dependencies:** None (stdlib only)
 - **Target model:** Qwen 2.5-Coder family
 - **Training format:** ChatML (Openai-compatible)
 
 For actual fine-tuning:
 - **Recommended:** unsloth, torch, transformers
 - **Apple Silicon:** mlx, mlx-lm
 
 ## Testing & QA
 **Current state:** No automated tests (training utility)
 
 **Recommended additions:**
 - Unit tests for `format_dataset.py`
 - Dataset validation script
 - Schema validation for input/output
 
 ## The SLM pipeline
 This project is governed by the `floyd-slm-architect` agent which coordinates:
 - Dataset preparation and validation
 - Fine-tuning readiness checks
 - Training configuration
 - Evaluation strategy
 - Deployment planning
 - Coordination with 'open Floyd' background agent
 
 ## Next steps
 To extend this project:
 1. Create `Training/train_unsloth.py` - LoRA fine-tuning with unsloth
 2. Create `Training/train_mlx.py` - MLX fine-tuning for Apple Silicon
 3. Create `Training/validate_dataset.py` - ChatML format validation
  4. Create `Training/evaluate_model.py` - Model evaluation harness
  5. Create `Training/merge_lora_weights.py` - Merge LoRA weights into base model
