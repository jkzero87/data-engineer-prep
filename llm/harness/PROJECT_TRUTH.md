# PROJECT TRUTH — Local Dual-Agent Harness

**Path:** `/home/jkzero/data-engineer-prep/llm/harness`
**Machine:** `jkzero-A520M-DS3H`
**Evidence baseline:** `harness_evidence_20260809_1506.txt`, generated 2026-08-09T15:06:17-05:00

---

## RULES FOR THIS FILE

1. Every fact carries the **command that produced it** and the **date verified**.
2. If a claim has no command, it goes in Part II §II.4 UNVERIFIED. No exceptions.
3. Narrative from any AI agent (including Claude Code) is **not evidence**. Only raw
   command output is. An agent may propose a line for this file, but only by
   supplying the command and its output.
4. Session notes, chat memory, and recollection are **not evidence**. Several claims
   carried in notes for three weeks turned out to be false — see Part II §II.1.
5. Re-verify before trusting anything older than the baseline date above.
6. **Part I governs.** Part II is technical notes, subordinate to Part I. If a
   technical note and Part I ever conflict, Part I wins and the note needs updating.

---

# PART I — PURPOSE AND METHOD

Read this part first. It governs everything under Part II.

## I.1 THE GOAL

- The goal is NOT a web searcher. Web search was the FIRST STEP, so the agent could
  calibrate itself against reality. The goal is an AGENT THAT WORKS LOCALLY ON THIS
  MACHINE: operating on files, running real tasks, with the internet only as a
  calibration oracle.
- Architecture: 4B = hands, 35B = brain, escalate when the small one fails. Only one
  model resident at a time is ACCEPTED — the ~28s wake-up cost of the other is a
  price worth paying.
- First real job chosen as the concrete target: have the agent perform the
  shadowed-definition cleanup in research.py. Deliberately demanding — read a large
  file, count exactly, tell shadowed from chained, write without breaking anything.

## I.2 HOW WE WORK — the rules that produced every good result here

- ALWAYS TEST. When the question is "does this work?", the answer is to measure it,
  never to explain why measuring probably isn't needed.
- BRING NEW IDEAS. Try different approaches. The expected response to a limitation
  is a SOLUTION, not acceptance of the limit.
- Do not centre the work on the limitations of the CURRENT design. Centre it on the
  technical actions needed to reach the goal. The only legitimate limit is a REAL
  hardware limit, PROVEN by measurement. Inherited "can't do that" items are old
  decisions, not laws — every one examined so far (read_file's 4000-char cap, 8192
  context, the coexistence VRAM numbers) turned out to be a July choice, not physics.
- MECHANICAL VERIFICATION OUTRANKS MODEL JUDGMENT. `grep -n` counts and locates;
  models interpret what the count means. Proven twice: both models fabricated line
  numbers on 2026-08-10, and eval.py's json_equals caught a malformed array the 35B
  judge had approved.
- AGENT NARRATION IS NOT EVIDENCE. Every claim in this file carries the command that
  produced it, with a date. Verify the port answers, the timestamp is current, and
  the directory is right BEFORE believing any output.
- ONE CHANGE AT A TIME, each backed up, each gated by the suite, and read the actual
  diff before committing.
- WEB-TASK failures need a targeted re-run before being called a regression;
  MECHANICAL failures are deterministic and count on the first observation.

## I.3 WHY THESE RULES EXIST — two documented cases, 2026-08-10

- The assistant twice asserted a limitation instead of testing it, and was wrong both
  times. The 4B's supposed context limit did not exist. And when the user insisted on
  testing the 35B on a task the 4B had failed, the 35B was right — and the test
  exposed a counting error the assistant had been repeating for hours (see the
  `result_score` correction, Part II §II.1).
- Keep these here. They are the reason Part I comes before Part II.

## I.4 CURRENT STATE IN ONE PARAGRAPH

Stack works when started manually (`jkhelper`); nothing autostarts (SearXNG,
`harness-executor`, `harness-supervisor` all need a manual bring-up). eval.py suite
holds at 9–10/10 on healthy search engines, with 1–2 web tasks wobbling per run — a
known noise floor, not a regression signal. Two real bugs found and fixed today
(2026-08-10): a 20+ minute stall on Retry-After (fixed, committed `b8c6b4e`) and
Wikipedia-first candidate injection to floor evidence quality when engines degrade
(shipped, committed `aaf5203`; resilience benefit not yet observed because engines
have stayed healthy). Engine-diagnostics logging added on top of that today, still
uncommitted. The agent still CANNOT operate on local files — `tools.py` is read-only
by design and its one write-adjacent path (`run_safe_bash`) is not a security
boundary. Next action: harden `run_safe_bash` before any write tool is added (Part
I.5, item 1).

## I.5 WHAT THE AGENT STILL NEEDS (the build order)

Keep the reason attached to each item:

1. Harden `run_safe_bash` BEFORE granting write power (validates only the first word,
   then `shell=True`, so `ls; rm -rf ~` passes).
2. Line-range reading in `read_file` (`local_task` accumulates observations; a full
   dump pollutes every later step).
3. Write tools with a safety net: `write_file` and `delete_lines`, each with
   timestamped backup and `dry_run=True` BY DEFAULT, returning the proposed diff
   without touching disk.
4. Widen the allowlist to `cp`, `diff`, `python -c` — today the agent cannot back up,
   check syntax, or show its own diff.
5. Escalation policy for destructive ops: the 4B may PROPOSE; any write deleting more
   than N lines requires the 35B to review the diff.
6. An eval for the agent itself. Capability that cannot be measured cannot be
   trusted. First controlled test already designed: ask it in dry-run to identify the
   dead definitions in research.py and compare against the grep truth. The hard part
   is whether it flags `build_evidence_pack` as CHAINED (do not delete) rather than
   "3 duplicates, keep the last".

---

# PART II — TECHNICAL NOTES

Everything below is subordinate to Part I. Organised by topic, not by session date.
The original chronological session logs are preserved verbatim in the Appendix.

## II.1 Live code map — what actually executes, shadowing, `_orig_` chains

**Repository state.** `git -C ~/data-engineer-prep log --oneline -5 / tag -l /
status --short / branch -a`, VERIFIED 2026-08-09:
```
HEAD:   5712f59  General web-grounded agent: topic-neutral relevance, entity
                 quoting, 3-query cap, empty-evidence guard, judged escalation
        c1b2602  Add SearXNG web-evidence layer + patched agent_v2
        cdeca25  v3.1: escalation tier
        0c06a1a  Async draft display
        3a1df78  Add harness v3
Tag:    working-web-evidence-2026-07-20
Branch: main only (no exp/ branch exists)
Remote: https://github.com/jkzero87/data-engineer-prep.git
```
Two commits landed on top of this on 2026-08-10 (see §II.5): `b8c6b4e` (Retry-After
+ as_completed timeout) and `aaf5203` (Wikipedia-first injection).

