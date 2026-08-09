# PROJECT TRUTH — Local Dual-Agent Harness

**Path:** `/home/jkzero/data-engineer-prep/llm/harness`
**Machine:** `jkzero-A520M-DS3H`
**Evidence baseline:** `harness_evidence_20260809_1506.txt`, generated 2026-08-09T15:06:17-05:00

---

## RULES FOR THIS FILE

1. Every fact carries the **command that produced it** and the **date verified**.
2. If a claim has no command, it goes in §9 UNVERIFIED. No exceptions.
3. Narrative from any AI agent (including Claude Code) is **not evidence**. Only raw
   command output is. An agent may propose a line for this file, but only by
   supplying the command and its output.
4. Session notes, chat memory, and recollection are **not evidence**. Several claims
   carried in notes for three weeks turned out to be false — see §8.
5. Re-verify before trusting anything older than the baseline date above.

---

## 1. GIT — VERIFIED 2026-08-09

`git -C ~/data-engineer-prep log --oneline -5 / tag -l / status --short / branch -a`

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

**The harness code IS committed and clean.** `agent_v2.py` and `research.py` do not
appear in `git status` — every patch through P10 is in commit `5712f59`.

Uncommitted, total:

```
 M llm/harness/searxng/settings.yml
 M sql/dimensional/02_scd2_dim_coins.sql     ← CoinGecko project, do not mix
?? llm/harness/tools.py                       ← THE LOCAL-AGENT FILE (§5)
?? llm/harness/backups/
?? 12 × agent_v2.py.* / research.py.* / harness_chat.py.* checkpoint files
```

`.gitignore` in harness is only `.webcache/` and `*.bak` — the glob misses
`.pre_strip`, `.bak_award_category`, `.pre_quote` etc., which is why 12 checkpoints
show as untracked.

**Other repos in home** (12 found, `find ~ -maxdepth 4 -name .git`): `de-journey`,
`cripto-fintech`, `devops-prep`, `ciberseguridad-uniminuto`, `lane-detection`,
`llama.cpp`, `gpu-burn`, `it87`, 2 Android projects, 2 Rust projects. **None contain
harness code.**

---

## 2. CODE LOCATION — VERIFIED 2026-08-09

`find ~ -type f \( -name 'agent_v2*' -o -name 'research*.py' -o ... \)` + sha256

**There is exactly one copy of the harness. Nothing is scattered.** Every other hit was
a library `tools.py` in site-packages. Live files:

| sha256 (12) | Bytes | Modified | File |
|---|---|---|---|
| `a4ae4cb840bd` | 64670 | Jul 19 18:40 | `agent_v2.py` |
| `28ce94b38291` | 57542 | Jul 19 18:42 | `research.py` |
| `26f946218bc0` | 3312 | Jul 19 18:07 | `harness_chat.py` |
| `851633fe98e9` | 2390 | Jul 18 15:01 | `queue_runner.py` |
| `f16b6e4c6b37` | 3421 | Jul 19 18:55 | `tools.py` ← newest file in the project |

`agent_v2.py.pre_strip` and `.pre_guard` are byte-identical (`f4d08f6754a9`) — one is
a redundant checkpoint.

**Nothing in this project has been modified since 2026-07-19.** Three weeks cold.

---

## 3. SYSTEMD UNITS — VERBATIM, VERIFIED 2026-08-09

**`harness-executor.service` (LIVE):**
```
llama-server -m ~/models/Qwen3.5-4B-MTP-UD-Q4_K_XL.gguf --host 127.0.0.1
  --port 8090 --ctx-size 8192 --parallel 1
```

**`harness-executor.service.bak` (Jul 19 17:33) — has MORE flags than the live one:**
```
llama-server -m ~/models/Qwen3.5-4B-MTP-UD-Q4_K_XL.gguf -ngl 99 -fa on -np 4
  --reasoning off --port 8090 --ctx-size 8192 --parallel 1
```
The backup file's first line is corrupted with a stray `qqq` (a vim keystroke that
landed in the buffer). **The live unit is a regression from its own backup** — the
performance flags were present and were lost.

Note the backup also contains a contradiction: `-np 4` *and* `--parallel 1`. These are
the same setting; whichever llama.cpp resolves last wins. Do not copy it blindly.

**`harness-supervisor.service` (LIVE):**
```
llama-server -m ~/models/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf -ngl 99 --n-cpu-moe 27
  -fa on -c 8192 --spec-type draft-mtp --spec-draft-n-max 2 --port 8091
```
No `--parallel 1`. The build defaults to 4 slots, and **MTP does not work with more
than one slot** — so `--spec-type draft-mtp` is being requested on a server that
cannot use it. No `.bak` exists for this unit.

