"""Lesson 05 (part 1): an agent loop with a FAKE brain. Runs offline: no API key, no cost.

The "brain" below is a handful of if-statements pretending to be an LLM. It returns
responses with the same shape as the real API (stop_reason, content blocks), so the
loop in `run_agent` is the same loop you'll use with real Claude in agent.py.

Run:  python lessons/05-the-agent-loop/fake_agent.py
"""

from types import SimpleNamespace as Obj

# ─────────────────────────────────────────────────────────────────────────────
# TOOLS: ordinary Python functions
# ─────────────────────────────────────────────────────────────────────────────
WEATHER = {
    "Paris": "14°C, heavy rain",
    "London": "11°C, drizzle",
    "Cairo": "31°C, clear and sunny",
    "Tokyo": "22°C, cloudy",
}


def get_weather(city: str) -> str:
    return WEATHER.get(city, f"No weather data for {city}.")


TOOLS = {"get_weather": get_weather}


# ─────────────────────────────────────────────────────────────────────────────
# THE FAKE BRAIN: stands in for client.messages.create(...)
# A real LLM makes these decisions by reading the history. This fake one does
# the same thing with if-statements, so you can see the logic.
# ─────────────────────────────────────────────────────────────────────────────
CANDIDATE_CITIES = ["Paris", "London", "Cairo", "Tokyo"]
_call_counter = 0


def fake_brain(messages):
    """Look at the history and decide the next step, like an LLM would."""
    # 1. Read the history: which cities have we already checked, and what came back?
    city_by_call_id = {}
    observations = {}
    for message in messages:
        if message["role"] == "assistant":
            for block in message["content"]:
                if block.type == "tool_use":
                    city_by_call_id[block.id] = block.input["city"]
        elif isinstance(message["content"], list):
            for block in message["content"]:
                if block["type"] == "tool_result":
                    observations[city_by_call_id[block["tool_use_id"]]] = block["content"]

    # 2. Decide. The next step DEPENDS ON WHAT EARLIER TOOLS RETURNED.
    for city in CANDIDATE_CITIES:
        if city not in observations:
            if observations:
                note = f"{list(observations)[-1]} is wet. Trying {city}."
            else:
                note = f"Let me start with {city}."
            return tool_use_response(note, "get_weather", {"city": city})
        weather = observations[city]
        if "rain" not in weather and "drizzle" not in weather:
            return final_response(f"Go to {city} for your picnic. It's {weather}.")
    return final_response("Sorry, it's wet everywhere I checked. Maybe a museum instead?")


def tool_use_response(text, name, tool_input):
    global _call_counter
    _call_counter += 1
    return Obj(
        stop_reason="tool_use",
        content=[
            Obj(type="text", text=text),
            Obj(type="tool_use", id=f"call_{_call_counter}", name=name, input=tool_input),
        ],
    )


def final_response(text):
    return Obj(stop_reason="end_turn", content=[Obj(type="text", text=text)])


# ─────────────────────────────────────────────────────────────────────────────
# THE AGENT LOOP: this is the part to understand and remember
# ─────────────────────────────────────────────────────────────────────────────
def run_agent(task, call_model, tools, max_turns=10):
    messages = [{"role": "user", "content": task}]
    print(f"🎯 TASK: {task}\n")

    for turn in range(1, max_turns + 1):
        # THINK: the model looks at everything so far and decides
        response = call_model(messages)
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text":
                print(f"[turn {turn}] 🗣  {block.text}")

        # DONE? If the model didn't ask for a tool, it's finished.
        if response.stop_reason == "end_turn":
            print(f"\n✅ Finished in {turn} turns.")
            return messages
        if response.stop_reason != "tool_use":
            print(f"\n⚠️  Stopped unexpectedly: {response.stop_reason}")
            return messages

        # ACT: run every tool the model asked for
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = tools[block.name](**block.input)
                print(f"[turn {turn}] 🔧 {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})

        # OBSERVE: the results become part of the history for the next THINK
        messages.append({"role": "user", "content": tool_results})

    print(f"\n🛑 Gave up after {max_turns} turns.")
    return messages


if __name__ == "__main__":
    history = run_agent(
        task="Find me a city where it's not raining, for a picnic.",
        call_model=fake_brain,
        tools=TOOLS,
    )
    print(f"\n📜 The history now has {len(history)} messages. That list is the agent's whole memory.")
