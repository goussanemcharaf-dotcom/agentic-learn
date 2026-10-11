# Lesson 03 · Memory is just a list

**Goal:** understand that the model is stateless, and that an agent's "memory"
is a Python list that you append to and resend on every call.

⏱️ ~20 minutes · 🔌 needs an API key

---

## The surprising fact

Run this experiment in your head. You make two separate API calls:

```python
client.messages.create(..., messages=[{"role": "user", "content": "My name is Sam."}])
client.messages.create(..., messages=[{"role": "user", "content": "What's my name?"}])
```

The second call has **no idea** your name is Sam. Each call is independent. The
model keeps no memory between requests.

So how does a chat app remember? **It resends the whole conversation every time:**

```python
messages = [
    {"role": "user",      "content": "My name is Sam."},
    {"role": "assistant", "content": "Nice to meet you, Sam!"},
    {"role": "user",      "content": "What's my name?"},
]
```

## Run it

```bash
python lessons/03-memory-is-just-a-list/chat.py
```

1. Tell it your name, then ask what your name is. It remembers.
2. Type `history` to see the exact list that gets sent on each call.
3. Watch the `input tokens` number climb with every message.

## The pattern

```python
messages = []
while True:
    messages.append({"role": "user", "content": input()})        # 1. add user turn
    response = client.messages.create(messages=messages, ...)    # 2. send ALL of it
    messages.append({"role": "assistant", "content": response.content})  # 3. add reply
```

This is already a loop, but it's a **chat loop**: a *human* decides what happens
on each turn. In Lesson 05 you'll replace the human with **tool results**, and
the chat loop becomes an **agent loop**.

## Two rules that will save you hours of debugging

**Rule 1: append `response.content`, not just the text.**
The response can include `thinking` blocks and (soon) `tool_use` blocks. The API
expects the assistant's turn back exactly as it was sent. Keep only the text and
you lose information. Once tools are involved, you'll get errors.

**Rule 2: only ever append.**
Treat the history as an append-only log. Editing or deleting earlier turns can
break things on current models. When the history gets too long, there are
proper tools for it (compaction, context editing), covered in Lesson 13.

## Why this matters for agents

- **The history is the agent's entire working memory.** The model sees whatever
  is in it, and nothing that isn't.
- **It grows on every turn.** An agent that makes 30 tool calls resends all 30
  calls and results on the 31st request. Cost and latency grow with it, and
  eventually you hit the context window limit.
- **You control it completely.** You can inspect it, log it, save it to disk,
  and reload it later to resume a conversation.

---

## ✍️ Exercises

1. **Prove it's stateless.** Change the code to send only the latest message
   (`messages=[messages[-1]]`) instead of all of them. Then ask "what's my name?". What happens?
2. **Save and resume.** When the user types `save`, write the history to a JSON
   file. On startup, load it if it exists.
   *Hint:* SDK block objects aren't plain dicts. Use `block.model_dump(exclude_none=True)`
   to convert them before saving.
3. **Fake a memory.** Start `messages` with a made-up exchange in which you
   already told the model your favorite color. Then ask what your favorite color is.
   (This shows the model trusts whatever is in the history, which matters for
   security later.)

<details>
<summary>Hint for Exercise 2</summary>

```python
import json, os

def to_jsonable(msg):
    content = msg["content"]
    if not isinstance(content, str):
        content = [block.model_dump(exclude_none=True) for block in content]
    return {"role": msg["role"], "content": content}

# saving
with open("history.json", "w") as f:
    json.dump([to_jsonable(m) for m in messages], f, indent=2)

# loading (plain dicts are valid input to the API)
if os.path.exists("history.json"):
    with open("history.json") as f:
        messages = json.load(f)
```

</details>

---

Next: [Lesson 04 · Tools: giving the model hands](../04-tools/)
