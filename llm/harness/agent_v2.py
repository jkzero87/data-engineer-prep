#!/usr/bin/env python3
"""
agent_v2.py — Harness v3
Worker/Supervisor loop over local llama-server instances.

  EXECUTOR   (Qwen3.5-4B,  port 8090): does the task, fast, thinking off
  SUPERVISOR (Qwen3.6-35B, port 8091): validates, thinking on

WHAT CHANGED IN v3 (and why — each maps to a failure we logged):

1. ROUTER (new tier 0). The 4B first classifies the task: does it need
   verifiable real-world facts? If yes, it writes a search query and we
   fetch evidence ONCE, BEFORE attempt 1. Both worker and judge see the
   same evidence. This is the "synergy" fix: agent_v1 was better because
   the answering model held the evidence — now it does again, and the
   judge only has to verify, in ONE round instead of two (~40s saved
   per attempt).

2. NUMBERED EVIDENCE + CITATIONS. Search results carry [n] and URLs;
   the worker must cite [n] after each factual claim. Forcing citation
   against numbered sources is the standard RAG anti-hallucination
   technique — a claim with no [n] to point at is a claim the model
   invented.

3. ABSTENTION. Both worker and judge may now say the evidence does not
   answer the question. New verdict INCONCLUSIVE stops the retry loop:
   when the evidence can't settle it, another retry only reshuffles
   guesses (that's what "Los Fabuleros de la Negra" was).

4. SAMPLING PARAMS PER ROLE. We were running on server defaults.
   Worker: temperature 0.2 — low temp is the community standard for
   grounded/RAG generation (fewer invented details). Judge: 0.6 /
   top_p 0.95 / top_k 20 — Qwen's recommended thinking-mode settings
   for precision tasks.

5. requests.Session for connection reuse (minor speed, good practice).

Kept from before: tier-1 mechanical check with supervisor override on
last attempt, network resilience (backoff, 503), engine-level JSONL
logging, last-verdict-wins parsing, clean-retry clause.
"""

import json
import sys
import time

import requests

EXECUTOR_URL = "http://localhost:8090/v1/chat/completions"
SUPERVISOR_URL = "http://localhost:8091/v1/chat/completions"
TIMEOUT = 180  # seconds per request; harness must never hang forever

SESSION = requests.Session()  # keep-alive: reuse TCP connections

# Sampling per role. Server defaults are tuned for chat, not for a
# grounded worker or a precise judge.
WORKER_PARAMS = {  # faithful extraction: low randomness
    "temperature": 0.2, "top_p": 0.8, "top_k": 20,
}
ROUTER_PARAMS = {  # classification: near-deterministic
    "temperature": 0.1, "top_p": 0.8, "top_k": 20,
}
JUDGE_PARAMS = {  # Qwen thinking-mode "precise" recommendation
    "temperature": 0.6, "top_p": 0.95, "top_k": 20,
}

ROUTER_PROMPT = """Classify this task. Answer in EXACTLY two lines:
FACTS: YES or NO  (YES if answering requires verifiable real-world
facts — names of people, bands, companies, products, dates, records,
statistics, current events. NO for pure formatting, extraction from
given text, math, or creative writing.)
QUERY: a good 3-6 word web search query for the task, in the task's
own language (or - if FACTS is NO)

TASK: {task}"""

WORKER_GROUNDED_PROMPT = """{task}

LIVE SEARCH RESULTS (numbered; newer and more reliable than your
training data):
{evidence}

RULES:
- Every factual claim (every name, date, number) MUST come from the
  results above and MUST be followed by its source number like [2].
- If the results do not clearly answer the question, say exactly that
  and state what they DO support. NEVER fill gaps from memory.
- Be concise. No essays, no invented detail."""

VALIDATION_PROMPT = """You are a supervisor validating a worker's output.

TASK GIVEN TO THE WORKER:
{task}

WORKER OUTPUT:
{output}

MANDATORY SEARCH RULE: if the task asks about anything "current",
"latest", "newest", "today", recent versions, prices, or events —
or if the worker's output asserts verifiable real-world facts (names
of people, bands, companies, products, dates, records, statistics) —
your training data may be wrong and you MUST NOT trust your own
knowledge. In that case respond with exactly one line:
SEARCH: <short search query>
You will receive search results and be asked again.

Otherwise, check the output against the task instructions. The FIRST
line of your final answer must be exactly one word: ACCEPT or REJECT.
If REJECT, follow with a numbered list of every error found. Be precise
and do not invent errors that are not there."""

