# Portfolio Writeup

## Problem

Most personal investing workflows are scattered across notes, charts, and disconnected tools. This makes it hard to compare ideas consistently, track decision quality over time, and avoid overconfidence.

## Solution

AI Portfolio Research Copilot is a research-only decision-support workstation that unifies market analysis, strategy testing, risk checks, and AI-readable summaries in one modular dashboard. It is explicitly designed for paper-trading research, not live execution.

## Technical Stack

- Python
- Streamlit UI
- Pandas / NumPy data handling
- SQLite (`data/research_os.db`) for research memory
- Pytest for core engine validation
- Modular engine architecture (`src/*_engine.py`)

## Main Features

- Market context: snapshot, risk metrics, macro/sector context
- Strategy analysis: backtesting, strategy lab, walk-forward testing
- Decision support: opportunity, conviction, execution, sizing, entry/exit
- Portfolio risk controls: exposure and correlation layers
- Synthesis layers: meta decision, sub-agent board, executive dashboard
- Persistence and safety: database status, health checks, logs

## What I Learned

- How to structure a complex analytics product as composable modules
- How to add features iteratively without breaking existing behavior
- How to design AI-assisted outputs with explicit uncertainty and safety constraints
- How to keep interfaces student-readable while scaling functionality

## Future Improvements

- Expand test coverage for orchestration and DB migration paths
- Add richer visual reporting and exportable research packets
- Improve factor attribution and scenario diagnostics
- Add model-based explanation quality checks

## Resume Bullet Ideas

- Built a modular AI research workstation in Python/Streamlit with 30+ composable quant and decision-support engines.
- Designed and implemented a research-only safety architecture (no live execution) with meta decision and sub-agent consensus layers.
- Migrated project persistence from CSV files to centralized SQLite with compatibility-first service abstractions.
- Added workflow orchestration, quality gates, and health diagnostics to improve reliability and demo readiness.