Uncommitted as of 2026-08-09:
```
 M llm/harness/searxng/settings.yml
 M sql/dimensional/02_scd2_dim_coins.sql     ← CoinGecko project, do not mix
?? llm/harness/tools.py                       ← THE LOCAL-AGENT FILE (§II.7 below)
?? llm/harness/backups/
?? 12 × agent_v2.py.* / research.py.* / harness_chat.py.* checkpoint files
```

**Code location.** `find ~ -type f \( -name 'agent_v2*' -o -name 'research*.py' -o
... \)` + sha256, VERIFIED 2026-08-09. Exactly one copy of the harness; every other
hit was a library `tools.py` in site-packages:

| sha256 (12) | Bytes | Modified | File |
|---|---|---|---|
| `a4ae4cb840bd` | 64670 | Jul 19 18:40 | `agent_v2.py` |
| `28ce94b38291` | 57542 | Jul 19 18:42 | `research.py` |
| `26f946218bc0` | 3312 | Jul 19 18:07 | `harness_chat.py` |
| `851633fe98e9` | 2390 | Jul 18 15:01 | `queue_runner.py` |
| `f16b6e4c6b37` | 3421 | Jul 19 18:55 | `tools.py` ← newest file in the project |

`agent_v2.py.pre_strip` and `.pre_guard` are byte-identical (`f4d08f6754a9`) — one is
a redundant checkpoint. As of 2026-08-09, nothing in the project had been modified
since 2026-07-19 — that baseline is superseded by the 2026-08-10 edits recorded in
§II.5 below.

