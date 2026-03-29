#!/usr/bin/env python3
"""
Test generator for itertools patterns - 5 examples to validate quality.
"""

import json
from pathlib import Path


def generate_test_itertools():
    """Generate 5 high-quality itertools examples."""
    
    examples = []
    
    # Example 1: itertools.chain - combining multiple iterables
    examples.append({
        "messages": [
            {
                "role": "system",
                "content": "You are a Python expert. Write idiomatic, performant Python using modern patterns."
            },
            {
                "role": "user",
                "content": "Implement a function that merges multiple sorted log files into a single chronologically sorted stream using itertools.chain."
            },
            {
                "role": "assistant",
                "content": """import itertools
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator, NamedTuple


class LogEntry(NamedTuple):
    timestamp: datetime
    level: str
    message: str

    @classmethod
    def parse(cls, line: str) -> \"LogEntry | None\":
        \"\"\"Parse '2024-03-29 10:15:30 INFO message'. Returns None on bad input.\"\"\"
        parts = line.strip().split(maxsplit=3)
        if len(parts) < 4:
            return None
        try:
            ts = datetime.strptime(f\"{parts[0]} {parts[1]}\", \"%Y-%m-%d %H:%M:%S\")
        except ValueError:
            return None
        return cls(timestamp=ts, level=parts[2], message=parts[3])


def read_log_file(path: Path) -> Iterator[LogEntry]:
    \"\"\"Yield parsed log entries, skipping malformed lines.\"\"\"
    with path.open(encoding=\"utf-8\") as f:
        for line in f:
            entry = LogEntry.parse(line)
            if entry is not None:
                yield entry


def merge_logs(*log_paths: Path) -> Iterator[LogEntry]:
    \"\"\"Merge multiple log files into chronologically sorted stream.\"\"\"
    all_entries = itertools.chain.from_iterable(
        read_log_file(path) for path in log_paths
    )
    return iter(sorted(all_entries, key=lambda e: e.timestamp))


def main() -> None:
    tmpdir = Path(tempfile.mkdtemp())
    try:
        (tmpdir / \"server.log\").write_text(
            \"2024-03-29 08:00:01 INFO Server started on port 8080\\n\"
            \"2024-03-29 09:15:00 WARN High memory usage detected\\n\"
            \"2024-03-29 10:15:01 ERROR Connection timeout to replica-3\\n\",
            encoding=\"utf-8\",
        )
        (tmpdir / \"access.log\").write_text(
            \"2024-03-29 07:45:00 INFO Health check passed\\n\"
            \"malformed line without timestamp\\n\"
            \"2024-03-29 09:00:00 INFO Backup completed successfully\\n\",
            encoding=\"utf-8\",
        )
        merged = merge_logs(*sorted(tmpdir.glob(\"*.log\")))
        for entry in merged:
            print(f\"[{entry.timestamp:%H:%M:%S}] {entry.level:5s} {entry.message}\")
    finally:
        shutil.rmtree(tmpdir)


if __name__ == \"__main__\":
    main()"""
            }
        ]
    })
    
    # Example 2: itertools.groupby - grouping consecutive elements
    examples.append({
        "messages": [
            {
                "role": "system",
                "content": "You are a Python expert. Write idiomatic, performant Python using modern patterns."
            },
            {
                "role": "user",
                "content": "Implement a function that groups consecutive HTTP status codes by category (2xx, 3xx, 4xx, 5xx) using itertools.groupby."
            },
            {
                "role": "assistant",
                "content": """import itertools
from typing import Iterator, NamedTuple


class HttpResponse(NamedTuple):
    status: int
    url: str
    duration_ms: float


def status_category(status: int) -> str:
    \"\"\"Get status code category: 2xx, 3xx, 4xx, 5xx.\"\"\"
    return f"{status // 100}xx"


def group_responses_by_status(
    responses: list[HttpResponse]
) -> dict[str, list[HttpResponse]]:
    \"\"\"Group HTTP responses by status category.\"\"\"
    # Sort by status code first (groupby requires sorted input)
    sorted_responses = sorted(responses, key=lambda r: r.status)
    
    # Group by status category
    grouped = {}
    for category, group in itertools.groupby(sorted_responses, key=lambda r: status_category(r.status)):
        grouped[category] = list(group)
    
    return grouped


def analyze_response_groups(responses: list[HttpResponse]) -> None:
    \"\"\"Analyze and report on grouped responses.\"\"\"
    groups = group_responses_by_status(responses)
    
    for category in sorted(groups.keys()):
        group = groups[category]
        avg_duration = sum(r.duration_ms for r in group) / len(group)
        print(f"{category}: {len(group)} requests, avg {avg_duration:.1f}ms")
        
        # Show first 3 URLs in each category
        for resp in group[:3]:
            print(f"  {resp.status} {resp.url} ({resp.duration_ms}ms)")


def main() -> None:
    responses = [
        HttpResponse(200, "/api/users", 45.2),
        HttpResponse(201, "/api/posts", 123.5),
        HttpResponse(200, "/api/comments", 34.1),
        HttpResponse(404, "/api/missing", 12.3),
        HttpResponse(500, "/api/error", 234.5),
        HttpResponse(503, "/api/unavailable", 5000.0),
        HttpResponse(301, "/old-page", 15.2),
    ]
    
    analyze_response_groups(responses)


if __name__ == "__main__":
    main()"""
            }
        ]
    })
    
    # Example 3: itertools.combinations - generating combinations
    examples.append({
        "messages": [
            {
                "role": "system",
                "content": "You are a Python expert. Write idiomatic, performant Python using modern patterns."
            },
            {
                "role": "user",
                "content": "Implement a function that finds all pairs of numbers in a list that sum to a target value using itertools.combinations."
            },
            {
                "role": "assistant",
                "content": """import itertools
from typing import Iterator


def find_pairs_with_sum(numbers: list[int], target: int) -> Iterator[tuple[int, int]]:
    \"\"\"Find all pairs of numbers that sum to target value.
    
    Args:
        numbers: List of integers
        target: Target sum value
        
    Yields:
        Tuples of (a, b) where a + b == target
    \"\"\"
    for a, b in itertools.combinations(numbers, 2):
        if a + b == target:
            yield (a, b)


def find_triplets_with_sum(numbers: list[int], target: int) -> Iterator[tuple[int, int, int]]:
    \"\"\"Find all triplets of numbers that sum to target value.\"\"\"
    for a, b, c in itertools.combinations(numbers, 3):
        if a + b + c == target:
            yield (a, b, c)


def analyze_combinations(numbers: list[int]) -> None:
    \"\"\"Analyze various combination patterns in a list.\"\"\"
    print(f"Analyzing {len(numbers)} numbers: {numbers}")
    print()
    
    # Find pairs that sum to 10
    pairs = list(find_pairs_with_sum(numbers, 10))
    print(f"Pairs summing to 10: {pairs}")
    
    # Find triplets that sum to 15
    triplets = list(find_triplets_with_sum(numbers, 15))
    print(f"Triplets summing to 15: {triplets}")
    
    # Count all possible pairs
    total_pairs = sum(1 for _ in itertools.combinations(numbers, 2))
    print(f"Total possible pairs: {total_pairs}")
    
    # Count all possible triplets
    total_triplets = sum(1 for _ in itertools.combinations(numbers, 3))
    print(f"Total possible triplets: {total_triplets}")


def main() -> None:
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    analyze_combinations(numbers)


if __name__ == "__main__":
    main()"""
            }
        ]
    })
    
    # Example 4: itertools.product - Cartesian product
    examples.append({
        "messages": [
            {
                "role": "system",
                "content": "You are a Python expert. Write idiomatic, performant Python using modern patterns."
            },
            {
                "role": "user",
                "content": "Implement a configuration matrix generator that creates all possible combinations of deployment settings using itertools.product."
            },
            {
                "role": "assistant",
                "content": """import itertools
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class DeploymentConfig:
    \"\"\"Immutable deployment configuration.\"\"\"
    environment: str
    region: str
    instance_type: str
    replicas: int

def generate_deployment_matrix(
    environments: list[str],
    regions: list[str],
    instance_types: list[str],
    replica_counts: list[int],
) -> Iterator[DeploymentConfig]:
    \"\"\"Generate all possible deployment configurations.
    
    Uses itertools.product to create Cartesian product of all options.
    \"\"\"
    for env, region, instance, replicas in itertools.product(
        environments, regions, instance_types, replica_counts
    ):
        yield DeploymentConfig(
            environment=env,
            region=region,
            instance_type=instance,
            replicas=replicas,
        )


def filter_valid_configs(configs: Iterator[DeploymentConfig]) -> Iterator[DeploymentConfig]:
    \"\"\"Filter out invalid configuration combinations.\"\"\"
    for config in configs:
        # Production must have at least 3 replicas
        if config.environment == "production" and config.replicas < 3:
            continue
        
        # Large instances only in production
        if config.instance_type == "c5.4xlarge" and config.environment != "production":
            continue
        
        yield config


def main() -> None:
    environments = ["development", "staging", "production"]
    regions = ["us-east-1", "us-west-2", "eu-west-1"]
    instance_types = ["t3.small", "t3.medium", "c5.4xlarge"]
    replica_counts = [1, 2, 3, 5]
    
    # Generate all possible configurations
    all_configs = generate_deployment_matrix(
        environments, regions, instance_types, replica_counts
    )
    
    # Filter to valid configurations only
    valid_configs = list(filter_valid_configs(all_configs))
    
    print(f"Generated {len(valid_configs)} valid deployment configurations")
    print()
    
    # Show production configs
    prod_configs = [c for c in valid_configs if c.environment == "production"]
    print(f"Production configurations ({len(prod_configs)}):")
    for config in prod_configs[:5]:
        print(f"  {config}")


if __name__ == "__main__":
    main()"""
            }
        ]
    })
    
    # Example 5: itertools.accumulate - running totals
    examples.append({
        "messages": [
            {
                "role": "system",
                "content": "You are a Python expert. Write idiomatic, performant Python using modern patterns."
            },
            {
                "role": "user",
                "content": "Implement a financial transaction analyzer that calculates running balances and cumulative statistics using itertools.accumulate."
            },
            {
                "role": "assistant",
                "content": """import itertools
import operator
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator


@dataclass
class Transaction:
    \"\"\"Financial transaction record.\"\"\"
    timestamp: datetime
    amount: float
    description: str
    
    def __repr__(self) -> str:
        sign = "+" if self.amount >= 0 else ""
        return f"{self.timestamp.strftime('%Y-%m-%d')} {sign}{self.amount:>8.2f} {self.description}"


def calculate_running_balance(
    transactions: list[Transaction],
    initial_balance: float = 0.0
) -> Iterator[tuple[Transaction, float]]:
    \"\"\"Calculate running balance after each transaction.
    
    Uses itertools.accumulate to maintain cumulative sum.
    \"\"\"
    amounts = [initial_balance] + [t.amount for t in transactions]
    balances = itertools.accumulate(amounts, operator.add)
    
    # Skip initial balance, pair transactions with their resulting balance
    next(balances)  # Skip initial
    return zip(transactions, balances)


def analyze_cash_flow(transactions: list[Transaction]) -> None:
    \"\"\"Analyze cash flow patterns with running statistics.\"\"\"
    print("Transaction History with Running Balance:")
    print("-" * 70)
    
    initial = 1000.0
    print(f"Initial Balance: ${initial:>8.2f}")
    print()
    
    for txn, balance in calculate_running_balance(transactions, initial):
        print(f"{txn} | Balance: ${balance:>8.2f}")
    
    print()
    
    # Calculate cumulative deposits and withdrawals separately
    deposits = [t.amount for t in transactions if t.amount > 0]
    withdrawals = [abs(t.amount) for t in transactions if t.amount < 0]
    
    cumulative_deposits = list(itertools.accumulate(deposits, operator.add))
    cumulative_withdrawals = list(itertools.accumulate(withdrawals, operator.add))
    
    print(f"Total Deposits: ${cumulative_deposits[-1] if cumulative_deposits else 0:.2f}")
    print(f"Total Withdrawals: ${cumulative_withdrawals[-1] if cumulative_withdrawals else 0:.2f}")
    
    # Peak balance: O(n) via accumulate instead of O(n^2) nested sum
    all_balances = list(itertools.accumulate(
        [initial] + [t.amount for t in transactions], operator.add
    ))
    # accumulate with max tracks the running high-water mark over time
    running_peak = list(itertools.accumulate(all_balances, max))
    print(f"Peak Balance: ${running_peak[-1]:.2f}")
    print(f"High-water mark per step: {['${:.0f}'.format(b) for b in running_peak]}")


def main() -> None:
    transactions = [
        Transaction(datetime(2024, 3, 1), 500.0, "Salary deposit"),
        Transaction(datetime(2024, 3, 5), -50.0, "Grocery shopping"),
        Transaction(datetime(2024, 3, 10), -120.0, "Utility bill"),
        Transaction(datetime(2024, 3, 15), 200.0, "Freelance payment"),
        Transaction(datetime(2024, 3, 20), -75.0, "Restaurant"),
        Transaction(datetime(2024, 3, 25), -30.0, "Subscription"),
        Transaction(datetime(2024, 3, 28), 150.0, "Refund"),
    ]
    
    analyze_cash_flow(transactions)


if __name__ == "__main__":
    main()"""
            }
        ]
    })
    
    return examples


def main():
    """Generate test examples and write to JSONL."""
    output_path = Path("/Volumes/SanDisk1Tb/HFModels/PYTHON AGENT OUTPUT/test_itertools.jsonl")
    
    examples = generate_test_itertools()
    
    with output_path.open("w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")
    
    print(f"Generated {len(examples)} test examples")
    print(f"Output: {output_path}")
    print(f"File size: {output_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