VALIDATION_GROUNDED_PROMPT = """You are a supervisor validating a worker's output.

TASK GIVEN TO THE WORKER:
{task}

WORKER OUTPUT:
{output}

SEARCH RESULTS (the only source of truth for this validation):
{evidence}

Verify EVERY factual claim in the worker's output against these search
results, one by one:
- A claim not supported by the results is an error.
- A citation [n] pointing at a result that does not say that is an error.
- In your error list, only state corrections that literally appear in
  the results — NEVER from your own memory. Your memory may be wrong.

The FIRST line of your final answer must be exactly one word:
ACCEPT       - every claim is supported by the results
REJECT       - one or more claims are unsupported or contradicted
INCONCLUSIVE - the results themselves do not contain enough
               information to answer the task either way
If REJECT, follow with a numbered list of every error found."""


def chat(url: str, prompt: str, max_tokens: int = 1500,
         retries: int = 5, backoff_s: float = 3.0,
         params: dict | None = None) -> str:
    """One chat completion against a local llama-server. Returns text.
    Retries on network errors and 503 (server still loading), waiting
    backoff_s * attempt between tries — a linear backoff.
    `params` merges extra sampling options (temperature etc.) into the
    payload so each role can run with its own settings."""
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    if params:
        payload.update(params)
    last_err = None
    for i in range(1, retries + 1):
        try:
            r = SESSION.post(url, json=payload, timeout=TIMEOUT)
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


def parse_verdict(text: str) -> tuple[str, str]:
    """Returns (verdict, error_list_text) with verdict one of
    'ACCEPT' | 'REJECT' | 'INCONCLUSIVE'. Last verdict line wins, so
    reasoning text mentioning the keywords earlier cannot mislead.
    No clear verdict anywhere -> REJECT with full text as feedback."""
    verdict = None
    errors_start = None
    for match_line in text.splitlines():
        line_up = match_line.strip().upper()
        if line_up.startswith("ACCEPT"):
            verdict = "ACCEPT"
            errors_start = None
        elif line_up.startswith("REJECT"):
            verdict = "REJECT"
            errors_start = text.find(match_line) + len(match_line)
        elif line_up.startswith("INCONCLUSIVE"):
            verdict = "INCONCLUSIVE"
            errors_start = None
    if verdict == "ACCEPT" or verdict == "INCONCLUSIVE":
        return verdict, ""
    if verdict == "REJECT":
        return "REJECT", text[errors_start:].strip() if errors_start else ""
    return "REJECT", text


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


def search_web(query: str, max_results: int = 6) -> str:
    """Tool: DuckDuckGo search. Returns numbered results with URLs so
    the worker can cite [n] and the judge can check citations."""
    from ddgs import DDGS
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        return "\n".join(
            f"[{i}] {r['title']} — {r.get('href', '')}\n    {r['body']}"
            for i, r in enumerate(results, 1)
        )
    except Exception as e:
        return f"Search failed: {e}"


def route_task(task: str) -> tuple[bool, str]:
    """Tier 0 router: ask the FAST model whether the task needs live
    facts, and for a search query if so. Costs ~1-2s; replaces the
    brittle keyword list for factual questions. Fails safe: any parse
    problem -> (False, '') and the judge's SEARCH fallback still
    protects us."""
    try:
        reply = chat(EXECUTOR_URL, ROUTER_PROMPT.format(task=task),
                     max_tokens=60, params=ROUTER_PARAMS)
    except RuntimeError:
        return False, ""
    needs, query = False, ""
    for line in reply.splitlines():
        line_up = line.strip().upper()
        if line_up.startswith("FACTS:"):
            needs = "YES" in line_up
        elif line_up.startswith("QUERY:"):
            query = line.split(":", 1)[1].strip()
    if query in ("-", ""):
        query = task
    return needs, query