**GITIGNORE — SUPERSEDED 2026-08-10.** Original claim (2026-08-09): "`.gitignore` in
harness is only `.webcache/` and `*.bak` — the glob misses `.pre_strip`,
`.bak_award_category`, `.pre_quote` etc., which is why 12 checkpoints show as
untracked." That is now known stale: `git check-ignore -v
research.py.pre_retryafter` (2026-08-10) returns
`llm/harness/.gitignore:3:*.pre_*` — `.pre_*` backups ARE ignored correctly.

**Other repos in home** (12 found, `find ~ -maxdepth 4 -name .git`, 2026-08-09):
`de-journey`, `cripto-fintech`, `devops-prep`, `ciberseguridad-uniminuto`,
`lane-detection`, `llama.cpp`, `gpu-burn`, `it87`, 2 Android projects, 2 Rust
projects. None contain harness code.

**Shadowing in research.py.** `grep -n '^def <name>'`, VERIFIED 2026-08-10 (line
numbers current as of today's edits — they shift with every patch, do not treat them
as permanent):
- `result_score` — **SIX** top-level definitions, not five as an earlier note
  claimed (SUPERSEDED 2026-08-10; that earlier count would have left one dead
  definition in place if acted on literally). Dead at lines 578, 968, 1353, 1583,
  1818; LIVE is the last, at 1971.
- `is_relevant_result` — three definitions; live is the last.
- `search_web` — three definitions; live is the last.
- `build_evidence_pack` — three definitions: one BASE (contains the
  `ThreadPoolExecutor`/`as_completed` logic) plus two wrappers chained via
  `_orig_bep_*` — a quoting wrapper and a query-cap wrapper. Confirmed working, not
  dead: this is the enforcement point for the 3-query cap.

**`is_relevant_result` root cause** (found 2026-08-09 night): it is a BLOCKLIST, not
a relevance test. The live definition returns True unless the url or text matches
`IRRELEVANT_URL_FRAGMENTS` / `IRRELEVANT_TEXT_TERMS`. It never requires the query's
distinctive terms to appear; `result_score` uses those terms only to RANK, never to
exclude. Three symptoms traced to this one gap:
- "¿cuál es la mejor comida colombiana?" retrieved 6 PERUVIAN sources from correct
  Colombian queries. The executor abstained correctly; this was not over-abstention.
- "que es snowflake?" retrieved 5 RAE Spanish-dictionary pages (matched the stopwords
  "que"/"es"), 0 mentions of Snowflake in 9972 chars.
- Corporate snowflake.com pages passed with near-empty titles/snippets.

A fix (requiring ≥1 term from `_important_query_terms` in title+snippet+url) was
tried, REVERTED, and is UNTESTED (not rejected) — see §II.3 Open issues.

**Dead hazard, found 2026-08-10:** the hardcoded Colombian-rock scoring at
~1277-1316 (+40 for the rock_de_colombia URL, -25 for anything without
`COLOMBIA_ROCK_TERMS`) is DEAD, shadowed by later `result_score` definitions.
Correctness in this file depends on definition order; any edit risks landing in a
corpse. Cleanup (delete shadowed definitions) is backlog, §II.3.

**`fetch_wikipedia_text` was already wired in** (design correction, 2026-08-10, made
by reading the code before building Wikipedia-first): it takes a URL, not a search
term, and `fetch_url_text` already routes `wikipedia.org/wiki/` URLs through it.
Fetching was never the gap — see §II.5 for what the actual gap was.

**Eliminated by measurement, 2026-08-09 night (do not re-investigate):** planner
health (produces good queries and smart negative_terms), `search_web` signature and
behaviour, `_quote_entities`, `fetch_url_text`, `make_source` (never drops a source —
falls back to snippet), the 3-query cap (works, chained via `_orig_` wrappers).

## II.2 `tools.py` — the undocumented local agent

`cat ~/data-engineer-prep/llm/harness/tools.py` (3421 bytes, Jul 19 18:55,
**untracked**), VERIFIED 2026-08-09. Newest artifact in the project, appears in no
prior notes — the start of the goal stated in Part I.1.

Own docstring: *"Local tools for the harness. READ-ONLY: nothing here modifies the
system."*

Four tools, all path-sandboxed to `$HOME` via `_safe()` (resolves the path, rejects
anything outside `ROOT`):
- `list_dir(path)` — max 200 entries
- `read_file(path)` — truncated at 4000 chars
- `grep_files(pattern, path)` — `grep -rn`, 30s timeout
- `run_safe_bash(cmd)` — allowlist of 18 read-only commands: `ls cat head tail wc df
  du find grep git systemctl docker nvidia-smi free uname which ss date ps`

`local_task(task, max_steps=5)` is a plan→act→observe loop driven by the brain
(8091), accumulating observations into history, expecting JSON `{thought, tool,
args, done, answer}`. System prompt ends with *"Never invent file contents or
command output."* Returns `OK`, `ERROR`, or `MAX_STEPS`.

**Known weakness:** `run_safe_bash` checks only the FIRST word against the
allowlist, then runs the string with `shell=True`. `ls; rm -rf ~` passes the check.
The allowlist stops accidents, not a determined model. Not urgent — the brain is
local and not adversarial — but it is not a security boundary. This is Part I.5
item 1.

## II.3 Open issues

- **Executor repetition loop (OPEN).** Attempt-1 degenerate loops observed at temp
  0.1 AND 0.3 ("Los Redondos" repeated hundreds of times; judge confirmed), 2026-08-09.
  `repeat_penalty` was tried as a fix and REJECTED — see §II.6 Graveyard. Fires ~1 in
  3 attempt-1 runs; retry rescues it. Judged the lesser evil vs always-corrupted
  JSON.
- **Executor memory-blending (OPEN).** Attempt 1 names entities absent from evidence
  (evidence pack verified clean: 0 mentions of the foreign bands across 8778 chars,
  6 on-topic sources), 2026-08-09. Fix candidate, not yet built: a grounding rule in
  EXECUTOR_SYSTEM_V2 — never name entities not present in evidence.
- **`is_relevant_result` relevance requirement — reverted, UNTESTED, not rejected.**
  Requiring ≥1 distinctive query term in title+snippet+url. Two suite runs at 8/10
  with different failures each, but the reverted baseline also came back 9/10, so
  the change could not be distinguished from engine noise (2026-08-09 night). Now
  measurable on healthy engines (§II.4).
- **`harness_log.jsonl` contents** — not parsed as of the 2026-08-09 baseline. Prior
  reading suggested it contains statuses the current code cannot emit, meaning it
  mixes eras.
- **Which `plan_research` executes at runtime** — three definitions exist across two
  files; resolution depends on import order, which grep cannot settle (2026-08-09).
- **The control question and LG2024 results** — last confirmed 2026-07-20, before
  P7–P10 were committed (2026-08-09).
- **Backlog, unordered:**
  - Delete the shadowed definitions in research.py (§II.1) — the concrete first
    target named in Part I.1.
  - Run-id or separator in `eval_results.jsonl` — it is cumulative with no boundary
    between runs (§II.8).
  - Per-task flush in eval.py — currently silent until process exit (§II.8).
  - `docker update --restart unless-stopped searxng` — container does not autostart
    (§II.4).
  - Fix both service units — executor needs its lost flags back; supervisor needs
    `--parallel 1` decided one way or the other (§II.7). Originally logged
    2026-08-09, not yet done as of the last verification.
  - Commit `tools.py` and the SearXNG settings — as of 2026-08-09 they existed only
    on this machine, untracked.

## II.4 Search engine health — the main confound

`docker ps -a` / `docker inspect` / `sudo cat searxng/settings.yml`, VERIFIED
2026-08-09: container `searxng` (image `searxng/searxng`) was Exited (0), 2 weeks
idle. `RestartPolicy=no` — confirmed, it will never autostart; `jkhelper` is the only
thing that brings it up. `settings.yml` present, owner uid 977,
`use_default_settings: true`, `limiter: false`, `formats: [html, json]`,
`safe_search: 0`. Engines explicitly enabled: mojeek, marginalia, qwant, wikipedia,
wikidata, bing, duckduckgo, brave, startpage, github, stackoverflow, askubuntu,
arxiv. The independent-index resilience plan WAS applied (those engines are in the
file) — but the file is uncommitted, so it exists only on this machine.

**Health has swung between sessions, same machine, same config:**
- 2026-08-09 (proof-of-life session): query "colombia" returned 39 results from
  bing, duckduckgo, google cse. Unresponsive: brave (too many requests), qwant
  (CAPTCHA), startpage (CAPTCHA).
- 2026-08-09 (night session): unresponsive_engines: brave (suspended), duckduckgo
  (CAPTCHA), google cse (suspended), mojeek (access denied), qwant (CAPTCHA),
  startpage (CAPTCHA) — effectively bing only. With one engine the result mix
  collapses and irrelevant pages dominate. Suite scores that session: 10/10, 10/10,
  9/10, 8/10, 8/10, 9/10 — the variance was the engines, not the code.
- 2026-08-10: SearXNG container was not running at all (`docker ps` returned
  nothing) — reboot, no autostart. `docker start searxng` revived it. Health probe:
  37 results, engines contributing = brave, duckduckgo, google cse, bing;
  unresponsive_engines = qwant (CAPTCHA), startpage (CAPTCHA) only. The near-total
  blockage from the night before was temporary; measurement was unblocked.

**Wikipedia-first floor, shipped 2026-08-10** (full fix detail in §II.5): guarantees
a Wikipedia candidate independent of SearXNG health. **NOT PROVEN as of 2026-08-10:**
the resilience benefit specifically. All engines were healthy for the entire session
the feature was built and measured in, so it has never been observed doing the thing
it was built for. Measurement says it is cheap (with `limit=1`) and does not hurt.
The payoff remains a hypothesis until engines degrade again — logging
`unresponsive_engines` per task (done, §II.5) is what will finally let this be
checked.

## II.5 Certified fixes, committed

Rule in force since 2026-08-09: no fix commits unless the full eval.py suite holds
or improves (§II.8).

**FIX 1 — `required_entities` injection removed** (2026-08-09; agent_v2.py
~1088-1089 commented; field kept in plan for logging; backup
`.pre_entities_fix`). The planner hallucinates this field from parametric memory
before evidence exists (measured: 5/6, 8/10, and 8/10 non-Colombian entities across
runs, different every time) and the judge graded against it. Control question:
ESCALATED/3 attempts/83.7s → ACCEPTED/2 attempts/~52s, 3/3 runs.

**FIX 2 — guard respects `needs_web`** (2026-08-09; `run_task` wrapper at ~1902; if
`plan.needs_web` is False, result returned unchanged; missing field = True,
fail-closed; backup `.pre_needsweb_fix`). Suite after both fixes: 10/10 (235.6s),
mechanicals ACCEPTED in 1 attempt (~10-11s); "photo" (photosynthesis) went
INCONCLUSIVE → ACCEPTED in 1 attempt 13.7s.

**Planner rule refinement — `needs_web=false` only when justified** (2026-08-09
night, committed, gated by eval.py): true only when the task carries its own data
(extraction/transformation/formatting/arithmetic) or asks about a generic concept
with no proper noun; true whenever a specific product, company, person, event,
standard or version is named. Measured before/after over 5 plans each: "que es
snowflake?" 3/5 → 5/5 true; "latest stable Linux kernel" 5/5 true (held); "que es un
dead letter queue?" 5/5 false (held — the rule is not blunt). Closes the hole where a
definitional question about a named product could be answered from model memory and
marked ACCEPTED with zero sources.

**Retry-After stall fix, commit `b8c6b4e`** (2026-08-10; `git show --stat b8c6b4e`:
+9/-3 — SUPERSEDED an earlier note that said +31/-1, verified 2026-08-10). Root
cause: an eval.py run blocked >23 minutes on `rock_co`, the first web task. `ps`
showed %CPU 0.0, STAT Sl+, WCHAN futex_do_wait. `ss -tnp` showed EVERY socket in
CLOSE-WAIT with Recv-Q>0, including local ports 8090/8091/8888 — remotes had closed,
the process was not reading or closing them, ruling out "fetch waiting on a slow
host" (that would show ESTAB). `sudo .venv/bin/py-spy dump --pid <pid>` showed two
ThreadPoolExecutor workers parked in `urllib3/util/retry.py:362 sleep_for_retry` —
the Retry-After branch, not the backoff branch — inside `fetch_html_text ->
fetch_url_text -> make_source`, while MainThread waited in `as_completed` with no
timeout. RETRY had `total=2`, `backoff_factor=0.4`, 429 in `status_forcelist`, and
`respect_retry_after_header` at its default True; backoff arithmetic caps the worst
case at ~37s (3 attempts × 12s WEB_TIMEOUT + 1.2s), so a rate-limited host must have
returned a 429 with a long Retry-After that urllib3 obeyed literally. Fix: (1)
`respect_retry_after_header=False` in the RETRY block; (2)
`as_completed(future_to_url, timeout=TIMEOUT*4)` in the BASE `build_evidence_pack`,
catching `concurrent.futures.TimeoutError`, logging the unfinished URLs, and
continuing with the sources that completed. **CAVEAT — the two fixes are
load-bearing TOGETHER:** `with ThreadPoolExecutor(...)` calls `shutdown(wait=True)`
on exit, so the `as_completed` timeout alone does not bound the block. Do not revert
`respect_retry_after_header` believing the timeout covers it. Confirmation: no
`"[build_evidence_pack] timed out"` line appeared in any subsequent run — the
Retry-After fix alone resolved it; the timeout stands as a backstop. `rock_co` ran
53.4s and 48.5s where it had consumed 20+ minutes.

**Wikipedia-first candidate injection, commit `aaf5203`** (2026-08-10). The gap was
candidate SUPPLY, not fetching (`fetch_wikipedia_text` was already wired in, §II.1):
Wikipedia pages only entered the evidence pack when SearXNG happened to return one,
so when engines collapsed Wikipedia vanished with them. Added
`search_wikipedia(query, limit)` calling the Wikipedia search API
(`action=query&list=search`) directly, independent of SearXNG, injecting hits into
the raw candidate list before dedupe and ranking. Additive: SearXNG collection
unchanged; returns `[]` on any exception. `MAX_FETCH=6` is fixed and every task
reports `src=6` before and after, so Wikipedia DISPLACES rather than adds — at
`limit=2`, up to 6 candidates were injected on one task, enough to occupy every
slot. Measured three-way: no Wikipedia 246.6s/239.0s (9/10, 10/10); `limit=2`
282.6s/275.0s (8/10, 9/10) — a reproducible +36s in both runs; `limit=1`
261.4s/193.8s (8/10, 10/10). `limit=1` shipped: the time penalty disappears and
injection drops to 1-3 per task. The score drops at `limit=2` were VARIANCE, not
regression — targeted re-runs passed 4/4 (rock_co ×2, comida ×2, all ACCEPTED in 2
attempts). `comida` improved against baseline: chronically INCONCLUSIVE at 3
attempts before, ACCEPTED at 2 in 4 of 5 observations after — that was the task
whose failure traced to Peruvian sources (§II.1).

**Engine-diagnostics logging, uncommitted as of 2026-08-10** (`git status --short
research.py` shows `M research.py`, verified 2026-08-10). `search_searxng` now
records into a module-level `LAST_SEARCH_DIAGNOSTICS` dict, per query: the
`unresponsive_engines` value on a live HTTP call, or an explicit CACHED marker (not
an empty list — the distinction between "engines are healthy" and "we did not ask"
must survive a cache hit) on the cache-hit early-return path. The BASE
`build_evidence_pack` clears that dict at the start of every call (added as a
same-day follow-up, after noticing the dict was never cleared, so a task whose
queries never reach `search_searxng` — e.g. the DDG fallback path — could otherwise
inherit a PREVIOUS task's diagnostics and silently misreport them as its own),
reads the accumulated diagnostics after the search loop, includes them in the
returned dict under `search_diagnostics` (no existing key removed — agent_v2.py
consumes this dict), and prints one summary line per task distinguishing live
queries from cached ones. This is what will finally make the Wikipedia-first
resilience claim above checkable.

## II.6 Graveyard — do not re-propose

**`repeat_penalty` for the executor repetition loop** (2026-08-09, REVERTED via git
restore). Three configurations tested, each gated by eval.py:

| Config | Suite | Failures |
|---|---|---|
| 1.1 global (all roles) | 7/10 | days (nested JSON array), rock_co ESCALATED, lg2024 INCONCLUSIVE |
| 1.1 executor-only | 9/10 | days (nested array) — web tasks recovered, confirming the global penalty was damaging the judge/planner |
| 1.05 executor-only | 8/10 | days (nested array) again + kernel (suite check bug, see below) |

`days` produced `[["lunes",...]]` (nested array) in 3/3 runs with a penalty active vs
clean exact-match without. VERDICT: any `repeat_penalty` distorts the executor's
JSON structure. Smarter candidates if the loop justifies revisiting: penalty applied
only on retry attempts, or a structural loop detector (repeated n-gram counter) in
code. The loop itself remains OPEN — see §II.3.

Side note from this experiment: the "kernel" failure at 1.05 was a suite bug, not a
harness bug — the answer came back in Spanish ("núcleo") and the check only matched
English terms; check widened to `["kernel","núcleo","Linux"]`. Also: the judge
ACCEPTED the malformed nested-array `days` output every time — the suite's
mechanical `json_equals` caught what the 35B judge waved through. Mechanical checks
outrank the judge on structure (this is Part I.2).

## II.7 System, hardware, and environment

**Hardware** (`nvidia-smi` / `free -h` / `df -h`, VERIFIED 2026-08-09):

| Item | Value |
|---|---|
| GPU | RTX 5060 Ti, 1223 / 16311 MiB used |
| Driver | **595.84** |
| RAM | 30Gi total, 25Gi available, 8Gi swap (unused) |
| Disk | `/dev/nvme0n1p2` 469G, 221G used, 224G free, single partition |

**Models** (`ls -la ~/models/` + `head -c 20000000 <gguf> | strings | grep -i
"nextn\|mtp\|draft"`, VERIFIED 2026-08-09):

| File | Bytes |
|---|---|
| `Qwen3.5-4B-MTP-UD-Q4_K_XL.gguf` | 2,990,664,000 |
| `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | 22,853,663,008 |

