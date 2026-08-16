#!/usr/bin/env python3
"""
agent_v2.py — Harness heartbeat v1
Worker/Supervisor loop over local llama-server instances.

  EXECUTOR   (Qwen3.5-4B,  port 8090): does the task, fast, thinking off
  SUPERVISOR (Qwen3.6-35B, port 8091): validates, ACCEPT/REJECT, thinking on

Flow per task:
  1. Send task -> executor
  2. Send task + executor output -> supervisor with validation prompt
  3. Parse verdict: ACCEPT -> done | REJECT -> retry executor once with
     the supervisor's error list appended, then re-validate
"""

import json
import sys
import time

import requests

EXECUTOR_URL = "http://localhost:8090/v1/chat/completions"
SUPERVISOR_URL = "http://localhost:8091/v1/chat/completions"
TIMEOUT = 180  # seconds per request; harness must never hang forever

VALIDATION_PROMPT = """You are a supervisor validating a worker's output.

TASK GIVEN TO THE WORKER:
{task}

WORKER OUTPUT:
{output}

MANDATORY SEARCH RULE: if the task asks about anything "current",
"latest", "newest", "today", recent versions, prices, or events —
your training data is outdated for such claims and you MUST NOT trust
your own knowledge. In that case respond with exactly one line:
SEARCH: <short search query>
You will receive search results and be asked again.
The same rule applies if the worker's output asserts verifiable
real-world facts (names of people, bands, companies, products,
dates, records, statistics): you MUST issue a SEARCH before any
verdict. Never confirm or correct facts from memory alone —
your training data may be wrong.

Otherwise, check the output against the task instructions. The FIRST line
of your final answer must be exactly one word: ACCEPT or REJECT. If REJECT,
follow with a numbered list of every error found. Be precise and do not
invent errors that are not there."""


def chat(url: str, prompt: str, max_tokens: int = 1500,
         retries: int = 5, backoff_s: float = 3.0) -> str:
    """One chat completion against a local llama-server. Returns text.
    Retries on network errors and 503 (server still loading), waiting
    backoff_s * attempt between tries — a linear backoff."""
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    last_err = None
    for i in range(1, retries + 1):
        try:
            r = requests.post(url, json=payload, timeout=TIMEOUT)
            if r.status_code == 503:
                raise requests.exceptions.HTTPError("503: server loading")
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            last_err = e
            wait = backoff_s * i
            print(f"  [chat] {url} failed ({e}); retry {i}/{retries} in {wait:.0f}s")
            time.sleep(wait)
    raise RuntimeError(f"chat() gave up after {retries} tries: {last_err}")


def parse_verdict(text: str) -> tuple[bool, str]:
    """Returns (accepted, error_list_text). Last verdict line wins,
    so reasoning text mentioning the keywords earlier cannot mislead."""
    verdict = None
    errors_start = None
    for match_line in text.splitlines():
        line_up = match_line.strip().upper()
        if line_up.startswith("ACCEPT"):
            verdict = True
            errors_start = None
        elif line_up.startswith("REJECT"):
            verdict = False
            errors_start = text.find(match_line) + len(match_line)
    if verdict is True:
        return True, ""
    if verdict is False:
        return False, text[errors_start:].strip() if errors_start else ""
    # No clear verdict anywhere: reject with full text as feedback.
    return False, text

