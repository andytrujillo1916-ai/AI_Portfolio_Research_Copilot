# AI Portfolio Research Copilot

AI Portfolio Research Copilot is a research-only AI quant workstation built in Streamlit. It helps users analyze market context, test strategy ideas, evaluate signal quality, and produce structured paper-trading decision support without executing real trades.

## Why I Built This

I built this project to practice full-stack quant research engineering: turning raw market context into explainable, modular decision support. The goal is to show strong product thinking, safe AI workflow design, and clear communication of uncertainty, not to build a live trading bot.

## Core Features

- Market snapshot, charting, and risk metrics
- News intelligence and sentiment context
- Signal generation and learning evaluation
- Backtesting, strategy lab, and walk-forward testing
- Opportunity ranking, conviction scoring, and execution readiness
- Position sizing, entry/exit framework, and exposure controls
- Meta decision layer, sub-agent review board, and executive dashboard
- Research logging, health checks, and workflow orchestration

## Architecture Overview

The app uses a modular engine pattern:
- `src/app.py`: orchestration and layout (tabs + shared state)
- `src/ui_sections.py`: rendering layer for each workflow section
- `src/*_engine.py`: focused research engines (signal/risk/opportunity/etc.)
- `src/database.py` + `src/db_service.py`: centralized SQLite persistence
- `tests/`: lightweight validation of core engine behavior

Detailed architecture notes are in [docs/current_architecture.md](docs/current_architecture.md).

## Screenshots

Add screenshots here as the UI evolves:
- `docs/screenshots/executive-dashboard.png`
- `docs/screenshots/strategy-lab.png`
- `docs/screenshots/research-tab.png`

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/AI_Portfolio_Research_Copilot.git
cd AI_Portfolio_Research_Copilot
```

2. Create and activate environment:

```powershell
conda create -n ai_portfolio_research python=3.11 -y
conda activate ai_portfolio_research
```

3. Install requirements:

```powershell
pip install -r requirements.txt
```

4. Run app:

```powershell
.\scripts\run_app.ps1
```

## Run Tests

```powershell
.\scripts\run_tests.ps1
```

Or:

```powershell
python -m pytest
```

## Roadmap

- Improve model-guided reasoning quality while preserving safety boundaries
- Expand evaluation quality gates and regression tests
- Strengthen research memory and cross-asset analytics
- Improve portfolio-level scenario and stress systems
- Add better visual polish and presentation artifacts

See [docs/QUANT_ROADMAP.md](docs/QUANT_ROADMAP.md) for phased planning.

## Research-Only Disclaimer

This project is for research and education only.

- No broker API integrations
- No live trading execution
- No auto-execution workflows
- No guaranteed returns or certainty claims
- Outputs are decision support, not financial advice
