# Lesson 04 · Tools: giving the model hands

**Goal:** understand exactly how a model "uses a tool". You'll do one complete
round trip by hand, with no loop yet, so every step is visible.

⏱️ ~30 minutes · 🔌 needs an API key

---

## The big misunderstanding

Many people think tool use means *the model runs your code*. **It doesn't.**

What actually happens:

1. You **describe** a tool to the model: its name, what it does, and what inputs it takes.
2. The model **replies with a request**: "please run `get_weather` with `{"city": "Paris"}`".
3. **Your code** runs the function.
4. You **send the result back** as a new message.
5. The model **reads the result** and continues.

The model only ever produces text, but now that text can be a structured
request your program understands.

## Run it

```bash
python lessons/04-tools/tool_call.py
python lessons/04-tools/tool_call.py "Do I need sunglasses in Cairo today?"
python lessons/04-tools/tool_call.py "What's 2 + 2?"     # does it use the tool?
```

Read [`tool_call.py`](tool_call.py) alongside the output. The numbered comments
match the steps below.

## The conversation, message by message

This is what `messages` looks like by the end. Study it, because it's the
foundation of every agent:

```python
[
  # 1. The user asks
  {"role": "user", "content": "What's the weather in Paris? Should I bring an umbrella?"},

  # 2. The model replies with a tool request (stop_reason == "tool_use")
  {"role": "assistant", "content": [
      {"type": "text", "text": "Let me check the weather."},                # optional
      {"type": "tool_use", "id": "toolu_01A...", "name": "get_weather",
       "input": {"city": "Paris"}},
  ]},

  # 3. We run it and send back the result, in a USER message
  {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "toolu_01A...", "content": "14°C, heavy rain"},
  ]},
]
# 4. The model answers: "It's 14°C with heavy rain, so yes, bring an umbrella." (stop_reason == "end_turn")
```

Things to notice:

- **Tool results go in a `user` message.** From the API's point of view, everything
  that isn't the model is the "user", and that includes your tool-running code.
- **`tool_use_id` links each result to its request.** The model can ask for
  several tools at once (Lesson 06), and the IDs keep the answers matched up.
- **You send `tools=[...]` on every call.** The API is stateless (Lesson 03),
  so the model needs to see the tool list again each time.

## Writing good tool definitions

The model decides *whether* and *how* to use a tool based only on the
definition. A good definition is a small prompt in its own right.

```python
{
    "name": "get_weather",                       # short, clear, snake_case
    "description": "Get the current weather for a city. Returns temperature and conditions.",
    "input_schema": {                            # standard JSON Schema
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Paris'"},
        },
        "required": ["city"],
    },
}
```

Tips:
- **The description is the most important part.** Say what the tool does, what it
  returns, and when to use it (or not use it). Vague descriptions lead to wrong calls.
- **Describe every parameter**, with an example of the format you expect.
- **Fewer, clearer tools beat many overlapping ones.** If *you* can't tell two
  tools apart from their descriptions, the model can't either.

## What you've built, and what's missing

You did **one** tool round trip. But what if the model wants the weather in
Paris *and then*, based on that, wants to check London? Your script calls the
API exactly twice, then stops.

The fix is to **put steps 3–7 in a loop**: keep going while
`stop_reason == "tool_use"`. That loop is an agent, and building it is the next lesson.

---

## ✍️ Exercises

1. **Ask about two cities** ("Compare the weather in Tokyo and London"). Look at
   the first response. How many `tool_use` blocks are there? What breaks in the
   script? (It only handles the first one. You'll fix this properly in Lesson 06.)
2. **Add a second tool**, `get_time(city)`, that returns a fake local time. Ask
   "Is it a good time to call my friend in Tokyo?" and see whether the model picks the right tool.
3. **Break the description.** Change the tool's description to something vague
   like `"Does stuff"`. Does the model still use it? How sure does it seem?
4. **Lie to the model.** Make `get_weather` return `"35°C and snowing"`. How
   does the model handle data that doesn't make sense?

<details>
<summary>What you should notice</summary>

1. There are usually **two** `tool_use` blocks in one response. The model asks
   for both cities at once (parallel tool calls). Your script answers only the
   first, and the API rejects the next request because every `tool_use` needs a
   matching `tool_result`. Lesson 06 shows how to handle all of them.
2. The model picks tools by reading their descriptions. Clear descriptions mean correct choices.
3. It may still try it, or it may avoid it. Either way, the model is less reliable when the description is vague.
4. Models tend to trust tool output, sometimes too much. Sometimes they point out
   the contradiction. This is why tool outputs need care: they're input the model believes.

</details>

---

Next: [Lesson 05 · The agent loop](../05-the-agent-loop/)
