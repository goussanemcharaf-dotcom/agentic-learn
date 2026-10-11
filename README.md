# Agentic AI: From Beginner to Expert

A hands-on course on **AI agents** and **agent loops**. You learn by reading short
lessons and running real code, one step at a time.

> **The one idea this whole course builds on:**
>
> An agent is an LLM that runs in a **loop**. Each time around, it picks a
> **tool**, sees what the tool returned, and decides what to do next. It stops
> when the job is done.
>
> ```
> while not done:
>     decision = llm(goal + everything_so_far)
>     if decision is "use a tool":
>         result = run_tool(decision)
>         everything_so_far += [decision, result]
>     else:
>         done = True
> ```
>
> The rest of the course adds detail to these lines: which tools to give the
> model, how to stop the loop safely, how to manage its memory, how to make
> several agents work together, and how to tell whether it works.

---

## How to use this course

1. Do the lessons **in order**. Each one builds on the last.
2. Each lesson folder has a `README.md` (read this first) and one or more `.py` files (run these).
3. **Type the code yourself** when you can, rather than only reading it.
4. Do the **exercises** at the end of each lesson. That's where most of the learning happens.
5. Tick the boxes in the roadmap below as you go.

Lessons marked 🔌 call the real Claude API and need an API key (see [Lesson 00](lessons/00-setup/)).
Lessons marked 🧪 run **offline**, with no key and no cost.

---

## Roadmap

### Level 1: Foundations (what an LLM call is)
- [ ] [00 · Setup](lessons/00-setup/): Python, an API key, and a check that everything works
- [ ] [01 · What is an agent?](lessons/01-what-is-an-agent/): the mental model, the vocabulary, and workflows vs. agents
- [ ] [02 · Your first LLM call](lessons/02-your-first-llm-call/) 🔌: messages, roles, content blocks, `stop_reason`
- [ ] [03 · Memory is just a list](lessons/03-memory-is-just-a-list/) 🔌: the model is stateless, so *you* keep the history

### Level 2: The agent loop (the core skill)
- [ ] [04 · Tools: giving the model hands](lessons/04-tools/) 🔌: tool schemas, `tool_use`, `tool_result`
- [ ] [05 · The agent loop](lessons/05-the-agent-loop/) 🧪 + 🔌: build the loop with a fake brain first, then a real one
- [ ] 06 · Many tools, parallel calls, and tool errors
- [ ] 07 · Stopping safely: turn limits, budgets, refusals, human approval

### Level 3: Workflow patterns (loops *you* control)
- [ ] 08 · Prompt chaining and routing
- [ ] 09 · Parallelization: splitting work into sections, and voting
- [ ] 10 · The evaluator–optimizer loop: generate → critique → improve
- [ ] 11 · Orchestrator–workers

### Level 4: Real agents
- [ ] 12 · A coding agent: file and shell tools in a sandbox
- [ ] 13 · Context engineering: compaction, context editing, long-term memory
- [ ] 14 · Structured outputs and strict tools
- [ ] 15 · The SDK Tool Runner (and when to write your own loop)

### Level 5: Expert
- [ ] 16 · Multi-agent systems and subagents
- [ ] 17 · MCP: connecting agents to any tool or data source
- [ ] 18 · Evals: measuring whether your agent actually works
- [ ] 19 · Production: cost, caching, observability, safety, prompt injection
- [ ] 20 · Beyond your own loop: the Claude Agent SDK and Managed Agents
- [ ] 🏆 Capstone: design, build, and evaluate your own agent

Lessons without links haven't been written yet. They get added as you progress.

---

## Quick start

```bash
git clone <this repo>
cd agentic-learn
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python lessons/00-setup/check_setup.py
```

Requires **Python 3.10 or newer**.
