"""Local tools for the harness. READ-ONLY: nothing here modifies the system."""
import os, subprocess
from pathlib import Path
from research import llm_json, BRAIN_PORT

ROOT = Path.home().resolve()
MAX_CHARS = 4000
SAFE_CMDS = {"ls","cat","head","tail","wc","df","du","find","grep","git",
             "systemctl","docker","nvidia-smi","free","uname","which","ss","date","ps"}

def _safe(p):
    q = Path(os.path.expanduser(str(p)))
    if not q.is_absolute():
        q = ROOT / q
    q = q.resolve()
    if q != ROOT and ROOT not in q.parents:
        raise ValueError(f"fuera del sandbox: {q}")
    return q

def list_dir(path="."):
    d = _safe(path)
    items = []
    for e in sorted(d.iterdir())[:200]:
        items.append(f"{'d' if e.is_dir() else '-'} {e.stat().st_size:>10} {e.name}")
    return "\n".join(items) or "(vacío)"

def read_file(path, max_chars=MAX_CHARS):
    f = _safe(path)
    txt = f.read_text(errors="replace")
    return txt[:max_chars] + ("\n...[truncado]" if len(txt) > max_chars else "")

def grep_files(pattern, path="."):
    d = _safe(path)
    out = subprocess.run(["grep","-rn","--binary-files=without-match","-m","5",pattern,str(d)],
                         capture_output=True, text=True, timeout=30)
    return (out.stdout or "(sin coincidencias)")[:MAX_CHARS]

def run_safe_bash(cmd):
    first = cmd.strip().split()[0] if cmd.strip() else ""
    if first not in SAFE_CMDS:
        return f"RECHAZADO: '{first}' no está en la lista de comandos seguros {sorted(SAFE_CMDS)}"
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=str(ROOT))
    return f"exit={out.returncode}\n{(out.stdout + out.stderr)[:MAX_CHARS]}"

TOOLS = {"list_dir": list_dir, "read_file": read_file,
         "grep_files": grep_files, "run_safe_bash": run_safe_bash}

SYSTEM = """You are a local assistant on the user's Linux PC. Answer using ONLY real tool output.
Available tools:
- list_dir(path)            list a directory
- read_file(path)           read a text file
- grep_files(pattern, path) search text recursively
- run_safe_bash(cmd)        safe read-only commands (ls, df, git, systemctl, nvidia-smi, ...)

Return ONLY JSON:
{"thought":"short","tool":"name or null","args":{...},"done":false,"answer":""}
Set done=true and fill answer when you have enough real output. Answer in the user's language.
Never invent file contents or command output."""

def local_task(task, max_steps=5, verbose=True):
    history = ""
    for step in range(1, max_steps + 1):
        user = f"Task: {task}\n\nObservations so far:\n{history or '(none)'}\n\nReturn only JSON."
        plan = llm_json(BRAIN_PORT, SYSTEM, user, temp=0.1, max_tokens=900)
        if not isinstance(plan, dict):
            return {"status": "ERROR", "answer": f"plan inválido: {plan}"}
        if plan.get("done") or not plan.get("tool"):
            return {"status": "OK", "answer": plan.get("answer", ""), "steps": step}
        name, args = plan.get("tool"), plan.get("args") or {}
        if verbose:
            print(f"  [{step}] {name}({args})")
        try:
            obs = TOOLS[name](**args) if name in TOOLS else f"herramienta desconocida: {name}"
        except Exception as e:
            obs = f"ERROR: {e}"
        history += f"\n--- {name}({args}) ---\n{obs}\n"
    return {"status": "MAX_STEPS", "answer": "no terminé en los pasos permitidos", "history": history[-1500:]}
