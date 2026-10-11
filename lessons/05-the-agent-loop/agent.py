"""Lesson 05 (part 2): the same agent loop, now with a REAL brain (Claude).

The agent can look around this course's own files (read-only) to answer questions.

Run:  python lessons/05-the-agent-loop/agent.py
      python lessons/05-the-agent-loop/agent.py "Which lesson explains stop_reason?"
"""

import json
import sys
from pathlib import Path

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

# The agent may only look inside the course folder.
COURSE_ROOT = Path(__file__).resolve().parents[2]


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS: the functions, then their descriptions for the model
# ─────────────────────────────────────────────────────────────────────────────
def safe_path(relative_path: str) -> Path:
    """Turn a path from the model into a real path, refusing anything outside the course."""
    path = (COURSE_ROOT / relative_path).resolve()
    if not path.is_relative_to(COURSE_ROOT):
        raise ValueError(f"{relative_path!r} is outside the course folder")
    return path


def list_files(directory: str = ".") -> str:
    path = safe_path(directory)
    entries = sorted(p for p in path.iterdir() if not p.name.startswith("."))
    return "\n".join(p.name + ("/" if p.is_dir() else "") for p in entries)


def read_file(path: str) -> str:
    text = safe_path(path).read_text(encoding="utf-8")
    limit = 10_000
    if len(text) > limit:
        return text[:limit] + f"\n\n[... truncated, {len(text) - limit} more characters]"
    return text


TOOLS = {"list_files": list_files, "read_file": read_file}

TOOL_DEFINITIONS = [
    {
        "name": "list_files",
        "description": "List the files and folders in a directory of the course. Folders end with '/'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory relative to the course root, e.g. '.' or 'lessons'",
                },
            },
            "required": ["directory"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file from the course. Long files are truncated.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to the course root, e.g. 'README.md'",
                },
            },
            "required": ["path"],
        },
    },
]

SYSTEM = (
    "You answer questions about a course on AI agents. "
    "Use the tools to look at the course files before answering, and base your answer on what you read. "
    "All paths are relative to the course root."
)


# ─────────────────────────────────────────────────────────────────────────────
# THE BRAIN: one call to Claude, with the history and the tools
# ─────────────────────────────────────────────────────────────────────────────
def call_claude(messages):
    return client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        tools=TOOL_DEFINITIONS,
        messages=messages,
        # Show a short summary of the model's reasoning so you can watch it "think".
        thinking={"type": "adaptive", "display": "summarized"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# THE AGENT LOOP: the same shape as fake_agent.py
# ─────────────────────────────────────────────────────────────────────────────
def run_agent(task, max_turns=15):
    messages = [{"role": "user", "content": task}]
    print(f"🎯 TASK: {task}\n")

    for turn in range(1, max_turns + 1):
        # THINK
        response = call_claude(messages)
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "thinking" and block.thinking:
                print(f"[turn {turn}] 💭 {shorten(block.thinking, 200)}")
            elif block.type == "text" and response.stop_reason == "tool_use":
                print(f"[turn {turn}] 🗣  {block.text}")

        # DONE?
        if response.stop_reason == "end_turn":
            answer = "".join(block.text for block in response.content if block.type == "text")
            print(f"\n✅ ANSWER (after {turn} turns):\n\n{answer}")
            return answer
        if response.stop_reason != "tool_use":
            # max_tokens, refusal, ...: anything other than "use a tool" or "done" means stop.
            print(f"\n⚠️  Stopped: stop_reason = {response.stop_reason}")
            return None

        # ACT: run every tool call in this response (there can be several)
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"[turn {turn}] 🔧 {block.name}({json.dumps(block.input)})")
            try:
                if block.name not in TOOLS:
                    raise ValueError(f"there is no tool called {block.name!r}")
                output = TOOLS[block.name](**block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
                print(f"[turn {turn}]    ↳ {shorten(output, 80)}")
            except Exception as error:
                # Tell the model what went wrong so it can try something else.
                message = f"Error: {error}"
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": message, "is_error": True}
                )
                print(f"[turn {turn}]    ↳ ❌ {message}")

        # OBSERVE
        messages.append({"role": "user", "content": tool_results})

    print(f"\n🛑 Gave up after {max_turns} turns.")
    return None


def shorten(text, width):
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or (
        "Give me a one-line summary of each lesson in this course that has been written so far."
    )
    run_agent(task)
