# AI Portfolio Research Copilot – Current Architecture

## Overview
The Copilot is a Streamlit-based research dashboard that combines market data, signal generation, news intelligence, and prediction tracking into a single research interface. It is **research-only** — no trading execution, no broker APIs, no live account management.

## Core Modules

### `app.py`
**Role:** Main Streamlit controller and page composition.

- Loads market data for the selected asset
- Renders all dashboard sections in sequence
- Manages sidebar asset/period selection
- Shows system status (data source, current asset, period)

**Key calls:**
- `get_watchlist()` → asset list
- `get_market_snapshot()` → price + change_pct
- `get_price_history()` → OHLC data
- Various `render_*()` UI functions

---

### `ui_sections.py`
**Role:** UI rendering and form handling.

**Major functions:**
- `render_market_snapshot()` — price, volume, position value
- `render_price_chart()` — line chart and risk metrics
- `render_backtest_section()` — backtesting results + equity curve
- `render_asset_comparison()` — multi-asset comparison chart
- `render_research_notes()` — user-entered notes display
- `render_research_agent()` — rule-based bull/bear cases
- `render_signal_engine()` — quant + news composite signal with save-to-log form
- `render_news_intelligence()` — recent headlines, sentiment, event tags, risk flags
- `render_prediction_log()` — stored signals with outcomes
- `render_prediction_evaluation()` — hit rate, average return, recent evaluated signals
- `render_research_journal()` — thesis form and journal history
- `render_roadmap()` — project vision section

**Imports from:**
- `market_data` → market snapshots, risk metrics, comparisons
- `prediction_log` → prediction storage and evaluation
- `research_agent` → bull/bear summary
- `signal_engine` → signal scoring
- `news_engine` → news context
- `backtester` → backtest results
- `journal` → thesis storage

---

### `market_data.py`
**Role:** Data layer for market information.

**Functions:**
- `get_market_snapshot(symbol)` — current price, change %, volume (yfinance or fallback)
- `get_price_history(symbol, period)` — OHLC history for charting
- `get_watchlist()` — list of watched symbols
- `get_risk_metrics(price_data)` — return %, volatility, max drawdown
- `get_asset_comparison(symbols, period, normalize)` — multi-asset comparison

**Fallback behavior:** When yfinance is unavailable, serves mock data with `"source": "mock"` flag.

---

### `research_agent.py`
**Role:** Rule-based decision-support summary.

**Function:**
- `generate_research_summary(symbol, snapshot, risk, notes)` → dict with:
  - `bull_case` — positive reasoning
  - `bear_case` — negative reasoning
  - `risk_summary` — composite risk label
  - `learning_questions` — research prompts
  - `overall_stance` — "Explore", "Monitor", "Caution", etc.

**Logic:** Simple if/else rules on price, volatility, and user notes.

---

### `signal_engine.py`
**Role:** Quantitative and news-aware signal scoring.

**Function:**
- `generate_signal(symbol, snapshot, risk, news_context=None)` → dict with:
  - `signal` — "Strong Watch", "Watch", "Caution", "Avoid"
  - `score` — final 0–100 score
  - `quant_score` — price/volatility/drawdown component
  - `news_score` — sentiment + event tags + risk flags
  - `reasons` — list of positive reasons
  - `risks` — list of risk items

**Scoring:**
- **Quant:** ±change, return %, volatility, drawdown bounds
- **News:** +5 for Bullish, 0 for Neutral, -5 for Bearish; +2 per positive tag; -3 per risk flag

---

### `news_engine.py`
**Role:** Event-aware research context using yfinance news.

**Functions:**
- `get_recent_news(symbol, limit=5)` — fetch yfinance.Ticker(symbol).news, parse fields robustly
- `generate_news_context(symbol)` → dict with:
  - `headline_summary` — top 3 headlines as bullets
  - `market_sentiment` — "Bullish", "Neutral", "Bearish" (rule-based on keywords)
  - `event_tags` — ["earnings", "ai", "regulation", ...] (keyword matches)
  - `risk_flags` — ["Mention of lawsuit", ...] (risk keywords)
  - `recent_headlines` — list of parsed news items (title, publisher, link, time)

**Fallback:** When no news, uses mock rule-based context by symbol name.

---

### `prediction_log.py`
**Role:** Persistent signal storage and evaluation.