Both GGUFs contain `nextn` and `draft` strings in their headers — the 35B has MTP
heads despite the filename omitting `MTP`; an earlier worry that it might not was
unfounded. Caveat: string presence is strong evidence, not proof — confirm at
runtime via the `draft_n` field in the `/v1/chat/completions` `timings` response.

**Systemd units, verbatim** (VERIFIED 2026-08-09). `harness-executor.service`
(LIVE):
```
llama-server -m ~/models/Qwen3.5-4B-MTP-UD-Q4_K_XL.gguf --host 127.0.0.1
  --port 8090 --ctx-size 8192 --parallel 1
```
`harness-executor.service.bak` (Jul 19 17:33) has MORE flags than the live one:
```
llama-server -m ~/models/Qwen3.5-4B-MTP-UD-Q4_K_XL.gguf -ngl 99 -fa on -np 4
  --reasoning off --port 8090 --ctx-size 8192 --parallel 1
```
The backup's first line is corrupted with a stray `qqq` (a vim keystroke that landed
in the buffer). The live unit is a regression from its own backup — the performance
flags were present and were lost. The backup also contradicts itself: `-np 4` and
`--parallel 1` are the same setting; whichever llama.cpp resolves last wins — do not
copy it blindly.

`harness-supervisor.service` (LIVE):
```
llama-server -m ~/models/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf -ngl 99 --n-cpu-moe 27
  -fa on -c 8192 --spec-type draft-mtp --spec-draft-n-max 2 --port 8091
```
No `--parallel 1`; no `.bak` exists for this unit. Both units `disabled` (won't
start at boot) and `inactive` (`systemctl --user list-unit-files 'harness-*'` +
`is-active`, 2026-08-09).

