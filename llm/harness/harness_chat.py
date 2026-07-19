#!/usr/bin/env python3
"""
harness_chat.py — Interactive REPL for the harness (Claude Code style).

Type a question, the worker/supervisor pipeline answers, repeat.
Commands:  /exit  quit   |   /last  show full detail of the last run
"""

from agent_v2 import run_task
import readline  # noqa: F401 — solo importarlo habilita edición de línea en input()

# ANSI color codes: \033[<n>m switches terminal text style. 0 resets.
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{CYAN}
  ┌─────────────────────────────────────────────┐
  │  HARNESS CHAT — 4B worker · 35B judge       │
  │  /exit to quit · /last for run details      │
  └─────────────────────────────────────────────┘{RESET}"""


def main() -> None:
    print(BANNER)
    last = None

    while True:
        try:
            task = input(f"\n{CYAN}you ▸ {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C / Ctrl+D exit cleanly instead of crashing.
            print(f"\n{DIM}bye.{RESET}")
            break

        if not task:
            continue
        if task == "/exit":
            print(f"{DIM}bye.{RESET}")
            break
        if task == "/last":
            if last is None:
                print(f"{DIM}no runs yet.{RESET}")
                continue
            for a in last["attempts"]:
                ok = f"{GREEN}ACCEPT{RESET}" if a["accepted"] else f"{RED}REJECT{RESET}"
                print(f"{DIM}attempt {a['attempt']} · exec {a['t_executor_s']}s"
                      f" · judge {a['t_supervisor_s']}s ·{RESET} {ok}")
                if a.get("errors"):
                    print(f"{YELLOW}{a['errors']}{RESET}")
            continue

        print(f"{DIM}thinking...{RESET}")
        last = run_task(task)

        color = GREEN if last["status"] == "ACCEPTED" else YELLOW
        tag = "✓" if last["status"] == "ACCEPTED" else "⚠ unverified"
        print(f"\n{color}{tag}{RESET} {last['final_output']}")


if __name__ == "__main__":
    main()
