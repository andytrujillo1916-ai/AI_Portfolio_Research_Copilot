# Agent Guidelines

This repository uses AI coding agents to support focused, practical work.

## Purpose
This repo is for building practical AI systems, automation tools, research tools, and future trading / decision-support projects.
The goal is to enable reusable, scalable systems without unnecessary complexity.

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
- auto-build live trading systems.
- make assumptions if uncertain.

## Change Behavior
Before medium or large changes:
- summarize the plan.
- identify affected files.
- explain why the changes are needed.
- preserve the repo structure.

## How agents should work
- Write clear, student-readable code.
- Keep edits small and targeted.
- Avoid overengineering.
- Prefer MVP-first solutions.
- Preserve the repository structure.
- Explain what files changed and why.
- Keep implementations practical and scalable.
- Use markdown for design notes and tasks.

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