**Functions:**
- `load_predictions()` — read all entries from CSV
- `add_prediction(...)` — append new signal to CSV
- `update_prediction_outcome(index, outcome, lesson)` — update status
- `evaluate_all_predictions(symbol, current_price)` → dict with:
  - `total_predictions` — count
  - `hit_rate` — % correct
  - `average_return` — avg realized %
  - `best_trade`, `worst_trade` — extremes
  - `recent_predictions` — latest 5 evaluated

**Storage:** `data/prediction_log.csv` with columns:
- date, symbol, signal, score, reasons, risks, price_at_signal, time_horizon, outcome, lesson

---

### `evaluation_engine.py`
**Role:** Evaluate stored predictions against current market prices.

**Function:**
- `evaluate_prediction(prediction, current_price)` → dict with:
  - `realized_return_pct` — (current - entry) / entry * 100
  - `correct_direction` — bool (signal direction matched price movement)
  - `evaluation_label` — "Strong Hit", "Partial Hit", "Miss"

**Logic:**
- "Strong Watch" / "Watch" → positive return = hit
- "Caution" / "Avoid" → negative/flat return = hit
- abs(return) >= 5% → "Strong Hit", else "Partial Hit"

---

### `backtester.py`
**Role:** Simple price-action strategy testing.

**Function:**
- `run_simple_backtest(price_data)` → dict with:
  - `buy_and_hold_return_pct` — baseline return
  - `strategy_return_pct` — SMA(20) crossover return
  - `max_drawdown_pct` — worst peak-to-trough
  - `number_of_signal_changes` — signal toggles
  - `equity_curve` — DataFrame (Date, Buy and Hold, Strategy) with both starting at 100

**Strategy:** Long when Close > SMA(20), out when Close ≤ SMA(20).

---

### `journal.py`
**Role:** Research thesis capture and storage.

**Functions:**
- `add_journal_entry(...)` — save thesis with symbol, signal, confidence, risk notes, entry/target, time horizon
- `load_journal()` — read all thesis entries

**Storage:** `data/research_journal.csv`

---

## Data Flow

```
app.py
  ├─ get_market_snapshot → market_data
  ├─ get_price_history → market_data
  ├─ render_market_snapshot → ui_sections
  ├─ render_price_chart → ui_sections (calls get_risk_metrics)
  ├─ render_backtest_section → ui_sections → backtester
  ├─ render_news_intelligence → ui_sections → news_engine → get_recent_news
  ├─ render_research_agent → ui_sections → research_agent
  ├─ render_signal_engine → ui_sections → signal_engine + news_engine + prediction_log
  ├─ render_prediction_log → ui_sections → prediction_log
  ├─ render_prediction_evaluation → ui_sections → prediction_log → evaluation_engine
  └─ render_research_journal → ui_sections → journal
```

---

## Safety & Scope

✅ **In scope:**
- Research context and signal generation
- Prediction tracking and learning
- Market data visualization
- News intelligence
- Historical backtesting

❌ **Out of scope:**
- Live trading execution
- Broker APIs (real or mock)
- Account management
- Auto-trading / algorithmic trading
- Financial advice

---

## Testing

Each module can be tested independently:

```bash
# Test signal engine
python -c "from signal_engine import generate_signal; print(generate_signal('AAPL', {...}, {...}))"

# Test news engine
python -c "from news_engine import get_recent_news; print(get_recent_news('AAPL'))"

# Test evaluation
python -c "from evaluation_engine import evaluate_prediction; print(evaluate_prediction({...}, 150.00))"
```

---

## Common Tasks

### Add a new render function
1. Create function in `ui_sections.py`
2. Import dependencies at top of file
3. Call from `app.py` in desired order
4. Test by running `streamlit run src/app.py`

### Add a new data source
1. Add function to `market_data.py`
2. Handle fallback gracefully
3. Return consistent dict/DataFrame format
4. Import and call in `app.py` or relevant UI function

### Modify signal scoring
1. Edit `generate_signal()` in `signal_engine.py`
2. Adjust quant_score or news_score weights
3. Test with `generate_signal(...)` directly
4. Check UI updates in `render_signal_engine()`

---

## Dependencies

See `requirements.txt`:
- `streamlit` — UI framework
- `pandas` — data manipulation
- `yfinance` — market data
- `python-dateutil` — date parsing

