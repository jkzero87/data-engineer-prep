#!/usr/bin/env python3
"""
queue_runner.py — Harness batch mode v1
Reads tasks from a text file (one per line), runs each through the
worker/supervisor cycle in agent_v2.run_task(), prints a live progress
line per task, and ends with a summary table.

Usage:
    python3 queue_runner.py tasks.txt
"""

import sys
import time

# THE KEY CONCEPT: import. agent_v2.py must be in the same folder.
# We reuse its run_task() without copying any code — agent_v2 is now
# a library, and this file is its first client.
from agent_v2 import run_task


def load_tasks(path: str) -> list[str]:
    """One task per line; blank lines and lines starting with # ignored."""
    tasks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                tasks.append(line)
    return tasks


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 queue_runner.py tasks.txt")
        sys.exit(1)

    tasks = load_tasks(sys.argv[1])
    print(f"Loaded {len(tasks)} tasks from {sys.argv[1]}\n")

    results = []
    t_batch = time.time()

    for i, task in enumerate(tasks, start=1):
        t0 = time.time()
        result = run_task(task)
        elapsed = time.time() - t0

        attempts = len(result["attempts"])
        status = result["status"]
        results.append((task, status, attempts, elapsed))

        # Live progress: one line per task, truncated for readability.
        short = task if len(task) <= 60 else task[:57] + "..."
        print(f"[{i}/{len(tasks)}] {status:15} "
              f"attempts={attempts} {elapsed:6.1f}s  {short}")

    total = time.time() - t_batch

    # Summary
    accepted = sum(1 for _, s, _, _ in results if s == "ACCEPTED")
    rejected = len(results) - accepted
    retried = sum(1 for _, _, a, _ in results if a > 1)

    print(f"\n{'=' * 60}")
    print(f"BATCH DONE: {len(results)} tasks in {total:.1f}s "
          f"({total / max(len(results), 1):.1f}s/task avg)")
    print(f"  ACCEPTED: {accepted}")
    print(f"  REJECTED: {rejected}")
    print(f"  needed retry: {retried}")

    if rejected:
        print("\nRejected tasks (check harness_log.jsonl for details):")
        for task, s, _, _ in results:
            if s != "ACCEPTED":
                print(f"  - {task[:70]}")


if __name__ == "__main__":
    main()