**MTP retraction, 2026-08-09 (proof-of-life session):** the belief above that MTP
requires `--parallel 1` is FALSE and retracted. journalctl showed `n_slots = 4` on
the supervisor; a generation probe returned `draft_n: 249, accepted: 174` (~70%)
while running 4 slots. `--parallel 1` may still be right for latency, but not for
MTP. The executor by contrast has NO MTP at all (`draft_n: None`) — confirmed by the
unit file (never passes `--spec-type draft-mtp`), not inferred. Also from that
probe: BOTH models returned empty `content` at `max_tokens=300` (whole budget spent
in `reasoning_content`) — not yet a confirmed production bug, since production uses
900 (`HARNESS_EXECUTOR_MAX_TOKENS_LIMIT`); retest at 900 was pending as of that
session.

**Environment** (`grep -n 'HARNESS\|WEB_\|SEARXNG\|PORT\|jkhelper' ~/.zshrc`,
VERIFIED 2026-08-09):
```
SEARXNG_URL=http://127.0.0.1:8888   EXECUTOR_PORT=8090   BRAIN_PORT=8091
WEB_MAX_RESULTS=12   WEB_MAX_FETCH=6   WEB_MAX_CHARS_PER_SOURCE=1800
WEB_MAX_EVIDENCE_CHARS=10000
HARNESS_EXECUTOR_EVIDENCE_CHARS=6000   HARNESS_EXECUTOR_MAX_TOKENS_LIMIT=900
HARNESS_EXECUTOR_PRIOR_CHARS=300       HARNESS_MAX_ATTEMPTS=2
```
`~/.bashrc` lines 130–132 still export 3 of these — a stale partial duplicate from
the pre-zsh fix; divergence risk if the shell ever differs. No
`HARNESS_ENABLE__*` variable is set anywhere, so patches 8, 9 and 10 in agent_v2.py
are dormant — present in committed code, never executing. `jkhelper`
(`~/.zshrc:744`) starts both units, `docker start searxng`, cd + venv activate, runs
`harness_chat.py`, traps INT/TERM to stop services on exit — no error handling, so a
failed service or container still lets the REPL launch against dead ports. venv:
`llm/harness/.venv`, Python 3.14.4; key packages: requests 2.34.2, trafilatura 2.1.0,
ddgs 9.14.4, beautifulsoup4, lxml, json_repair, pypdf.

**Performance caveat, standing since 2026-08-09:** all tok/s figures are treated as
stale until re-measured. 150 t/s executor, 74.5 t/s supervisor at `--n-cpu-moe 17`,
82 t/s headless at 14, OOM boundaries at 16 and 26 — none re-measured since Jul 27,
and the driver has changed since (580 → 595). A same-session measurement found
executor 104.1 t/s, brain 23.3 t/s cold / 57.4 t/s warm at `--n-cpu-moe 27` — single
runs, not a median of 3, indicative only per Part I.2's "measure, don't project"
rule.

## II.8 eval.py baselines and measured variance

eval.py created 2026-08-09: 10 tasks / 4 domains, mechanical checks only (status,
JSON equality, required/forbidden strings). Results append to `eval_results.jsonl`.
Rule adopted: no fix commits unless the full suite holds or improves.

**Baseline history:**
- 2026-08-09, before FIX 1/2: 5/10 (230.1s). All 5 web tasks passed; all 5
  mechanical tasks failed INCONCLUSIVE in 1 attempt — the July empty-evidence guard
  forced INCONCLUSIVE on any task with 0 sources, including tasks that need none.
  The mechanical workload had been broken since the guard was added; July's 6/6
  batch predates the guard and was never re-run. The suite caught this on its first
  execution.
- 2026-08-09, after FIX 1/2: 10/10 (235.6s).
- 2026-08-09 night, on a degraded search engine mix: 10/10, 10/10, 9/10, 8/10, 8/10,
  9/10 across repeated runs — attributed to engine variance, not code (§II.4).
- 2026-08-10, on recovered engines, no-Wikipedia baseline: 9/10 (246.6s) and 10/10
  (239.0s). Mechanicals 5/5 both runs, 1 attempt, src=0, 4.5-10.2s.
- 2026-08-10, Wikipedia-first at `limit=2`: 8/10 (282.6s), 9/10 (275.0s).
- 2026-08-10, Wikipedia-first at `limit=1` (shipped): 8/10 (261.4s), 10/10 (193.8s).

**Noise floor, characterized 2026-08-10:** 1-2 web tasks wobble per run, a different
task each time — lg2024 failed run 1 and passed run 2 in one pair; comida did the
reverse. A single suite score cannot distinguish a regression from variance; targeted
re-runs are required before calling a web-task result a regression (Part I.2). The
spread is wider than it first looks — 261.4s vs 193.8s between runs otherwise
comparable — because one task escalating to 3 attempts costs ~40s.

**Discovery closed, 2026-08-09:** no hidden material exists. July Claude Code
transcripts are unrelated (fans, dock icons). Qwen 3.8 Max ran via web, left nothing
on disk. The code is the only record of the P1-P10 patches.

## II.9 Tooling and diagnostic recipes

- `sudo .venv/bin/py-spy dump --pid <pid>` prints every thread's stack without
  touching the process. Requires sudo (yama ptrace restriction) — without it, it
  prints NOTHING, no output, no error. Install with the venv's full pip path; system
  pip refuses under PEP 668. (2026-08-10)
- `eval_results.jsonl` is CUMULATIVE with no separator between runs. A `tail -10`
  once returned the PREVIOUS night's run and was briefly read as the current one.
  Always check the last record's timestamp before trusting a tail. (2026-08-10)
- eval.py does not flush per task, and `| tail -20` buffers all output until the
  process exits, so a running suite shows NOTHING and a stall is indistinguishable
  from progress. Use `| tee eval_run.log` instead. The real live progress meter is
  `harness_log.jsonl`, which `log_record` writes per task. (2026-08-10)
- `ss -tnp` distinguishes a slow remote host (ESTAB) from a process that isn't
  reading/closing sockets it already has (CLOSE-WAIT with Recv-Q>0) — the second
  pattern is what a missing `as_completed` timeout looks like. (2026-08-10)
