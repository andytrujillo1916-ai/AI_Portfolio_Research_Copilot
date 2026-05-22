# Claude Code Guide

## Project Purpose
AI Portfolio Research Copilot is an investment research and learning dashboard. It helps users study ETFs/stocks, review market data, record notes, run simple backtests, and practice research workflows.

This project is research-only. It is not a live trading bot.

## How to Run
From the project root:

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

## Current Architecture
- `src/app.py` is the Streamlit entry point.
- `src/ui_sections.py` renders dashboard sections.
- `src/market_data.py` loads watchlist and market data.
- `src/backtester.py`, `src/signal_engine.py`, and `src/research_agent.py` support research, signals, and backtesting.
- `src/journal.py` and `src/prediction_log.py` write lightweight CSV data under `data/`.

## Coding Style
- Keep code clear, readable, and beginner-to-intermediate friendly.
- Prefer small, focused functions over clever abstractions.
- Follow the existing Streamlit and Python module patterns.
- Keep changes practical, easy to debug, and easy to explain.

## Safety Rules
- Do not add live trading.
- Do not add broker APIs.
- Do not place real orders or simulate order placement as production behavior.
- Preserve the research-only, backtesting, and paper-trading boundary.
- Prefer research tools, backtests, journals, and paper-trading experiments before any trading-related feature.
- Keep changes small and targeted.
- Do not rewrite large areas of the repo unless explicitly asked.
- Explain files changed and why.