def run_task(task: str, max_retries: int = 1) -> dict:
    """Full worker->supervisor cycle with retry. Returns a result record."""
    record = {"task": task, "attempts": []}

    # Tier 0: decide once whether this task needs live evidence.
    # Keyword hits force YES (cheap, zero false negatives on freshness);
    # otherwise the router classifies. Evidence is fetched ONE time and
    # shared by worker (grounded prompt) and judge (grounded validation).
    FRESH_WORDS = ("current", "latest", "newest", "today", "this year")
    evidence = ""
    if any(w in task.lower() for w in FRESH_WORDS):
        needs_facts, query = True, task
    else:
        needs_facts, query = route_task(task)
    if needs_facts:
        print(f"  [tool] pre-search for worker+judge: {query}")
        evidence = search_web(query)
        record["search_query"] = query

    if evidence:
        prompt = WORKER_GROUNDED_PROMPT.format(task=task, evidence=evidence)
    else:
        prompt = task

    for attempt in range(1 + max_retries):
        t0 = time.time()
        output = chat(EXECUTOR_URL, prompt, params=WORKER_PARAMS)
        t_exec = time.time() - t0

        # Tier 1: mechanical validation — free, instant, structural only.
        mech_ok, mech_reason = mechanical_check(task, output)
        if not mech_ok and attempt < max_retries:
            record["attempts"].append({
                "attempt": attempt + 1,
                "output": output,
                "accepted": False,
                "verdict": "REJECT",
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

        # Tier 2: the judge. With evidence -> ONE grounded round.
        # Without evidence -> classic round, SEARCH fallback available.
        t0 = time.time()
        if evidence:
            verdict_raw = chat(
                SUPERVISOR_URL,
                VALIDATION_GROUNDED_PROMPT.format(
                    task=task, output=output, evidence=evidence),
                max_tokens=6000, params=JUDGE_PARAMS,
            )
        else:
            verdict_raw = chat(
                SUPERVISOR_URL,
                VALIDATION_PROMPT.format(task=task, output=output),
                max_tokens=4000, params=JUDGE_PARAMS,
            )
        t_sup = time.time() - t0

        if not verdict_raw:
            # Thinking likely consumed the whole token budget before the
            # final answer. Do not poison the retry with empty feedback.
            verdict_raw = "(empty supervisor response — token budget exhausted?)"
            verdict, errors = "REJECT", "Supervisor returned no verdict; retry as-is."
        elif verdict_raw.strip().upper().startswith("SEARCH:"):
            # Only reachable on the no-evidence path: the judge spotted
            # factual claims the router missed. Fetch once, keep the
            # evidence for the retry, validate grounded.
            query = verdict_raw.strip()[7:].strip()
            print(f"  [tool] supervisor requests search: {query}")
            evidence = search_web(query)
            record["search_query"] = query
            t0 = time.time()
            verdict_raw = chat(
                SUPERVISOR_URL,
                VALIDATION_GROUNDED_PROMPT.format(
                    task=task, output=output, evidence=evidence),
                max_tokens=6000, params=JUDGE_PARAMS,
            )
            t_sup += time.time() - t0
            verdict, errors = parse_verdict(verdict_raw)
        else:
            verdict, errors = parse_verdict(verdict_raw)

        record["attempts"].append({
            "attempt": attempt + 1,
            "output": output,
            "accepted": verdict == "ACCEPT",
            "verdict": verdict,
            "errors": errors,
            "verdict_raw": verdict_raw,
            "t_executor_s": round(t_exec, 2),
            "t_supervisor_s": round(t_sup, 2),
            "rejected_by": "supervisor" if verdict == "REJECT" else "",
        })

        if verdict == "ACCEPT":
            record["status"] = "ACCEPTED"
            record["final_output"] = output
            log_record(record)
            return record

        if verdict == "INCONCLUSIVE":
            # The evidence cannot settle the question. Retrying would
            # only make the worker reshuffle guesses — stop honestly.
            record["status"] = "INCONCLUSIVE"
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
        if evidence:
            prompt += (
                "\n\nLIVE SEARCH RESULTS (numbered; the only source of "
                "truth — every factual claim must come from these and "
                "cite its number like [2]):\n" + evidence
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
        print(f"VERDICT: {a.get('verdict', 'ACCEPT' if a['accepted'] else 'REJECT')}")
        if a["errors"]:
            print(f"ERRORS:\n{a['errors']}")
        if not a['accepted'] and 'verdict_raw' in a:
            print(f"SUPERVISOR RAW:\n{a['verdict_raw']}")

    print(f"\n{'=' * 60}\nSTATUS: {result['status']}")
    print(f"FINAL OUTPUT:\n{result['final_output']}")


if __name__ == "__main__":
    main()