- jkhelper stops both models on REPL exit; probes run after that will silently
  measure a dead brain. Always verify the port answers before trusting output.
  (2026-08-09 night)
- `len(evidence_text)==149` is not necessarily an empty pack — it can be
  `_empty_evidence`'s explanatory text. Print the string itself before concluding
  evidence is missing; this exact confusion once cost a multi-hour hunt.
  (2026-08-09 night)

## II.10 UNVERIFIED — believed, not confirmed by command

Carried forward from the 2026-08-09 baseline, relocated without re-verification.
Cross-check against §II.3 Open issues and §II.5 Certified fixes before treating any
of these as still open — some may have been settled by later sessions, but settling
them here would require re-verification this restructuring did not do.

- All performance numbers not otherwise re-measured in §II.7.
- Which `plan_research` executes at runtime.
- Whether the shadowed patches matter beyond what §II.1 mechanically confirms —
  `result_score` ×6, `run_task` ×3 etc. were reported by an agent, not all confirmed
  by a command in the 2026-08-09 baseline.
- Whether the harness still works at all, as of the 2026-08-09 baseline specifically
  (subsequent sessions ran it repeatedly; this line is preserved as originally
  written, not updated).
- The control question and LG2024 results, last confirmed 2026-07-20.
- `harness_log.jsonl` contents, not parsed as of the 2026-08-09 baseline.

## II.11 Superseded — original working agreements (2026-08-09)

Superseded by Part I.2, which supersedes and extends this list. Kept for the
record, not for use:

- Do not rewrite from scratch. Patch and extend.
- One change at a time. Back up before editing.
- Granular assistance only: generate a function or block, Juan reviews and tests,
  then continue. The goal is learning, not shipping.
- Measure, don't project. Three runs, take the median.
- A config counts only if it completes inference, not if it merely loads.
- Update this file in the same session as any change, with the command that proves
  it.

---

# APPENDIX — DATED SESSION LOGS (history, not current state)

Preserved verbatim from the pre-restructure file. Facts here have been merged into
Part II above; this appendix exists for provenance and narrative detail Part II
compresses out. Do not treat anything here as more current than Part II.

## Appendix A — SESSION LOG, 2026-08-09: proof of life after 3 weeks cold

Cold start with services UNCHANGED, to establish an honest baseline before any fix.
Driver 595.84. Monitor on dGPU. Both models resident.

**Stack came up.** `systemctl --user start harness-executor harness-supervisor`
+ `docker start searxng`, 90s wait. Both units active. Ports 8090, 8091, 8888
listening. VRAM 15130 / 16311 MiB. No CUDA errors in journalctl — the 580 -> 595
driver change did NOT break the CUDA 13.1 build.

**journalctl, verbatim:**
- executor: `n_slots = 1, n_ctx_slot = 8192, kv_unified = 'false'`
- supervisor: `n_slots = 4, n_ctx_slot = 8192, kv_unified = 'true'`
- supervisor warning: `tensor overrides to CPU are used with mmap enabled -
  consider using --no-mmap` (note: --no-mmap was measured 5.7% SLOWER in July)
- supervisor load time 28s, executor 6s