**State:** both units `disabled` (won't start at boot), both `inactive`.
`systemctl --user list-unit-files 'harness-*'` + `is-active`.

---

## 4. MODELS — VERIFIED 2026-08-09

`ls -la ~/models/` + `head -c 20000000 <gguf> | strings | grep -i "nextn\|mtp\|draft"`

| File | Bytes |
|---|---|
| `Qwen3.5-4B-MTP-UD-Q4_K_XL.gguf` | 2,990,664,000 |
| `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | 22,853,663,008 |

**Both GGUFs contain `nextn` and `draft` strings in their headers.** The 35B has MTP
heads despite the filename omitting `MTP` — the earlier worry was unfounded.

*Caveat:* string presence is strong evidence, not proof. Confirm at runtime by checking
for a `draft_n` field in the `/v1/chat/completions` `timings` response.

---

## 5. `tools.py` — THE UNDOCUMENTED LOCAL AGENT — VERIFIED 2026-08-09

`cat ~/data-engineer-prep/llm/harness/tools.py` (3421 bytes, Jul 19 18:55, **untracked**)

This is the newest artifact in the project and appears in **no** prior notes. It is the
start of the stated long-term goal: an agent that works locally on the machine.

Its own docstring: *"Local tools for the harness. READ-ONLY: nothing here modifies the
system."*

**Four tools**, all path-sandboxed to `$HOME` via `_safe()` (resolves the path and
rejects anything outside `ROOT`):

- `list_dir(path)` — max 200 entries
- `read_file(path)` — truncated at 4000 chars
- `grep_files(pattern, path)` — `grep -rn`, 30s timeout
- `run_safe_bash(cmd)` — allowlist of 18 read-only commands: `ls cat head tail wc df
  du find grep git systemctl docker nvidia-smi free uname which ss date ps`

**`local_task(task, max_steps=5)`** is a plan→act→observe loop driven by the **brain
(8091)**, accumulating observations into history, expecting JSON
`{thought, tool, args, done, answer}`. System prompt ends with *"Never invent file
contents or command output."* Returns `OK`, `ERROR`, or `MAX_STEPS`.

**Known weakness in the sandbox:** `run_safe_bash` checks only the *first* word against
the allowlist, then runs the string with `shell=True`. `ls; rm -rf ~` passes the check.
The allowlist stops accidents, not a determined model. Not urgent — the brain is local
and not adversarial — but it is not a security boundary.

---

## 6. ENVIRONMENT — VERIFIED 2026-08-09

`grep -n 'HARNESS\|WEB_\|SEARXNG\|PORT\|jkhelper' ~/.zshrc`

```
SEARXNG_URL=http://127.0.0.1:8888   EXECUTOR_PORT=8090   BRAIN_PORT=8091
WEB_MAX_RESULTS=12   WEB_MAX_FETCH=6   WEB_MAX_CHARS_PER_SOURCE=1800
WEB_MAX_EVIDENCE_CHARS=10000
HARNESS_EXECUTOR_EVIDENCE_CHARS=6000   HARNESS_EXECUTOR_MAX_TOKENS_LIMIT=900
HARNESS_EXECUTOR_PRIOR_CHARS=300       HARNESS_MAX_ATTEMPTS=2
```

**`~/.bashrc` lines 130–132 still export 3 of these** — a stale partial duplicate from
the pre-zsh fix. Divergence risk: two files, one wins depending on shell.

**No `HARNESS_ENABLE__*` variable is set anywhere.** Patches 8, 9 and 10 in
`agent_v2.py` are gated behind these and are therefore **dormant** — present in the
committed code, never executing.

**`jkhelper`** (`~/.zshrc:744`): starts both units, `docker start searxng`, cd + venv
activate, runs `harness_chat.py`, traps INT/TERM to stop services on exit. No error
handling — if a service or the container fails to start, the REPL launches anyway
against dead ports.

**venv:** `llm/harness/.venv`, Python 3.14.4. Key packages: requests 2.34.2,
trafilatura 2.1.0, ddgs 9.14.4, beautifulsoup4, lxml, json_repair, pypdf.

---

## 7. SEARXNG — VERIFIED 2026-08-09

`docker ps -a` / `docker inspect` / `sudo cat searxng/settings.yml`

- Container `searxng` (image `searxng/searxng`): **Exited (0), 2 weeks idle**
- **`RestartPolicy=no`** — confirmed: it will never autostart. `jkhelper` is the only
  thing that brings it up.
- `settings.yml` present, owner uid 977, `use_default_settings: true`, `limiter: false`,
  `formats: [html, json]`, `safe_search: 0`
- Engines explicitly enabled: mojeek, marginalia, qwant, wikipedia, wikidata, bing,
  duckduckgo, brave, startpage, github, stackoverflow, askubuntu, arxiv

The independent-index resilience plan **was applied** (mojeek/marginalia/qwant/wikidata
are in the file) — but the file is uncommitted, so it exists only on this machine.

---

## 8. CORRECTIONS — claims that were believed and are FALSE

Recorded so they are not re-introduced.

| Claim carried in notes | Reality (2026-08-09) |
|---|---|
| "Nothing is committed" | HEAD `5712f59` contains the full patch stack; both main source files are clean |
| "Work is scattered across repos/folders" | One copy, one directory. 12 other repos, none with harness code |
| "P7–P10 were parked in branch `exp/patches7-10`" | No such branch. P7 is live; P8–P10 are committed but dormant behind unset env vars |
| "The executor service fix was applied (Aug 9)" | Never ran. Live unit is unchanged and is a regression from its own `.bak` |
| "The 35B GGUF may lack MTP heads" | `nextn` + `draft` present in the header |
| "`.gitignore` excludes `__pycache__`" | Harness `.gitignore` is two lines: `.webcache/`, `*.bak` |
| "Driver 580.159.03" | `nvidia-smi`: **595.84** |
| "32GB RAM" | `free -h`: 30Gi usable, 8Gi swap |

---

## 9. UNVERIFIED — believed, not confirmed by command

Do not treat any of these as fact. Each needs a measurement before it is promoted.

- **All performance numbers.** 150 t/s executor, 74.5 t/s supervisor at `--n-cpu-moe
  17`, 82 t/s headless at 14, OOM boundaries at 16 and 26 — none re-measured since
  Jul 27, and the driver has changed since (580 → 595). **Treat every tok/s figure as
  stale until re-run.**
- **Which `plan_research` executes at runtime.** Three definitions exist across two
  files; resolution depends on import order, which grep cannot settle.
- **Whether the shadowed patches matter.** `result_score` ×6, `run_task` ×3 etc. were
  reported by an agent, not confirmed by a command in this baseline.
- **Whether the harness still works at all.** Nothing has run since Jul 19. No end-to-end
  execution has been observed.
- **The control question and LG2024 results.** Last confirmed Jul 20, before P7–P10 were
  committed.
- **`harness_log.jsonl` contents.** Not parsed in this baseline. Prior reading suggested
  it contains statuses the current code cannot emit, meaning it mixes eras.

---

## 10. HARDWARE — VERIFIED 2026-08-09

| Item | Value | Source |
|---|---|---|
| GPU | RTX 5060 Ti, 1223 / 16311 MiB used | `nvidia-smi` |
| Driver | **595.84** | `nvidia-smi` |
| RAM | 30Gi total, 25Gi available, 8Gi swap (unused) | `free -h` |
| Disk | `/dev/nvme0n1p2` 469G, 221G used, 224G free, single partition | `df -h` |

---

## 11. NEXT ACTIONS — ordered

1. **Commit `tools.py` and the SearXNG settings.** They exist on one machine, untracked.
   The most interesting file in the project is one `rm` from gone.
2. **Add `.pre_*` and `.bak_*` to `.gitignore`**, or move the 12 checkpoints into
   `backups/`.
3. **Fix both service units** — executor needs its lost flags back; supervisor needs
   `--parallel 1` or its MTP flag is inert. Then **re-measure**, because §9 says every
   speed number is stale.
4. **Prove the harness still runs.** One end-to-end task. Nothing else matters until
   this passes.
5. **Then** the evaluation suite, then the shadowing cleanup.

---

## 12. WORKING AGREEMENTS

- Do not rewrite from scratch. Patch and extend.
- One change at a time. Back up before editing.
- Granular assistance only: generate a function or block, Juan reviews and tests, then
  continue. The goal is learning, not shipping.
- Measure, don't project. Three runs, take the median.
- A config counts only if it completes inference, not if it merely loads.
- Update this file in the same session as any change, with the command that proves it.

---

## 13. SESSION LOG — 2026-08-09, proof of life after 3 weeks cold

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

---

## 14. SESSION LOG — 2026-08-09 (later), two general fixes certified by eval suite

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

---
