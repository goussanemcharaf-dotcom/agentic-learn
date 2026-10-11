"""Lesson 00: check that Python, the SDK, and your API key all work.

Run:  python lessons/00-setup/check_setup.py
"""

import sys

OK = "\033[32m✔\033[0m"
FAIL = "\033[31m✘\033[0m"

# 1. Python version
if sys.version_info < (3, 10):
    print(f"{FAIL} Python {sys.version.split()[0]} is too old. Install 3.10 or newer.")
    sys.exit(1)
print(f"{OK} Python {sys.version.split()[0]}")

# 2. The Anthropic SDK
try:
    import anthropic
except ImportError:
    print(f"{FAIL} The 'anthropic' package is not installed.")
    print("   Activate your venv, then run: pip install -r requirements.txt")
    sys.exit(1)
print(f"{OK} anthropic SDK {anthropic.__version__}")

# 3. A real (tiny) API call
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
try:
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Say hello to a new student of AI agents, in one short sentence."}],
    )
except TypeError:
    # The SDK raises TypeError when it finds no credentials at all.
    print(f"{FAIL} No API key found. Set ANTHROPIC_API_KEY (see this lesson's README).")
    sys.exit(1)
except anthropic.AuthenticationError:
    print(f"{FAIL} Your API key was rejected. Check that you copied it correctly.")
    sys.exit(1)
except anthropic.APIConnectionError:
    print(f"{FAIL} Could not reach the API. Check your internet connection.")
    sys.exit(1)

print(f"{OK} API call succeeded\n")
for block in response.content:
    if block.type == "text":
        print("Claude says:", block.text)
