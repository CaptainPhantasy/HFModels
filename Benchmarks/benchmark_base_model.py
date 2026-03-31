#!/usr/bin/env python3
"""
Floyd Patterns Benchmark Suite
Tests Qwen3-8B base model on coding assistant tasks
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# Set cache location
os.environ["HF_HOME"] = os.path.abspath("../Models/cache")

from mlx_lm import load, generate


# Benchmark prompts for Floyd patterns use case
BENCHMARK_TESTS = [
    # ===== Pattern Recognition =====
    {
        "id": "PR-01",
        "category": "Pattern Recognition",
        "name": "Change Impact Analyzer Explanation",
        "prompt": """You are a coding assistant that strictly follows Floyd patterns.
Explain the Change Impact Analyzer pattern. When is it triggered? What are its enforcement rules?""",
        "expected_tokens": 200,
        "criteria": ["trace", "cascade", "impact", "symbols"]
    },
    {
        "id": "PR-02",
        "category": "Pattern Recognition",
        "name": "Error Resolution Engine",
        "prompt": """You are a coding assistant that strictly follows Floyd patterns.
Describe the Error Resolution Engine pattern. How does it handle build failures?""",
        "expected_tokens": 200,
        "criteria": ["parse", "root cause", "cascade", "diagnostic"]
    },
    {
        "id": "PR-03",
        "category": "Pattern Recognition",
        "name": "Pre-Edit Intelligence",
        "prompt": """You are a coding assistant that strictly follows Floyd patterns.
Explain Pre-Edit Intelligence. Why is it critical before refactoring?""",
        "expected_tokens": 200,
        "criteria": ["dependency tree", "blast radius", "safe order", "checkpoint"]
    },
    
    # ===== Code Generation =====
    {
        "id": "CG-01",
        "category": "Code Generation",
        "name": "Tarjan's Algorithm",
        "prompt": """Write a Python function that implements Tarjan's algorithm for finding strongly connected components in a directed graph. Include type hints and docstrings.""",
        "expected_tokens": 300,
        "criteria": ["def ", "stack", "index", "lowlink", "SCC"]
    },
    {
        "id": "CG-02",
        "category": "Code Generation",
        "name": "Dependency Graph Builder",
        "prompt": """Write a Python function that builds a dependency graph from a list of import statements. Return an adjacency list representation.""",
        "expected_tokens": 250,
        "criteria": ["dict", "import", "graph", "adjacency"]
    },
    {
        "id": "CG-03",
        "category": "Code Generation",
        "name": "Error Parser",
        "prompt": """Write a Python class that parses compiler error output and extracts error messages, line numbers, and file paths. Use regex.""",
        "expected_tokens": 250,
        "criteria": ["class ", "regex", "compile", "error"]
    },
    
    # ===== Refactoring Tasks =====
    {
        "id": "RF-01",
        "category": "Refactoring",
        "name": "Safe Rename Analysis",
        "prompt": """You are implementing a refactoring operation. A function 'calculateTotalPrice' in 'pricing.ts' needs to be renamed to 'computeOrderTotal'.

Following Floyd's Pre-Edit Intelligence pattern:
1. What files would you need to analyze first?
2. What would be the blast radius of this change?
3. In what order would you update the files?""",
        "expected_tokens": 300,
        "criteria": ["grep", "import", "usage", "order", "definition"]
    },
    {
        "id": "RF-02",
        "category": "Refactoring",
        "name": "Hub File Protection",
        "prompt": """You need to modify a file that is imported by 20 other files (a hub file).
Following Floyd's Architectural Guardian pattern:
1. What analysis steps are mandatory?
2. How do you calculate blast radius?
3. What checkpoint should you create before editing?""",
        "expected_tokens": 300,
        "criteria": ["importers", "blast radius", "checkpoint", "architectural"]
    },
    
    # ===== Error Diagnosis =====
    {
        "id": "ED-01",
        "category": "Error Diagnosis",
        "name": "TypeScript Error Analysis",
        "prompt": """You see this TypeScript error:
TS2322: Type 'string | undefined' is not assignable to type 'string'.

Following Floyd's Error Resolution Engine pattern, how do you diagnose and fix this?""",
        "expected_tokens": 250,
        "criteria": ["root cause", "null check", "type assertion", "cascade"]
    },
    {
        "id": "ED-02",
        "category": "Error Diagnosis",
        "name": "Circular Dependency Detection",
        "prompt": """You suspect circular dependencies in your import graph.
Following Floyd's Dependency Health Check pattern:
1. How do you detect circular dependencies?
2. How do you identify the weakest edge to break?
3. What algorithm do you use?""",
        "expected_tokens": 250,
        "criteria": ["cycle", "Tarjan", "SCC", "graph", "break"]
    },
    
    # ===== Quality Gates =====
    {
        "id": "QG-01",
        "category": "Quality Gates",
        "name": "Completion Fortress",
        "prompt": """You are about to mark a task as complete.
Following Floyd's Completion Fortress pattern, what five quality gates must pass before marking done?""",
        "expected_tokens": 300,
        "criteria": ["correctness", "security", "performance", "maintainability", "coverage"]
    },
    {
        "id": "QG-02",
        "category": "Quality Gates",
        "name": "Schema Change Safety",
        "prompt": """You need to modify a database schema.
Following Floyd's Schema Fortress pattern, what four layers of validation are required?""",
        "expected_tokens": 250,
        "criteria": ["migration safety", "API contract", "type propagation", "semantic"]
    },
]


