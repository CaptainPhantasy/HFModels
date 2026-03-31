#!/usr/bin/env python3
"""
Benchmark script for Floyd SLM models.
Tests base vs fine-tuned models on coding tasks.
"""

import json
import time
import os
from datetime import datetime

# Floyd pattern test prompts
TEST_PROMPTS = [
    {
        "id": "pattern_recognition",
        "prompt": "Write a function that checks if a string contains only unique characters.",
        "expected": "Should use set() or similar for O(n) solution"
    },
    {
        "id": "itertools_usage", 
        "prompt": "Implement a function to flatten nested lists using itertools.chain.from_iterable.",
        "expected": "Should use itertools.chain.from_iterable"
    },
    {
        "id": "memory_efficiency",
        "prompt": "Create a class with __slots__ for memory efficiency.",
        "expected": "Should define __slots__ tuple"
    },
    {
        "id": "type_hints",
        "prompt": "Write a type-safe function that adds two numbers and returns the result.",
        "expected": "Should have type hints (int, float)"
    },
    {
        "id": "error_handling",
        "prompt": "Write a function that reads a file and handles FileNotFoundError gracefully.",
        "expected": "Should have try/except block"
    },
]


def benchmark_mlx(prompts, model_path="mlx-community/Qwen3-8B-4bit"):
    """Benchmark using MLX local inference."""
    from mlx_lm import load, generate
    
    print(f"\n=== MLX Benchmark ({model_path}) ===\n")
    
    results = []
    
    try:
        from mlx_lm import load, generate
        model, tokenizer = load(model_path)
        
        for test in prompts:
            print(f"Test: {test['id']}")
            print(f"Prompt: {test['prompt']}")
            
            start = time.time()
            response = generate(model, tokenizer, prompt=test['prompt'], max_tokens=400)
            elapsed = time.time() - start
            
            # Check for expected patterns
            expected = test['expected'].lower()
            has_expected = expected in response.lower()
            
            result = {
                "test_id": test['id'],
                "prompt": test['prompt'],
                "response": response,
                "elapsed_seconds": elapsed,
                "has_expected_pattern": has_expected,
                "model": model_path
            }
            results.append(result)
            
            print(f"  Time: {elapsed:.2f}s")
            print(f"  Has expected: {has_expected}")
            print()
            
    except Exception as e:
        print(f"MLX Error: {e}")
        return None
    
    return results


def benchmark_together(prompts, model_id, api_key):
    """Benchmark using Together AI inference endpoint."""
    from together import Together
    
    print(f"\n=== Together AI Benchmark ({model_id}) ===\n")
    
    client = Together(api_key=api_key)
    results = []
    
    for test in prompts:
        print(f"Test: {test['id']}")
        print(f"Prompt: {test['prompt']}")
        
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a Python expert. Write concise, idiomatic code."},
                    {"role": "user", "content": test['prompt']}
                ],
                max_tokens=400,
                temperature=0.3
            )
            elapsed = time.time() - start
            
            content = response.choices[0].message.content
            
            # Check for expected patterns
            expected = test['expected'].lower()
            has_expected = expected in content.lower()
            
            result = {
                "test_id": test['id'],
                "prompt": test['prompt'],
                "response": content,
                "elapsed_seconds": elapsed,
                "has_expected_pattern": has_expected,
                "model": model_id
            }
            results.append(result)
            
            print(f"  Time: {elapsed:.2f}s")
            print(f"  Has expected: {has_expected}")
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
    
    return results


def save_results(results, filename_prefix):
    """Save benchmark results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/Volumes/SanDisk1Tb/HFModels/Benchmarks/results/{filename_prefix}_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Summary stats
    summary = {
        "timestamp": timestamp,
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.get('has_expected_pattern')),
        "failed": sum(1 for r in results if not r.get('has_expected_pattern')),
        "avg_time": sum(r.get('elapsed_seconds', 0) for r in results) / len(results) if results else 0,
        "model": results[0].get('model') if results else 'unknown'
    }
    
    output = {
        "summary": summary,
        "results": results
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n=== Results saved to: {filename} ===")
    print(f"Pass rate: {summary['passed']}/{summary['total_tests']} ({100*summary['passed']/summary['total_tests']:.0f}%)")
    
    return filename


if __name__ == "__main__":
    API_KEY = "tgp_v1_o2vrTeqe1aGyKXCT4lpHtWi3AJkZZ3hInw3pCD8fo70"
    
    print("=== Floyd SLM Model Benchmark ===")
    print(f"Test prompts: {len(TEST_PROMPTS)}")
    
    # Option 1: Test base model with MLX
    # results = benchmark_mlx(TEST_PROMPTS, "mlx-community/Qwen3-8B-4bit")
    
    # Option 2: Test fine-tuned model with Together AI
    # results = benchmark_together(TEST_PROMPTS, "CaptainPhantasy/Qwen3.5-4B-floyd-slm-b3bd4ca4", API_KEY)
    
    # Option 3: Test base model with Together AI
    # results = benchmark_together(TEST_PROMPTS, "Qwen/Qwen3.5-4B", API_KEY)
    
    print("Uncomment the benchmark you want to run.")