def log_record(record: dict) -> None:
    """Append one result to the harness log. Lives with the engine so
    every caller (main, queue_runner, future agents) logs for free."""
    with open("harness_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def mechanical_check(task: str, output: str) -> tuple[bool, str]:
    """Tier-1 validation: cheap structural checks in pure Python.
    Returns (passed, reason). Only judges structure, never meaning."""
    if "JSON" in task.upper():
        try:
            json.loads(output)
        except json.JSONDecodeError as e:
            return False, f"Output is not valid JSON: {e}"
    return True, ""

def search_web(query: str, max_results: int = 4) -> str:
    """Tool: DuckDuckGo search. Returns titles + snippets as plain text."""
    from ddgs import DDGS
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        return "\n".join(
            f"- {r['title']}: {r['body']}" for r in results
        )
    except Exception as e:
        return f"Search failed: {e}"

def run_task(task: str, max_retries: int = 1) -> dict:
    """Full worker->supervisor cycle with retry. Returns a result record."""
    record = {"task": task, "attempts": []}

    prompt = task
    # Tier 0: pre-search — if the task's own words demand fresh data,
    # fetch it up front so the worker never answers blind.
    FRESH_WORDS = ("current", "latest", "newest", "today", "this year")
    if any(w in task.lower() for w in FRESH_WORDS):
        results = search_web(task)
        print(f"  [tool] pre-search injected for worker")
        prompt = (
            f"{task}\n\nUse these live search results as the source of "
            f"truth (they are newer than your training data):\n{results}"
        )
    last_results = ""
    for attempt in range(1 + max_retries):
        t0 = time.time()
        output = chat(EXECUTOR_URL, prompt)
        t_exec = time.time() - t0

        # Tier 1: mechanical validation — free, instant, structural only.
        mech_ok, mech_reason = mechanical_check(task, output)
        if not mech_ok and attempt < max_retries:
            record["attempts"].append({
                "attempt": attempt + 1,
                "output": output,
                "accepted": False,
                "errors": mech_reason,
                "rejected_by": "mechanical",
                "t_executor_s": round(t_exec, 2),
                "t_supervisor_s": 0.0,
            })
            prompt = (
                f"{task}\n\nYour previous attempt was rejected with these "
                f"errors — fix ALL of them:\n{mech_reason}\n\n"
                f"Previous attempt:\n{output}"
            )
            continue  # skip the supervisor, go straight to next attempt
   
        t0 = time.time()
        verdict_raw = chat(
            SUPERVISOR_URL,
            VALIDATION_PROMPT.format(task=task, output=output),
            max_tokens=4000,
        )
        t_sup = time.time() - t0

        if not verdict_raw:
            # Thinking likely consumed the whole token budget before the
            # final answer. Do not poison the retry with empty feedback.
            verdict_raw = "(empty supervisor response — token budget exhausted?)"
            accepted, errors = False, "Supervisor returned no verdict; retry as-is."
        elif verdict_raw.strip().upper().startswith("SEARCH:"):
            query = verdict_raw.strip()[7:].strip()
            print(f"  [tool] supervisor requests search: {query}")
            results = search_web(query)
            last_results = results
            t0 = time.time()
            verdict_raw = chat(
                SUPERVISOR_URL,
                VALIDATION_PROMPT.format(task=task, output=output)
                + f"\n\nSEARCH RESULTS for '{query}':\n{results}\n\n"
                    "Verify EVERY factual claim in the worker's output against these "
                    "search results. Any claim NOT supported by the results is an error. "
                    "In your error list, only state corrections that appear in the "
                    "search results — never from your own memory. "
                    "Now give your final verdict.",
                max_tokens=4000,
            )
            t_sup += time.time() - t0
            accepted, errors = parse_verdict(verdict_raw)
        else:
            accepted, errors = parse_verdict(verdict_raw)
        record["attempts"].append({
            "attempt": attempt + 1,
            "output": output,
            "accepted": accepted,
            "errors": errors,
            "verdict_raw": verdict_raw,
            "t_executor_s": round(t_exec, 2),
            "t_supervisor_s": round(t_sup, 2),
            "rejected_by": "supervisor" if not accepted else "",
        })

        if accepted:
            record["status"] = "ACCEPTED"
            record["final_output"] = output
            log_record(record)
            return record

        # Retry: same task plus the supervisor's corrections.
        prompt = (
            f"{task}\n\nYour previous attempt was rejected with these "
            f"errors — fix ALL of them:\n{errors}\n\nPrevious attempt:\n{output}\n\n"
            f"Output ONLY the corrected final answer. Do NOT mention "
            f"previous attempts, corrections, or the review process."
        )
        if last_results:
            prompt += (
                "\n\nSEARCH RESULTS (ground truth — mention ONLY names "
                "and facts supported by these):\n" + last_results
            )

    record["status"] = "REJECTED_FINAL"
    record["final_output"] = record["attempts"][-1]["output"]
    log_record(record)
    return record


def main() -> None:
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = (
            "Extract every date from the following text. Output ONLY a JSON "
            "array of strings in YYYY-MM-DD format. Do not explain. Text: "
            "The contract was signed on March 5, 2024, after a meeting on "
            "19/02/2024 and an audit on 2023-11-30."
        )

    print(f"TASK: {task}\n{'=' * 60}")
    result = run_task(task)

    for a in result["attempts"]:
        print(f"\n--- Attempt {a['attempt']} "
              f"(executor {a['t_executor_s']}s, supervisor {a['t_supervisor_s']}s)")
        print(f"OUTPUT:\n{a['output']}")
        print(f"VERDICT: {'ACCEPT' if a['accepted'] else 'REJECT'}")
        if a["errors"]:
            print(f"ERRORS:\n{a['errors']}")
        if not a['accepted'] and 'verdict_raw' in a:
            print(f"SUPERVISOR RAW:\n{a['verdict_raw']}")

    print(f"\n{'=' * 60}\nSTATUS: {result['status']}")
    print(f"FINAL OUTPUT:\n{result['final_output']}")


if __name__ == "__main__":
    main()
