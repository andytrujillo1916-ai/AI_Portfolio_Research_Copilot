# AI Portfolio Research Copilot

**⚠️ RESEARCH ONLY — Not financial advice. No trading execution. No broker APIs.**

## Project Purpose

Build a **research-only investment learning dashboard** that combines market intelligence, signal generation, and prediction tracking into a single interface. This tool helps students and researchers understand how signals perform over time without executing trades.

## Problem Being Solved

Investors and researchers need a simple, organized way to:
- Monitor market data for stocks and ETFs
- Generate and track research signals
- Compare strategies against buy-and-hold
- Learn from past predictions
- Capture research notes in one place

All without jumping between tools or placing actual trades.

## Users

- 📚 Market research learners
- 🎓 Students building portfolio theory knowledge
- 📊 Individual investors analyzing strategies
- 🤖 AI-assisted researchers testing hypotheses

## Current Features

### Core Dashboard
- **Market Snapshot** — Real-time price, volume, position value (yfinance with fallback)
- **Price Chart** — Historical performance with volatility & drawdown metrics
- **Backtesting** — SMA(20) strategy vs. buy-and-hold, equity curve visualization

### Research Tools
- **Research Notes** — Capture thoughts and observations
- **Research Agent** — Rule-based bull/bear case analysis
- **Signal Engine** — Composite quant + news-aware signal scoring (0–100)
- **News Intelligence** — Real yfinance headlines, sentiment, event tags, risk flags

### Learning & Tracking
- **Prediction Log** — Save signals with reasoning
- **Prediction Evaluation** — Measure signal accuracy over time (hit rate, realized return, Strong Hit/Partial Hit/Miss)
- **Research Journal** — Long-form thesis with entry/target/time horizon

### Portfolio Tools
- **Asset Comparison** — Side-by-side performance across watchlist
- **Multiple assets** — Built-in watchlist (e.g., AAPL, MSFT, GOOGL, SPY, QQQ)

## Tech Stack

- **Frontend:** Streamlit (Python UI framework)
- **Data:** Pandas, yfinance (market data)
- **Storage:** CSV (predictions, research journal, watchlist)
- **Environment:** Conda (Python 3.11+)
- **Version Control:** Git / GitHub

## Safety & Scope

### ✅ In Scope (Research-Only)
- Signal generation and backtesting
- Prediction tracking and evaluation
- Market data visualization
- News intelligence and sentiment
- Portfolio performance comparison
- Research notes and theses

### ❌ Out of Scope (Never)
- **Live trading execution**
- **Broker APIs** (real or simulated)
- **Account management**
- **Auto-trading / algorithmic trading**
- **Financial advice or guarantees**

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/AI_Portfolio_Research_Copilot.git
cd AI_Portfolio_Research_Copilot
```

### 2. Create and Activate Conda Environment

```bash
conda create -n ai_portfolio_research python=3.11 -y
conda activate ai_portfolio_research
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
cd src
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

---

## Quick Tour

1. **Select an asset** from the sidebar (default: AAPL)
2. **Choose a time period** (5d, 1mo, 3mo, 6mo, 1y)
3. **View market data** — snapshot, price chart, backtesting results
4. **Read news** — recent headlines with sentiment and event tags
5. **Generate a signal** — quant + news composite score
6. **Save a prediction** — log your hypothesis with time horizon
7. **Check evaluation** — see how past signals performed
8. **Add research notes** — capture thesis and risk analysis
9. **View journal** — long-form thesis tracking

---

## Key Concepts

### Signal Scoring
- **Quant Score** (0–100): Price momentum, volatility, drawdown
- **News Score**: Sentiment (±5), event tags (+2), risk flags (-3)
- **Final Score**: Composite of both
- **Signal Label**: "Strong Watch", "Watch", "Caution", "Avoid"

### Prediction Evaluation
- **Correct Direction**: Did the price move as the signal suggested?
- **Hit Rate**: % of predictions with correct direction
- **Realized Return**: (Current Price - Entry Price) / Entry Price * 100
- **Labels**: "Strong Hit" (≥5% correct), "Partial Hit" (correct, <5%), "Miss"

### Backtesting
- **Strategy**: Go long when Close > SMA(20), exit when Close ≤ SMA(20)
- **Baseline**: Buy-and-hold the entire period
- **Equity Curve**: Both strategies visualized starting at 100

---

## Documentation

- **[docs/current_architecture.md](docs/current_architecture.md)** — System design and module reference
- **[docs/development_workflow.md](docs/development_workflow.md)** — How to run, develop, and contribute safely
- **[docs/agent_workflow.md](docs/agent_workflow.md)** — AI copilot guidelines

---

## Development

### Adding a Feature

1. Create or modify a module in `src/`
2. Test in isolation: `python -c "from module import function; print(function(...))"`
3. Test in the full app by running `streamlit run src/app.py`
4. Commit with a clear message:
   ```bash
   git add src/module.py docs/current_architecture.md
   git commit -m "Feature: add X component; docs: update architecture"
   git push origin feature/my-feature
   ```

### Testing Data

The app includes a fallback "mock" data source. If yfinance is unavailable or rate-limited, the dashboard will still work with synthetic data and show "Using fallback market data" in the sidebar.

---

## License

MIT (or specify your license)

---

## Disclaimer

**This tool is for research and learning purposes only.**

- Not financial advice
- No trading execution
- No guaranteed predictions
- Past performance ≠ future results
- Always do your own due diligence
- Consult a financial advisor for investment decisions

---

## Contributing

See [docs/development_workflow.md](docs/development_workflow.md) for guidelines on:
- Setting up your environment
- Creating branches and commits
- Safe Copilot usage
- Code review checklist

---

## Support

For questions or issues:
1. Check [docs/current_architecture.md](docs/current_architecture.md) for system overview
2. Check [docs/development_workflow.md](docs/development_workflow.md) for setup/troubleshooting
3. Open a GitHub issue with a clear description

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