**Generation probe** (`curl /v1/chat/completions`, "Write 150 words about
databases.", max_tokens=300):

| Endpoint | tok/s | draft_n | accepted | content_len | reasoning_len |
|---|---|---|---|---|---|
| executor 8090 | 104.1 | None | None | 0 | 1308 |
| brain 8091 | 23.3 | 249 | 174 | 0 | 1475 |

NOTE: brain 23.3 t/s was a cold-cache first run; warm runs same day measured
57.4 t/s.

**FINDING 1 — MTP works with n_slots=4.** The brain returned draft_n 249 with 174
accepted (~70%) while running 4 slots. The prior belief that MTP requires
`--parallel 1` is FALSE and is retracted. `--parallel 1` may still be right for
latency, but not for MTP.

**FINDING 2 — executor has no MTP at all.** `draft_n: None`. Its unit never passes
`--spec-type draft-mtp`. Confirmed by the unit file, not inferred.

**FINDING 3 — empty content on BOTH models at max_tokens=300.** Whole budget spent
in reasoning_content; content empty. NOT yet a confirmed production bug: production
uses 900 (HARNESS_EXECUTOR_MAX_TOKENS_LIMIT). Retest at 900 pending.

**MEASURED SPEEDS SUPERSEDE ALL PRIOR NUMBERS:**
- executor: 104 t/s (notes claimed 150 — claim retracted, was never re-measured)
- brain at --n-cpu-moe 27, both models resident: 23.3 t/s (notes claimed 74.5 at
  --n-cpu-moe 17, a different and untested config)
- Single run each, not a median of 3. Treat as indicative, not certified.

**SearXNG alive.** Query "colombia" returned 39 results from bing, duckduckgo,
google cse. Unresponsive: brave (too many requests), qwant (CAPTCHA), startpage
(CAPTCHA). The July engine bans persist; three working engines remain.

**Still unverified after this session:** whether the harness itself runs end to end;
which plan_research executes; whether shadowed patches matter; harness_log.jsonl
contents.

## Appendix B — SESSION LOG, 2026-08-09 (later): two general fixes certified by eval suite

**eval.py created** — 10 tasks / 4 domains, mechanical checks only (status, JSON
equality, required/forbidden strings). Results append to eval_results.jsonl.
Rule adopted: no fix commits unless the full suite holds or improves.

**BASELINE: 5/10 (230.1s).** All 5 web tasks passed; all 5 mechanical tasks
(primes, days, currency, emails, dates) failed INCONCLUSIVE in 1 attempt —
the July empty-evidence guard forced INCONCLUSIVE on any task with 0 sources,
including tasks that need none. The core mechanical workload had been broken
since the guard was added; July's 6/6 batch predates the guard and was never
re-run. The suite caught this on its first execution.

**FIX 1 — required_entities injection removed** (agent_v2.py ~1088-1089
commented; field kept in plan for logging; backup .pre_entities_fix).
The planner hallucinates this field from parametric memory before evidence
exists (measured: 5/6, 8/10, and 8/10 non-Colombian entities across runs,
different every time) and the judge graded against it. Control question:
ESCALATED/3 attempts/83.7s -> ACCEPTED/2 attempts/~52s, 3/3 runs.

**FIX 2 — guard respects needs_web** (run_task wrapper at ~1902; if
plan.needs_web is False, result returned unchanged; missing field = True,
fail-closed; backup .pre_needsweb_fix).

**AFTER BOTH: 10/10 (235.6s).** Mechanicals ACCEPTED in 1 attempt (~10-11s).
Web tasks unchanged. photo (photosynthesis) went INCONCLUSIVE -> ACCEPTED in
1 attempt 13.7s: planner marks it needs_web=false, 4B answers directly, judge
still verifies. Open item C (atemporal routing) closed by this path.

**Diagnosed, NOT yet fixed (next, one at a time, each gated by the suite):**
- Executor repetition loop: attempt-1 degenerate loops observed at temp 0.1
  AND 0.3 ("Los Redondos" repeated hundreds of times; judge confirmed). Fix
  candidate: repeat_penalty ~1.1 in llm_json payload (research.py:960), which
  currently sends only model/messages/temperature/max_tokens.
- Executor memory-blending: attempt 1 names entities absent from evidence
  (evidence pack verified clean: 0 mentions of the foreign bands across 8778
  chars, 6 on-topic sources). Fix candidate: grounding rule in
  EXECUTOR_SYSTEM_V2 — never name entities not present in evidence.
- Temperatures are env vars (agent_v2.py:48-50): HARNESS_EXECUTOR_TEMP (0.1),
  HARNESS_JUDGE_TEMP (0.0), HARNESS_BRAIN_TEMP (0.1).

**Discovery closed:** no hidden material exists. July Claude Code transcripts
are unrelated (fans, dock icons). Qwen 3.8 Max ran via web, left nothing on
disk. The code is the only record of the P1-P10 patches.

## Appendix C — SESSION LOG, 2026-08-09 (later still): repeat_penalty rejected by the suite

Attempted fix for the executor's intermittent repetition loop: repeat_penalty in
the llm_json payload. Three configurations tested, each gated by eval.py:

| Config | Suite | Failures |
|---|---|---|
| 1.1 global (all roles) | 7/10 | days (nested JSON array), rock_co ESCALATED, lg2024 INCONCLUSIVE |
| 1.1 executor-only | 9/10 | days (nested array) — web tasks recovered, confirming the global penalty was damaging the judge/planner |
| 1.05 executor-only | 8/10 | days (nested array) again + kernel (suite check bug, see below) |

days produced [["lunes",...]] (nested array) in 3/3 runs with a penalty active
vs clean exact-match without. VERDICT: any repeat_penalty distorts the
executor's JSON structure. Fully reverted via git restore. GRAVEYARD ENTRY:
do not re-propose repeat_penalty as a blanket setting. Smarter candidates if
the loop justifies revisiting: penalty applied only on retry attempts, or a
structural loop detector (repeated n-gram counter) in code.

The intermittent loop remains OPEN: fires ~1 in 3 attempt-1 runs, retry rescues
it. Judged the lesser evil vs always-corrupted JSON.

kernel "failure" at 1.05 was a suite bug, not a harness bug: the answer came
back in Spanish ("núcleo") and the check only matched English terms. Check
widened to ["kernel","núcleo","Linux"].

Note also: the judge ACCEPTED the malformed nested-array days output every
time — the suite's mechanical json_equals caught what the 35B judge waved
through. Mechanical checks outrank the judge on structure.

## Appendix D — SESSION LOG, 2026-08-09 (night): retrieval is the bottleneck

**COMMITTED, gated by eval.py:**
- Planner rule: needs_web=false ONLY when the task carries its own data
  (extraction/transformation/formatting/arithmetic) or asks about a generic
  concept with no proper noun. True whenever a specific product, company,
  person, event, standard or version is named. Measured before/after over 5
  plans each: "que es snowflake?" 3/5 -> 5/5 true; "latest stable Linux kernel"
  5/5 true (held); "que es un dead letter queue?" 5/5 false (held — the rule is
  not blunt). Closes the hole opened by the earlier needs_web guard fix, where a
  definitional question about a named product could be answered from model memory
  and marked ACCEPTED with zero sources.
- eval.py: new min_sources check on rock_co, lg2024, kernel; every result line
  now prints src=N.

**ROOT CAUSE FOUND — is_relevant_result is a blocklist, not a relevance test.**
The live definition (research.py ~1857) returns True unless the url or text
matches IRRELEVANT_URL_FRAGMENTS / IRRELEVANT_TEXT_TERMS. It never requires the
query's distinctive terms to appear. result_score uses those terms only to RANK,
never to exclude. Three separate symptoms trace to this one gap:
- "¿cuál es la mejor comida colombiana?" retrieved 6 PERUVIAN sources
  (Gastronomía del Perú, recetascocinaperuana.com x2, isil.pe, comococinar.pe)
  from correct Colombian queries. The executor abstained CORRECTLY; the brain
  named the problem explicitly. This was NOT over-abstention.
- "que es snowflake?" retrieved 5 RAE Spanish-dictionary pages (matched the
  stopwords "que"/"es"), 0 mentions of Snowflake in 9972 chars.
- Corporate snowflake.com pages passed with near-empty titles/snippets.

**Attempted fix, REVERTED, UNTESTED (not rejected):** requiring >=1 term from
_important_query_terms in title+snippet+url inside is_relevant_result. Two suite
runs at 8/10 with different failures each, but the reverted baseline also came
back 9/10, so the change could not be distinguished from engine noise.

**MEASUREMENT IS BLOCKED BY ENGINE HEALTH.** SearXNG unresponsive_engines during
this session: brave (suspended, too many requests), duckduckgo (CAPTCHA),
google cse (suspended), mojeek (access denied), qwant (CAPTCHA), startpage
(CAPTCHA). Effectively bing only. With one engine the result mix collapses and
irrelevant pages dominate. Suite scores tonight: 10/10, 10/10, 9/10, 8/10, 8/10,
9/10 — the variance is the engines, not the code.

**NEXT WORK, in order:**
1. Wikipedia-first retrieval. fetch_wikipedia_text already exists at
   research.py:1315. Wikipedia never blocks, never CAPTCHAs, always fetches.
   Guarantee it a slot in every evidence pack.
2. Log SearXNG's unresponsive_engines per task. It is returned on every response
   and currently discarded. The REPL should be able to say "search degraded"
   instead of implying no information exists.
3. Then retry the relevance requirement, measurable again.

**Eliminated by measurement tonight (do not re-investigate):** planner health
(produces good queries and smart negative_terms), search_web signature and
behaviour, _quote_entities, fetch_url_text, make_source (never drops a source —
falls back to snippet), the 3-query cap (works, chained via _orig_ wrappers).

**Method notes:** jkhelper stops both models on REPL exit; three probes tonight
silently measured a dead brain. Always verify the port answers before trusting
output. Also: len(evidence_text)==149 was not an empty header — it was
_empty_evidence's explanatory text, and printing it would have ended a
multi-hour hunt in one minute.

## Appendix E — SESSION LOG, 2026-08-10

**ENGINE HEALTH RECOVERED**
- SearXNG container was not running (`docker ps` returned nothing); it does not
  autostart after reboot. `docker start searxng` revived it. Pending chore:
  `docker update --restart unless-stopped searxng`.
- Health probe: 37 results, engines contributing = brave, duckduckgo, google cse,
  bing. `unresponsive_engines` = qwant (CAPTCHA), startpage (CAPTCHA) only. Last
  night's near-total blockage was temporary. Measurement is unblocked.

**THE 20-MINUTE STALL — FOUND AND FIXED**
- An eval.py run blocked for >23 minutes on rock_co, the first web task. All 5
  mechanicals had completed in 1 attempt (~1s executor, 4-5s judge). `ps` showed
  %CPU 0.0, STAT Sl+, WCHAN futex_do_wait.
- `ss -tnp` showed EVERY socket in CLOSE-WAIT with Recv-Q>0, including the local
  ports 8090, 8091 and 8888. Remotes had closed; the process was not reading or
  closing them. This ruled out "fetch waiting on a slow host" (that would show
  ESTAB).
- ROOT CAUSE, from `sudo .venv/bin/py-spy dump --pid <pid>`: two ThreadPoolExecutor
  workers parked in `urllib3/util/retry.py:362 sleep_for_retry` — the Retry-After
  branch, not the backoff branch — inside `fetch_html_text -> fetch_url_text ->
  make_source`, while MainThread waited in `as_completed` with no timeout.
- RETRY had `total=2`, `backoff_factor=0.4`, 429 in `status_forcelist`, and
  `respect_retry_after_header` at its default `True`. Arithmetic rules out
  backoff: 3 attempts x 12s WEB_TIMEOUT + 1.2s = ~37s worst case, vs a 20+ minute
  stall. A rate-limited host returned 429 with a long Retry-After and urllib3
  obeyed it literally.
- FIX, commit `b8c6b4e` (`git show --stat b8c6b4e`: +9 -3): (1)
  `respect_retry_after_header=False` in the RETRY block; (2)
  `as_completed(future_to_url, timeout=TIMEOUT*4)` in the BASE
  `build_evidence_pack`, catching `concurrent.futures.TimeoutError`, logging the
  unfinished URLs, and continuing with the sources that completed.
- CAVEAT, recorded explicitly: the two fixes are load-bearing TOGETHER. `with
  ThreadPoolExecutor(...)` calls `shutdown(wait=True)` on exit, so the
  `as_completed` timeout alone does not bound the block. Do not revert
  `respect_retry_after_header` believing the timeout covers it.
- Confirmation: no `"[build_evidence_pack] timed out"` line appeared in any
  subsequent run. The Retry-After fix alone resolved it; the `as_completed`
  timeout stands as a backstop. rock_co ran 53.4s and 48.5s where it had
  consumed 20+ minutes.

**BASELINE RE-ESTABLISHED ON HEALTHY ENGINES**
- 9/10 (246.6s) and 10/10 (239.0s). Mechanicals 5/5 both runs, 1 attempt, src=0,
  4.5-10.2s.
- NOISE FLOOR: 1-2 web tasks wobble per run, a different task each time. lg2024
  failed run 1 and passed run 2; comida did the reverse. A single suite score
  cannot distinguish a regression from variance. Later runs showed the spread is
  wider than it first appeared — 261.4s vs 193.8s between identical runs —
  because one task escalating to 3 attempts costs ~40s.

**WIKIPEDIA-FIRST — SHIPPED**
- Design correction found by reading the code: fetch_wikipedia_text (~1313)
  takes a URL, not a search term, and is ALREADY wired in — fetch_url_text
  routes wikipedia.org/wiki/ URLs through it. Fetching was never the gap. The
  gap was candidate SUPPLY: Wikipedia pages only entered the pack when SearXNG
  happened to return one, so when engines collapsed Wikipedia vanished with them.
- Added search_wikipedia(query, limit) calling the Wikipedia search API
  (action=query&list=search) directly, independent of SearXNG, injecting hits
  into the raw candidate list before dedupe and ranking. Additive: SearXNG
  collection unchanged. Returns [] on any exception.
- MAX_FETCH=6 is fixed and every task reports src=6 before and after, so
  Wikipedia DISPLACES rather than adds. At limit=2, up to 6 candidates were
  injected on one task — enough to occupy every slot.
- MEASURED, three-way: no Wikipedia 246.6s/239.0s (9/10, 10/10); limit=2
  282.6s/275.0s (8/10, 9/10) — a reproducible +36s in both runs; limit=1
  261.4s/193.8s (8/10, 10/10). limit=1 chosen: the time penalty disappears and
  injection drops to 1-3 per task.
- The score drops at limit=2 were VARIANCE, not regression: targeted re-runs
  passed 4/4 (rock_co x2, comida x2, all ACCEPTED in 2 attempts). Method note:
  web-task failures require targeted re-runs before being called a regression;
  mechanical failures are deterministic and count on the first observation.
- comida improved against baseline: chronically INCONCLUSIVE at 3 attempts
  before, ACCEPTED at 2 in 4 of 5 observations after. That was the task whose
  failure traced to Peruvian sources.
- NOT PROVEN: the resilience benefit. All four engines were healthy all session,
  so the change has never been observed doing the thing it was built for.
  Measurement says it is cheap and does not hurt. The payoff remains a hypothesis
  until engines degrade again.

**METHOD / TOOLING NOTES**
- `sudo .venv/bin/py-spy dump --pid <pid>` prints every thread's stack without
  touching the process. Requires sudo (yama ptrace restriction); without it, it
  prints NOTHING — no output, no error. Install with the venv's full pip path;
  system pip refuses under PEP 668.
- eval_results.jsonl is CUMULATIVE with no separator between runs. A tail -10
  returned the PREVIOUS night's run and was briefly read as the current one.
  Always check the last record's timestamp before trusting a tail. Pending
  improvement: a run-id or separator per run.
- eval.py does not flush per task, and `| tail -20` buffers all output until
  the process exits, so a running suite shows NOTHING and a stall is
  indistinguishable from progress. Use `| tee eval_run.log`. The real live
  progress meter is harness_log.jsonl, which log_record writes per task.
- Shadowing confirmed again by grep: result_score defined 5 times (live = last,
  ~1895), is_relevant_result 3 times (live ~1863), build_evidence_pack
  wrapped twice via _orig_ chaining. The hardcoded Colombian-rock scoring at
  ~1277-1316 (+40 for the rock_de_colombia URL, -25 for anything without
  COLOMBIA_ROCK_TERMS) is DEAD, shadowed by later definitions. Flagged as a real
  hazard: correctness depends on definition order, and any edit risks landing in
  a corpse. Cleanup (delete shadowed definitions) belongs on the backlog.

**NEXT WORK, in order:**
1. Log SearXNG's unresponsive_engines per task. It is returned on every response
   and currently discarded. This is also what would let us finally verify the
   Wikipedia-first resilience claim.
2. Re-try the relevance requirement in is_relevant_result (>=1 distinctive
   query term in title+snippet+url) — reverted untested last night, now
   measurable on healthy engines.
3. Backlog: delete shadowed definitions in research.py; run-id in
   eval_results.jsonl; per-task flush in eval.py; docker restart policy for
   searxng.

**NOTE ON THIS APPENDIX ENTRY (added during the 2026-08-10 restructure):** the
result_score count in this entry's own tooling notes ("defined 5 times") is the
exact count later found to be wrong — see Part II §II.1. Left unedited here
deliberately; the appendix is a verbatim historical record, not the current state.

---
