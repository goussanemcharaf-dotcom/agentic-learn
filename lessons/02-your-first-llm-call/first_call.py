"""Lesson 02: your first LLM call, taken apart piece by piece.

Run:  python lessons/02-your-first-llm-call/first_call.py
      python lessons/02-your-first-llm-call/first_call.py "Why is the sky blue?"
"""

import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

question = " ".join(sys.argv[1:]) or "In two sentences, what is an AI agent?"

# ── THE REQUEST ──────────────────────────────────────────────────────────────
response = client.messages.create(
    # Which model to use.
    model="claude-opus-5-5",
    # A hard cap on how many tokens the reply may use. If it's hit, the reply is cut off.
    max_tokens=16000,
    # Standing instructions. These shape *how* the model answers.
    system="You are a patient teacher. Use plain language and short sentences.",
    # The conversation so far. Right now that's just one user message.
    messages=[
        {"role": "user", "content": question},
    ],
    # Ask for a readable summary of the model's reasoning (more on this in the README).
    thinking={"type": "adaptive", "display": "summarized"},
)

# ── THE RESPONSE ─────────────────────────────────────────────────────────────
# 1. `content` is a LIST of blocks, not a single string.
print("=== Content blocks ===")
for i, block in enumerate(response.content):
    if block.type == "thinking":
        print(f"[{i}] thinking: {block.thinking or '(empty)'}\n")
    elif block.type == "text":
        print(f"[{i}] text: {block.text}\n")
    else:
        print(f"[{i}] {block.type}\n")

# 2. `stop_reason` says WHY the model stopped. In an agent, this drives the loop.
print("=== Stop reason ===")
print(response.stop_reason)  # "end_turn" means "I'm finished"

# 3. `usage` says how many tokens were read and written. This is what you pay for.
print("\n=== Usage ===")
print(f"input tokens:  {response.usage.input_tokens}")
print(f"output tokens: {response.usage.output_tokens}")
