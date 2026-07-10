import requests
from ddgs import DDGS

def print_diagnostics(resp):
    """Imprime metricas de una respuesta de Ollama /api/chat."""
    msg = resp["message"]

    # 1. Razonamiento (si el modelo es razonador)
    if msg.get("thinking"):
        print(f"\n--- THINKING ---\n{msg['thinking']}\n----------------")

    # 2. Tokens y velocidad (duraciones vienen en nanosegundos)
    if resp.get("eval_count"):
        eval_tps = resp["eval_count"] / resp["eval_duration"] * 1e9
        prompt_tps = resp["prompt_eval_count"] / resp["prompt_eval_duration"] * 1e9
        total_s = resp["total_duration"] / 1e9
        print(f"[stats] prompt: {resp['prompt_eval_count']} tok @ {prompt_tps:.0f} tok/s | "
              f"gen: {resp['eval_count']} tok @ {eval_tps:.1f} tok/s | "
              f"total: {total_s:.1f}s")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.6:35b-a3b"

# 1. TOOL SCHEMA: how we describe the tool TO the model.
# The model never runs code - it only reads this description
# and decides when to "ask" for the tool.
TOOLS = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current or factual information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    }
}]

# 2. THE ACTUAL TOOL: the Python that really executes.
def web_search(query):
    results = DDGS().text(query, max_results=3)
    return "\n".join(f"{r['title']}: {r['body']}" for r in results)

messages = [
    {"role": "system", "content": "You are a research assistant. STRICT RULE: you may only name artists, albums, or facts that literally appear in the web_search results in this conversation. Your internal knowledge of artists is unreliable and must never appear in answers or search queries. If the search results are insufficient, say so explicitly instead of filling gaps from memory. You may use web_search at most 3 times. Answer in the user's language, citing source titles."},
    {"role": "user", "content": "cual es el artista de rap mas grande de colombia?"}
]

MAX_ITERATIONS = 20  # safety rail: never trust a model with an infinite loop

for i in range(MAX_ITERATIONS):
    is_last = (i == MAX_ITERATIONS - 1)
    payload = {"model": MODEL, "messages": messages, "stream": False,
               "options": {"num_ctx": 16384}}
    if not is_last:
        payload["tools"] = TOOLS   # tools withheld on the final pass
    else:
        messages.append({"role": "user", "content": "Ya no hay más búsquedas disponibles. Responde AHORA en español usando solo los resultados anteriores, citando los títulos de las fuentes. No planees más búsquedas."})
        payload["messages"] = messages

    resp = requests.post(OLLAMA_URL, json=payload).json()
    msg = resp["message"]
    print_diagnostics(resp)
    messages.append(msg)

    if not msg.get("tool_calls"):
        print("\nFINAL ANSWER:\n", msg["content"])
        break

    for call in msg["tool_calls"]:
        query = call["function"]["arguments"]["query"]
        print(f"[iteration {i+1}] Executing search: {query}")
        result = web_search(query)
        messages.append({"role": "tool", "content": result})
else:
    print("\nHit max iterations without a final answer.")