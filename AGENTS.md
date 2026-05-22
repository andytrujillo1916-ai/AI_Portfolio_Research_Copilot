# Agent Guidelines

This repository uses AI coding agents to support focused, practical work across Copilot, Codex, ChatGPT, and Claude Code.

## Purpose
This repo is for an AI-powered investment research and learning dashboard.
The goal is to support market study, portfolio research, notes, signals, backtesting, and paper-trading experiments without becoming a live trading system.

## Which Assistant to Use
- Use ChatGPT for architecture, learning, design tradeoffs, and explanations.
- Use Copilot for small local edits, autocomplete, and quick fixes inside one file.
- Use Codex for bigger implementation tasks, cross-file changes, tests, and repo-aware work.
- Use Claude Code for deeper repo review, larger refactors, and architecture cleanup later.

## Coding Style
- Clear and readable.
- Modular and easy to extend.
- Beginner-to-intermediate friendly.
- Student-readable, with simple explanations when needed.
- Production-aware without being overcomplicated.
- Scalable but simple.
- Easy to debug.

## Development Philosophy
- MVP first.
- Build the smallest useful step.
- No premature optimization.
- No hidden magic.
- Avoid unnecessary abstractions.
- Practical over clever.

## Agent Safety / Boundaries
Do not:
- rewrite large parts of the repo unless asked.
- touch unrelated files.
- create unnecessary dependencies.
- overengineer architecture.
- add live trading.
- add broker APIs.
- place real orders.
- turn research signals into automated trading execution.
- make assumptions if uncertain.

Always preserve the research-only trading boundary. Prefer research, backtesting, journaling, and paper-trading workflows first.

## Change Behavior
For every change:
- explain what files changed and why.
- keep edits small and targeted.
- preserve the repo structure.
- avoid changing app functionality unless explicitly asked.

Before medium or large changes:
- summarize the plan.
- identify affected files.
- explain why the changes are needed.

## How agents should work
- Write clear, student-readable code.
- Keep edits small and targeted.
- Avoid overengineering.
- Prefer MVP-first solutions.
- Preserve the repository structure.
- Explain what files changed and why.
- Keep implementations practical and scalable.
- Use markdown for design notes and tasks.
- Do not expand the project beyond research/backtesting/paper-trading without explicit approval.

## Preferred Stack
Default toward:
- Python
- FastAPI
- Streamlit
- SQLite / Postgres
- Markdown
- GitHub
- VS Code
- Docker later if needed
