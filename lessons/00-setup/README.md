# Lesson 00 · Setup

**Goal:** get your computer ready so every lesson in this course runs.

## 1. Python 3.10+

Check your version:

```bash
python3 --version
```

If it's older than 3.10, install a newer one from [python.org](https://www.python.org/downloads/).

## 2. A virtual environment

A virtual environment ("venv") keeps this course's packages separate from the rest of your system.

```bash
cd agentic-learn
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

You'll know it's active when your prompt starts with `(.venv)`. Activate it again each time you open a new terminal.

## 3. An API key

1. Go to the [Claude Console](https://platform.claude.com/) and sign up.
2. Add a small amount of credit. These lessons cost cents, not dollars.
3. Create an API key. It starts with `sk-ant-`.
4. Put it in an environment variable:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

> ⚠️ **Never paste your key into code or commit it to git.** Anyone with your key
> can spend your credit. The SDK reads it from the environment automatically.
> `.env` is already in `.gitignore` if you prefer keeping it in a file.

## 4. Check everything

```bash
python lessons/00-setup/check_setup.py
```

You should see three green ticks and a short greeting from Claude.

## No API key yet?

That's fine. [Lesson 01](../01-what-is-an-agent/) is reading only, and
[Lesson 05](../05-the-agent-loop/) includes a fully offline agent (`fake_agent.py`)
that teaches the most important idea in the course without any key.

---

Next: [Lesson 01 · What is an agent?](../01-what-is-an-agent/)
