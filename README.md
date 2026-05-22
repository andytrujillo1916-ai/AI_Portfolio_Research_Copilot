# AI Portfolio Research Copilot

## Project goal
Build an AI-powered investment research and learning dashboard focused on market study, portfolio tracking, and research notes.

## Problem being solved
Many investors need a simple, organized way to monitor ETFs/stocks, compare performance, and capture research without jumping between tools.

## Users
- Personal investors
- Market research learners
- Portfolio builders
- AI-driven research copilots

## Core features
- Watchlist tracking for ETFs and stocks
- Basic market data display
- Simple price charts
- Asset-level notes and research
- Portfolio and performance comparison

## Tech stack
- Python
- FastAPI or Streamlit for dashboard UI
- SQLite or Postgres for lightweight storage
- Markdown for notes and documentation
- GitHub for version control

## Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/AI_Portfolio_Research_Copilot.git
   cd AI_Portfolio_Research_Copilot
   ```
2. Create a conda environment:
   ```bash
   conda create -n ai_portfolio_research python=3.11 -y
   ```
3. Activate the environment:
   ```bash
   conda activate ai_portfolio_research
   ```
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Current status
- Project scaffold created.
- Core design defined as a research dashboard, not a live trading bot.

## Next steps
- Build dashboard MVP.
- Add market data source.
- Show price charts.
- Add asset notes.
- Compare ETF performance.
- Prepare for backtesting later.
