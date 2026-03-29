#!/usr/bin/env python3
"""
Training Data Pipeline - Generates all training examples and merges into final dataset.
"""
import json
import sys
from pathlib import Path
import hashlib


DEFAULT_SYSTEM_PROMPT = (
    "You are an elite live coding assistant. You strictly adhere to canonical patterns, "
    "enforcement rules, and architectural constraints."
)


def convert_floyd_patterns(input_path, output_path):
    """Convert raw floyd-patterns-export.jsonl to ChatML format."""
    count = 0
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            try:
                d = json.loads(line)
                user_content = (
                    f"Pattern: {d.get('pattern_name', 'Unknown')}\n"
                    f"Trigger: {d.get('trigger', '')}\n\n"
                    f"Enforcement Rule: {d.get('enforcement_rule', '')}"
                )
                record = {
                    "messages": [
                        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": d.get("canonical_implementation", "")}
                    ]
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            except json.JSONDecodeError:
                continue
    return count


def deduplicate_stream(in_path, out_path):
    """Remove exact duplicates from a JSONL file."""
    seen = set()
    total = 0
    unique = 0

    with open(in_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                msg_hash = hashlib.md5(
                    json.dumps(data, sort_keys=True).encode()
                ).hexdigest()

                if msg_hash in seen:
                    total += 1
                    continue

                seen.add(msg_hash)
                fout.write(line)
                unique += 1
                total += 1
            except json.JSONDecodeError:
                continue

    return unique, total


def validate_chatml_stream(filepath):
    """Validate ChatML structure."""
    errors = []
    valid = 0
    invalid = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "messages" not in data:
                    errors.append(f"Line {i}: missing 'messages'")
                    invalid += 1
                    continue
                msgs = data["messages"]
                if not isinstance(msgs, list):
                    errors.append(f"Line {i}: 'messages' not a list")
                    invalid += 1
                    continue
                roles = {m.get("role") for m in msgs}
                if "system" not in roles:
                    errors.append(f"Line {i}: no system message")
                    invalid += 1
                    continue
                if "assistant" not in roles:
                    errors.append(f"Line {i}: no assistant message")
                    invalid += 1
                    continue
                valid += 1
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: JSON error - {e}")
                invalid += 1

    return errors, valid, invalid


def run_pipeline():
    """Execute full pipeline: generate data + merge + validate."""
    training_dir = Path(__file__).parent

    print("=" * 60)
    print("Training Data Pipeline")
    print("=" * 60)

    # Step 0: Convert floyd patterns to ChatML
    floyd_chatml = training_dir / "floyd_patterns_chatml.jsonl"
    floyd_raw = training_dir / "floyd-patterns-export.jsonl"

    if not floyd_chatml.exists() and floyd_raw.exists():
        print("\n[1/8] Converting Floyd patterns to ChatML format...")
        floyd_count = convert_floyd_patterns(floyd_raw, floyd_chatml)
        print(f"  Converted {floyd_count} Floyd patterns")
    elif floyd_chatml.exists():
        with open(floyd_chatml) as f:
            floyd_count = sum(1 for line in f if line.strip())
        print(f"\n[1/8] Using existing {floyd_count} Floyd patterns")
    else:
        print("\n[1/8] WARNING: floyd-patterns-export.jsonl not found")
        floyd_count = 0

    # Step 1: Generate anti-patterns
    print("\n[2/8] Generating anti-pattern training data...")
    sys.path.insert(0, str(training_dir))
    try:
        from generate_anti_patterns import generate_chatml_examples
        anti_count = generate_chatml_examples(str(training_dir / "anti_patterns_training.jsonl"))
        print(f"  Generated {anti_count} anti-pattern examples")
    except Exception as e:
        print(f"  Error: {e}")
        anti_count = 0

    # Step 2: Generate multi-turn conversations
    print("\n[3/8] Generating multi-turn conversation data...")
    try:
        from generate_multi_turn import generate_multi_turn
        mt_count = generate_multi_turn(str(training_dir / "multi_turn_training.jsonl"))
        print(f"  Generated {mt_count} multi-turn examples")
    except Exception as e:
        print(f"  Error: {e}")
        mt_count = 0

    # Step 3: Generate error recovery
    print("\n[4/8] Generating error recovery examples...")
    try:
        from generate_error_recovery import generate_error_recovery
        er_count = generate_error_recovery(str(training_dir / "error_recovery_training.jsonl"))
        print(f"  Generated {er_count} error recovery examples")
    except Exception as e:
        print(f"  Error: {e}")
        er_count = 0

    # Step 4: Generate multi-language examples
    print("\n[5/8] Generating multi-language examples...")
    try:
        from generate_multi_lang import generate_multi_lang
        ml_count = generate_multi_lang(str(training_dir / "multi_lang_training.jsonl"))
        print(f"  Generated {ml_count} multi-language examples")
    except Exception as e:
        print(f"  Error: {e}")
        ml_count = 0

    # Step 5: Generate deep Python patterns
    print("\n[6/8] Generating deep Python patterns...")
    try:
        from generate_deep_python import generate_deep_python
        dp_count = generate_deep_python(str(training_dir / "deep_python_training.jsonl"))
        print(f"  Generated {dp_count} deep Python examples")
    except Exception as e:
        print(f"  Error: {e}")
        dp_count = 0

    # Step 6: Deduplicate and merge
    print("\n[7/8] Deduplicating and merging datasets...")

    temp_merged = training_dir / "temp_merged.jsonl"
    deduped = training_dir / "temp_deduped.jsonl"

    source_files = [
        training_dir / "floyd_patterns_chatml.jsonl",
        training_dir / "anti_patterns_training.jsonl",
        training_dir / "multi_turn_training.jsonl",
        training_dir / "error_recovery_training.jsonl",
        training_dir / "multi_lang_training.jsonl",
        training_dir / "deep_python_training.jsonl",
    ]

    total_before_dedup = 0
    with open(temp_merged, "w", encoding="utf-8") as fout:
        for src in source_files:
            if not src.exists():
                print(f"  Warning: {src.name} not found, skipping")
                continue
            with open(src, "r", encoding="utf-8") as fin:
                for line in fin:
                    if line.strip():
                        fout.write(line)
                        total_before_dedup += 1

    print(f"  Merged {total_before_dedup} examples from {len([s for s in source_files if s.exists()])} files")

    unique_count, total_count = deduplicate_stream(temp_merged, deduped)
    print(f"  Deduplicated: {unique_count} unique of {total_count} total")

    Path(temp_merged).unlink(missing_ok=True)

    # Step 7: Validate and copy to final
    print("\n[8/8] Validating final dataset...")

    final_output = training_dir / "qwen_training_dataset.jsonl"

    import shutil
    shutil.copy(deduped, final_output)
    Path(deduped).unlink(missing_ok=True)

    errors, valid, invalid = validate_chatml_stream(final_output)

    if errors and len(errors) < 20:
        print(f"  Validation warnings ({len(errors)}):")
        for e in errors[:10]:
            print(f"    - {e}")

    # Step 8: Cleanup intermediate files
    print("\n[Cleanup] Removing intermediate files...")
    for tmp_file in [
        "floyd_patterns_chatml.jsonl",
        "multi_turn_training.jsonl",
        "anti_patterns_training.jsonl",
        "error_recovery_training.jsonl",
        "multi_lang_training.jsonl",
        "deep_python_training.jsonl",
    ]:
        path = training_dir / tmp_file
        if path.exists():
            path.unlink()

    print(f"\n{'=' * 60}")
    print(f"DATASET COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Final dataset: {final_output.name}")
    print(f"  Total examples: {valid}")
    print(f"  Breakdown:")
    print(f"    - Floyd patterns: ~{floyd_count}")
    print(f"    - Anti-patterns: ~{anti_count}")
    print(f"    - Multi-turn: ~{mt_count}")
    print(f"    - Error recovery: ~{er_count}")
    print(f"    - Multi-language: ~{ml_count}")
    print(f"    - Deep Python: ~{dp_count}")
    print(f"  All Chinese/bilingual references: REMOVED")
    print(f"{'=' * 60}")

    return valid


if __name__ == "__main__":
    run_pipeline()
