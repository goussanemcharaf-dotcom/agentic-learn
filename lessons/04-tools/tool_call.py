"""Lesson 04: one complete tool round trip, written out step by step (no loop yet).

Run:  python lessons/04-tools/tool_call.py
      python lessons/04-tools/tool_call.py "Do I need sunglasses in Cairo today?"
"""

import json
import sys

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"


# ── 1. A normal Python function: the thing we want the model to be able to use ──
def get_weather(city: str) -> str:
    # Fake data so the lesson works offline. A real tool would call a weather API.
    fake_weather = {
        "paris": "14°C, heavy rain",
        "cairo": "31°C, clear and sunny",
        "tokyo": "22°C, cloudy",
        "london": "11°C, drizzle",
    }
    return fake_weather.get(city.lower(), f"No weather data for {city}.")


# ── 2. A DESCRIPTION of that function, written for the model ──
# The model never sees your Python code. It sees only this name, description, and schema.
weather_tool = {
    "name": "get_weather",
    "description": "Get the current weather for a city. Returns temperature and conditions.",
    "input_schema": {  # JSON Schema describing the inputs
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Paris'"},
        },
        "required": ["city"],
    },
}

question = " ".join(sys.argv[1:]) or "What's the weather in Paris? Should I bring an umbrella?"
messages = [{"role": "user", "content": question}]
print(f"USER: {question}\n")

# ── 3. FIRST CALL: send the question and the tool list ──
response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    tools=[weather_tool],
    messages=messages,
)
print(f"[call 1] stop_reason = {response.stop_reason}")

if response.stop_reason != "tool_use":
    # The model decided it didn't need the tool. That's allowed!
    print("The model answered without using the tool:")
    print("".join(b.text for b in response.content if b.type == "text"))
    sys.exit(0)

# ── 4. The model ASKED for a tool. Find the tool_use block. ──
tool_use = next(block for block in response.content if block.type == "tool_use")
print(f"[call 1] the model wants: {tool_use.name}({json.dumps(tool_use.input)})")
print(f"[call 1] tool_use id = {tool_use.id}\n")

# ── 5. WE run the tool. The model can't. ──
result = get_weather(**tool_use.input)
print(f"[our code] ran get_weather -> {result!r}\n")

# ── 6. Add BOTH turns to the history: the model's request, then our result ──
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",  # tool results go back in a *user* message
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,  # must match the request it answers
        "content": result,
    }],
})

# ── 7. SECOND CALL: the model now has the data it asked for ──
response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    tools=[weather_tool],  # always send the tools again
    messages=messages,
)
print(f"[call 2] stop_reason = {response.stop_reason}")
print("CLAUDE:", "".join(b.text for b in response.content if b.type == "text"))
