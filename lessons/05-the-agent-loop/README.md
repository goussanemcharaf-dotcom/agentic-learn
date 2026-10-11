# Lesson 05 · The agent loop

**Goal:** build a working agent from scratch. You'll do it twice: first with a
**fake brain** made of if-statements (offline, free), then with **Claude** as the
brain. The loop is the same both times, and that's the point of the lesson.

⏱️ ~45 minutes · 🧪 `fake_agent.py` runs offline · 🔌 `agent.py` needs an API key

---

## Part 1: the loop with a fake brain 🧪

```bash
python lessons/05-the-agent-loop/fake_agent.py
```

```
🎯 TASK: Find me a city where it's not raining, for a picnic.

[turn 1] 🗣  Let me start with Paris.
[turn 1] 🔧 get_weather({'city': 'Paris'}) -> 14°C, heavy rain
[turn 2] 🗣  Paris is wet. Trying London.
[turn 2] 🔧 get_weather({'city': 'London'}) -> 11°C, drizzle
[turn 3] 🗣  London is wet. Trying Cairo.
[turn 3] 🔧 get_weather({'city': 'Cairo'}) -> 31°C, clear and sunny
[turn 4] 🗣  Go to Cairo for your picnic. It's 31°C, clear and sunny.

✅ Finished in 4 turns.
```

Look at what happened:

- **Nobody told it to check three cities.** It checked until it found an answer.
  With different weather, it would take a different number of turns.
- **Each decision depended on the last result.** It tried London *because* Paris was rainy.

Those two properties are what make this an **agent** and not a workflow. The
number of steps, and which steps, are decided at runtime by the brain, based on
what it observes.

Open [`fake_agent.py`](fake_agent.py). The `fake_brain` function reads the
history and decides the next step with if-statements. A real LLM does the same
job, reading the history and deciding, but it can handle situations nobody wrote
an if-statement for.

## The loop, line by line

This is the heart of the course. Read it until you could write it from memory:

```python
def run_agent(task, call_model, tools, max_turns=10):
    messages = [{"role": "user", "content": task}]

    for turn in range(1, max_turns + 1):            # a safety limit, never `while True`
        response = call_model(messages)             # THINK
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":      # DONE: no tool needed
            return messages
        if response.stop_reason != "tool_use":      # something unexpected: stop
            return messages

        tool_results = []
        for block in response.content:              # ACT: run EVERY requested tool
            if block.type == "tool_use":
                output = tools[block.name](**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

        messages.append({"role": "user", "content": tool_results})  # OBSERVE
```

Compare it with the pieces from earlier lessons:

| Piece | Where you learned it |
|---|---|
| `messages` list that grows every turn | Lesson 03 (memory is a list) |
| `response.content` is a list of blocks | Lesson 02 |
| `tool_use` → run it → `tool_result` | Lesson 04 |
| `stop_reason` decides what happens next | Lesson 02 |
| **wrapping all of it in a loop** | **this lesson** |

That's all an agent is. Everything after this lesson makes the loop smarter,
safer, cheaper, or able to handle longer tasks.

## Part 2: the same loop with a real brain 🔌

```bash
python lessons/05-the-agent-loop/agent.py
python lessons/05-the-agent-loop/agent.py "Which lesson explains stop_reason, and what does it say about max_tokens?"
python lessons/05-the-agent-loop/agent.py "Is there anything in this course about security? Quote it."
```

This agent has two tools, `list_files` and `read_file`, and it can explore **this
course's own files** to answer questions. You'll see something like:

```
[turn 1] 💭 I need to see what lessons exist first...
[turn 1] 🔧 list_files({"directory": "lessons"})
[turn 1]    ↳ 00-setup/ 01-what-is-an-agent/ 02-your-first-llm-call/ …
[turn 2] 💭 Now I'll read each lesson's README...
[turn 2] 🔧 read_file({"path": "lessons/00-setup/README.md"})
[turn 2] 🔧 read_file({"path": "lessons/01-what-is-an-agent/README.md"})
[turn 2] 🔧 read_file({"path": "lessons/02-your-first-llm-call/README.md"})
...
✅ ANSWER (after 3 turns): ...
```