def run_benchmark(model_name: str, max_tokens: int = 400) -> dict:
    """Run all benchmark tests."""
    
    print("=" * 70)
    print(f"BENCHMARK: {model_name}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Load model
    print(f"\nLoading model...")
    start_load = time.time()
    model, tokenizer = load(model_name)
    load_time = time.time() - start_load
    print(f"Load time: {load_time:.1f}s\n")
    
    results = {
        "model": model_name,
        "load_time": load_time,
        "tests": [],
        "started_at": datetime.now().isoformat()
    }
    
    total_time = 0
    all_tokens = 0
    
    for test in BENCHMARK_TESTS:
        test_id = test["id"]
        category = test["category"]
        name = test["name"]
        prompt = test["prompt"]
        criteria = test["criteria"]
        
        print(f"[{test_id}] {name}")
        print(f"  Category: {category}")
        
        # Run inference
        start = time.time()
        response = generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens)
        elapsed = time.time() - start
        
        tokens = len(tokenizer.encode(response))
        tps = tokens / elapsed if elapsed > 0 else 0
        total_time += elapsed
        all_tokens += tokens
        
        # Check criteria
        response_lower = response.lower()
        criteria_met = sum(1 for c in criteria if c.lower() in response_lower)
        criteria_total = len(criteria)
        criteria_pct = (criteria_met / criteria_total * 100) if criteria_total > 0 else 0
        
        print(f"  Time: {elapsed:.2f}s | Tokens: {tokens} | Speed: {tps:.1f} tok/s")
        print(f"  Criteria: {criteria_met}/{criteria_total} ({criteria_pct:.0f}%)")
        print(f"  Response: {response[:100]}...")
        print()
        
        results["tests"].append({
            "id": test_id,
            "category": category,
            "name": name,
            "tokens": tokens,
            "time": elapsed,
            "tps": tps,
            "criteria_met": criteria_met,
            "criteria_total": criteria_total,
            "criteria_pct": criteria_pct,
            "response_preview": response[:200]
        })
    
    # Summary
    results["completed_at"] = datetime.now().isoformat()
    results["total_time"] = total_time
    results["total_tokens"] = all_tokens
    results["avg_tps"] = all_tokens / total_time if total_time > 0 else 0
    
    # Category summaries
    by_category = {}
    for test in results["tests"]:
        cat = test["category"]
        if cat not in by_category:
            by_category[cat] = {"tests": [], "avg_criteria_pct": 0}
        by_category[cat]["tests"].append(test)
    
    for cat, data in by_category.items():
        avg = sum(t["criteria_pct"] for t in data["tests"]) / len(data["tests"])
        data["avg_criteria_pct"] = avg
    
    results["by_category"] = by_category
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total time: {total_time:.1f}s")
    print(f"Total tokens: {all_tokens}")
    print(f"Average speed: {results['avg_tps']:.1f} tok/s")
    print()
    
    for cat, data in by_category.items():
        print(f"{cat}:")
        print(f"  Avg criteria match: {data['avg_criteria_pct']:.1f}%")
        for test in data["tests"]:
            print(f"    {test['id']}: {test['criteria_pct']:.0f}%")
    print()
    
    return results


def save_results(results: dict, output_path: str):
    """Save benchmark results to file."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    model = sys.argv[1] if len(sys.argv) > 1 else "mlx-community/Qwen3-8B-4bit"
    
    results = run_benchmark(model)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"results/{model.split('/')[-1]}_{timestamp}.json"
    save_results(results, output_path)
