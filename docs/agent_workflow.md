# Agent Workflow

This project uses AI agents to build AI Portfolio Research Copilot carefully, one practical step at a time. The app must stay research-only and should help learners understand market data, signals, portfolios, and backtests without executing trades.

## Agent roles

### ChatGPT
- Plan the smallest safe change
- Explain the tradeoffs in plain language
- Draft the implementation and documentation
- Summarize what changed and what should be tested next

### Copilot
- Edit files directly in the workspace
- Keep the change focused on the request
- Preserve current app behavior unless asked otherwise
- Suggest clean, readable implementations

### Codex
- Handle larger multi-file edits
- Check for regressions across the app
- Help verify that documentation and code stay aligned

### Future Claude Code
- Review scope, safety, and clarity
- Flag risky changes early
- Improve structure, readability, and maintainability

## Development loop

1. Plan the smallest safe change.
2. Build the change in the relevant files.
3. Run or test the change.
4. Inspect the UI, outputs, and changed files.
5. Fix issues before expanding scope.
6. Summarize what changed and what should be validated next.

## Safe build rules

- Keep the project research-only.
- Do not add broker APIs.
- Do not add live trading.
- Do not place real orders.
- Do not claim guaranteed profit.
- Keep code simple and easy to inspect.
- Build one feature at a time.
- Explain every file changed and why.
- Suggest a test or run command after changes.
- Prefer research, backtesting, journaling, and paper-trading over execution features.

## Review checklist

- Is the change research-only?
- Does it preserve existing app functionality?
- Is the code easy to understand?
- Are the docs updated where needed?
- Has a verification step been run?

## Safety guardrails

- No live account access
- No broker integrations
- No execution logic
- No financial advice
- No false claims about future performance

## Safe continuation prompt

Use this prompt when continuing development:

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
