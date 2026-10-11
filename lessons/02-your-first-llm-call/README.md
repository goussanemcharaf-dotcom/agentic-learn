# Lesson 02 · Your first LLM call

**Goal:** send one request to Claude and understand every part of what comes back.
An agent is this same call made over and over in a loop, so it's worth knowing it well.

⏱️ ~20 minutes · 🔌 needs an API key

---

## Run it

```bash
python lessons/02-your-first-llm-call/first_call.py
python lessons/02-your-first-llm-call/first_call.py "Why is the sky blue?"
```

Then open [`first_call.py`](first_call.py) and read it top to bottom. It's short.

## The request

Every call to Claude goes to one endpoint, the **Messages API**, and has the same shape:

```python
client.messages.create(
    model="claude-opus-5-5",          # which model
    max_tokens=16000,                 # hard cap on the reply length
    system="You are a patient ...",   # standing instructions (optional)
    messages=[                        # the conversation so far
        {"role": "user", "content": "In two sentences, what is an AI agent?"},
    ],
)
```

- **`messages`** is a list. Each message has a **`role`** (`"user"` or
  `"assistant"`) and **`content`**. The list must start with a `user` message.
- **`system`** sets the model's behavior for the whole conversation. Changing it
  changes how the model answers without changing the question.
- **`max_tokens`** is a ceiling, not a target. If the model hits it, the reply is
  cut off mid-sentence, so don't set it too low.

## The response

### 1. `content` is a list of blocks

The most common beginner bug is treating the response as one string. It isn't.
It's a **list of typed blocks**:

```python
for block in response.content:
    if block.type == "text":
        print(block.text)
```

So far you've seen `text` and `thinking` blocks. In Lesson 04 you'll meet the
most important one for agents: **`tool_use`**.

### 2. `thinking` blocks

Current Claude models can **think before answering**. With *adaptive* thinking,
the model decides for itself how much to think: a lot for hard problems, little
or none for easy ones. By default the thinking text is hidden. This lesson asks
for `"display": "summarized"`, so you get a readable summary.

Try a harder question and compare:

```bash
python lessons/02-your-first-llm-call/first_call.py "A bat and a ball cost \$1.10. The bat costs \$1 more than the ball. How much is the ball?"
```

### 3. `stop_reason` drives the agent loop

| `stop_reason` | Meaning | What an agent does |
|---|---|---|
| `end_turn` | "I'm finished." | Stop the loop and return the answer. |
| `tool_use` | "Please run a tool for me." | Run the tool, send back the result, and loop again. |
| `max_tokens` | Ran out of room mid-reply. | Raise `max_tokens`, or treat it as an error. |
| `refusal` | Declined for safety reasons. | Stop, and tell the user. |

In Lesson 05 you'll write a loop that is mostly a big `if` on this one field.

### 4. `usage` is your bill

`input_tokens` is everything you sent. `output_tokens` is everything the model
wrote, including thinking. Agents resend the whole history on every turn, so
**input tokens grow with each trip around the loop**. Remember this. It becomes
important in Levels 4 and 5.

---

## ✍️ Exercises

1. **Change the system prompt** to `"You are a pirate."` and ask the same question. What changes, and what doesn't?
2. **Starve it.** Set `max_tokens=30` and ask for a long explanation. What's the `stop_reason`? What does the text look like?
3. **Count tokens.** Ask a one-word question, then paste in a long paragraph. How do `input_tokens` change?
4. **Print the raw response** with `print(response.to_json())`. Find `content`, `stop_reason`, and `usage` in it.

<details>
<summary>What you should notice</summary>

1. The style changes completely, but the facts stay the same. The system prompt controls *behavior*.
2. `stop_reason` is `"max_tokens"` and the reply stops mid-thought. If an agent hits this in the middle of a tool call, the tool request is incomplete, so a real agent must check for it.
3. `input_tokens` grows with what you send. Even a one-word question costs some tokens, because the system prompt counts too.
4. The SDK objects are just a typed view of this JSON.

</details>

---

Next: [Lesson 03 · Memory is just a list](../03-memory-is-just-a-list/)