Open [`agent.py`](agent.py) and compare `run_agent` with the fake version. It's
the same loop, with three upgrades you'll need in every real agent:

1. **Several tool calls per turn.** In turn 2 above, Claude asked to read several
   files *at once*. The loop runs all of them and returns all the results
   together in **one** user message.
2. **Errors go back to the model instead of crashing.** If a tool raises an
   exception (a missing file, a bad argument, an unknown tool), the loop sends
   back a `tool_result` with `"is_error": True`. The model reads the error and
   usually adapts, for example by listing the folder to find the right filename.
3. **A sandbox.** `safe_path()` refuses any path outside the course folder. The
   model asks, and *your code* decides what's allowed. Never trust a tool input
   just because the model wrote it.

The `💭` lines are **summaries of the model's reasoning** (`"display": "summarized"`).
They let you watch the *think* step of think → act → observe.

---

## ✍️ Exercises

### With the fake brain (no API key needed)
1. **Change the world.** In `fake_agent.py`, make Cairo rainy too. Run it. How many turns does it take now, and what's the answer?
2. **Break the brain.** Make the brain get stuck: add
   `return tool_use_response("Checking again...", "get_weather", {"city": "Paris"})`
   as the first line of `fake_brain`. What stops the loop? What would happen without `max_turns`?
3. **Track cost.** Count the total number of messages sent across *all* calls to `call_model` (call 1 sends 1, call 2 sends 3, ...). How does it grow with the number of turns?

### With the real brain
4. **Watch it recover.** Ask: `"Read the file lessons/99-secret/README.md"`. What does the model do when it gets an error?
5. **Test the sandbox.** Ask it to read `/etc/passwd` or `../../something`. Does `safe_path` stop it?
6. **Add a tool.** Add `search_files(query)`, which returns the paths of files containing a word. Write the function, add its definition to `TOOL_DEFINITIONS`, and add it to `TOOLS`. Then ask "Which lessons mention ReAct?" Does the agent use your new tool instead of reading every file?
7. **Write your own from memory.** Close the files and write `run_agent` from scratch in a new file. If you can, you understand agent loops.

<details>
<summary>Answers for 1–3</summary>

1. It checks Paris, London, Cairo, and Tokyo: 4 tool calls and 5 turns. Tokyo is cloudy but not raining, so Tokyo is the answer.
2. `max_turns` stops it after 10 turns. Without it, the loop would never end.
   Real LLMs get stuck too, for example by retrying the same failing tool call
   again and again, and each turn costs money. **Always cap your loops.**
3. Call *n* sends 2n − 1 messages, so the total over *n* turns is n². The history grows
   **every turn**, and the total tokens sent grow roughly with the **square** of
   the number of turns. This is why long-running agents need context management (Lesson 13).

</details>

<details>
<summary>Hint for Exercise 6</summary>

```python
def search_files(query: str) -> str:
    matches = []
    for path in COURSE_ROOT.rglob("*.md"):
        if query.lower() in path.read_text(encoding="utf-8").lower():
            matches.append(str(path.relative_to(COURSE_ROOT)))
    return "\n".join(matches) or "No matches."
```

Write a clear description so the model knows when to prefer it over `read_file`,
for example: *"Find which files mention a word or phrase. Use this before reading
files when you're looking for a specific topic."*

</details>

---

## 🎉 Checkpoint

You've built an agent. Everything from here on adds to this loop. Next up:

- **Lesson 06:** many tools, parallel calls, and handling tool errors well
- **Lesson 07:** stopping safely, with turn limits, token budgets, refusals, and asking a human before risky actions
