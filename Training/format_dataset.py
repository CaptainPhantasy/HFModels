#!/usr/bin/env python3
"""
Format raw pattern files into ChatML training format.
Handles both 3-turn single examples and multi-turn conversations.
"""
import json
from pathlib import Path


def format_to_chatml(input_filepath, output_filepath, system_prompt=None):
    """Transform a JSONL of patterns to ChatML format.

    Supports two input formats:
    1. Single-turn (3 messages): { pattern_name, trigger, enforcement_rule, canonical_implementation }
    2. Multi-turn (already has messages[]): { messages: [...] }
    """
    default_system = system_prompt or (
        "You are an elite live coding assistant. You strictly adhere to "
        "canonical patterns, enforcement rules, and architectural constraints."
    )

    processed = 0
    skipped = 0

    with open(input_filepath, "r", encoding="utf-8") as infile, \
         open(output_filepath, "w", encoding="utf-8") as outfile:

        for line in infile:
            if not line.strip():
                continue

            try:
                data = json.loads(line)

                # Multi-turn format already has messages
                if "messages" in data:
                    # Validate message structure
                    messages = data["messages"]
                    if not isinstance(messages, list) or len(messages) < 2:
                        print(f"Skipped invalid multi-turn (need >=2 messages): {line[:80]}")
                        skipped += 1
                        continue

                    # Ensure system message at start
                    if messages[0].get("role") != "system":
                        messages = [{"role": "system", "content": default_system}] + messages

                    record = {"messages": messages}
                    outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                    processed += 1
                    continue

                # Single-turn format: build from pattern fields
                if not all(k in data for k in ("pattern_name", "trigger", "enforcement_rule", "canonical_implementation")):
                    print(f"Skipped malformed record (missing fields): {line[:80]}")
                    skipped += 1
                    continue

                # Build user content
                user_content = (
                    f"Pattern: {data['pattern_name']}\n"
                    f"Trigger: {data['trigger']}\n\n"
                    f"Enforcement Rule: {data['enforcement_rule']}"
                )

                # Add negative example if present
                if "negative_example" in data:
                    user_content += (
                        f"\n\nNegative Example (NEVER do this):\n{data.get('negative_example')}"
                    )

                # Add consequences if present
                if "consequences" in data:
                    user_content += f"\n\nConsequences: {data.get('consequences')}"

                record = {
                    "messages": [
                        {"role": "system", "content": default_system},
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": data["canonical_implementation"]}
                    ]
                }

                outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                processed += 1

            except json.JSONDecodeError:
                print(f"Skipped invalid JSON line")
                skipped += 1

    print(f"Processed {processed} records ({skipped} skipped)")
    return processed


def validate_chatml(filepath):
    """Validate ChatML format. Returns list of errors."""
    errors = []
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "messages" not in data:
                    errors.append(f"Line {i}: missing 'messages' key")
                    continue
                msgs = data["messages"]
                if not isinstance(msgs, list):
                    errors.append(f"Line {i}: 'messages' must be a list")
                    continue
                roles = [m.get("role") for m in msgs]
                if "system" not in roles:
                    errors.append(f"Line {i}: no system message")
                if "assistant" not in roles:
                    errors.append(f"Line {i}: no assistant message")
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: invalid JSON - {e}")
    return errors


def merge_datasets(filepaths, output_path):
    """Merge multiple JSONL files into one training dataset."""
    total = 0
    duplicates = 0
    seen = set()

    with open(output_path, "w", encoding="utf-8") as outfile:
        for filepath in filepaths:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: {filepath} not found, skipping")
                continue

            with open(path, "r", encoding="utf-8") as infile:
                for line in infile:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "messages" not in data:
                            continue

                        # Deduplicate by content hash
                        content_hash = hash(json.dumps(data["messages"], sort_keys=True))
                        if content_hash in seen:
                            duplicates += 1
                            continue
                        seen.add(content_hash)

                        outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
                        total += 1
                    except json.JSONDecodeError:
                        continue

    print(f"Merged {total} unique examples ({duplicates} duplicates removed)")
    return total


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Format patterns to ChatML")
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("output", help="Output JSONL file")
    parser.add_argument("--system-prompt", help="Custom system prompt")
    args = parser.parse_args()

    count = format_to_chatml(args.input, args.output, args.system_prompt)
    print(f"Saved to: {args.output}")
