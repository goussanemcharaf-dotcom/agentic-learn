"""Lesson 03: a chat loop. The model remembers only because WE resend the history.

Run:  python lessons/03-memory-is-just-a-list/chat.py
Type 'quit' to exit, or 'history' to see exactly what is being sent each turn.
"""

import anthropic

client = anthropic.Anthropic()

SYSTEM = "You are a friendly tutor helping someone learn about AI agents. Keep answers short."

# This list IS the model's memory. Nothing else is.
messages = []

print("Chat with Claude. Type 'history' to inspect memory, 'quit' to exit.\n")

while True:
    user_input = input("you> ").strip()
    if user_input.lower() in {"quit", "exit"}:
        break
    if user_input.lower() == "history":
        for m in messages:
            if isinstance(m["content"], str):
                print(f"  [{m['role']}] {m['content']}")
            else:
                for block in m["content"]:
                    print(f"  [{m['role']}] ({block.type}) {getattr(block, 'text', '')}")
        continue
    if not user_input:
        continue

    # 1. Add the user's message to the history.
    messages.append({"role": "user", "content": user_input})

    # 2. Send the WHOLE history. The API remembers nothing from earlier calls.
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        system=SYSTEM,
        messages=messages,
    )

    # 3. Add the model's reply to the history.
    #    Append the full `response.content` (every block), not only the text.
    #    The response may include thinking blocks, and the API expects to get
    #    them back unchanged. Editing or dropping parts of earlier turns can
    #    cause errors on current models.
    messages.append({"role": "assistant", "content": response.content})

    reply = "".join(block.text for block in response.content if block.type == "text")
    print(f"claude> {reply}")
    print(f"        (this request sent {len(messages) - 1} messages · {response.usage.input_tokens} input tokens)\n")
