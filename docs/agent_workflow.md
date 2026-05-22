# Agent Workflow

This project uses AI agents to build the AI Portfolio Research Copilot carefully, one practical step at a time. The app is research-only for now and must stay focused on learning, market study, notes, backtesting, and paper-trading experiments.

## Development Loop

Use this loop for every feature or fix:

1. Plan: define the goal, affected files, and smallest useful change.
2. Build: make focused edits without changing unrelated behavior.
3. Run: start or test the app with the relevant command.
4. Inspect: review the UI, logs, outputs, and changed files.
5. Fix: correct issues before expanding scope.
6. Commit: summarize what changed and why.

## Agent Roles

- Builder Agent: implements small, well-scoped features using the existing project structure.
- Debugger Agent: investigates errors, reproduces issues, and proposes minimal fixes.
- Reviewer Agent: checks for bugs, regressions, unclear code, missing tests, and risky scope creep.
- Quant Research Agent: helps design indicators, backtests, comparisons, and paper-trading experiments without treating them as financial advice.
- Safety Agent: enforces research-only boundaries, blocks broker integration, and watches for profit guarantees or live execution.
- Documentation Agent: updates README, agent guidance, tasks, notes, and workflow docs so future agents understand the project.

## Rules

- Keep the project research-only for now.
- Do not add broker APIs.
- Do not add live trading.
- Do not claim or imply guaranteed profit.
- Keep code simple and easy to inspect.
- Build one feature at a time.
- Always explain changed files and why they changed.
- Always suggest a test or run command after changes.
- Prefer research, backtesting, journaling, and paper-trading before any trading-related feature.

## Safe Continuation Prompt

Use this prompt with Codex or Copilot when continuing development:

```text
You are helping build AI Portfolio Research Copilot, a research-only Streamlit app for market study, notes, simple signals, backtesting, and paper-trading experiments.

Goal:
Implement one small feature or fix at a time.

Rules:
- Do not add live trading.
- Do not add broker APIs.
- Do not place real orders.
- Do not claim guaranteed profit.
- Keep code simple and readable.
- Preserve existing app functionality unless explicitly asked.
- Explain every file changed and why.
- Suggest the command to run or test the change.

Development loop:
Plan -> Build -> Run -> Inspect -> Fix -> Commit.

Before editing, identify the smallest safe change and the files likely affected.
```
