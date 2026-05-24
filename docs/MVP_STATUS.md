# MVP Status

## Current features

- Market snapshot, price chart, and asset comparison
- Research notes and research journal
- News intelligence with sentiment and event tags
- Signal engine with quant + news-aware scoring
- Prediction log and prediction evaluation
- Backtesting and Strategy Lab
- Walk-Forward Testing
- Portfolio Simulator

## What works

- The dashboard launches and renders the main sections
- Market data can come from yfinance or fallback mock data
- Strategy Lab compares multiple strategies on the current price history
- Walk-Forward Testing produces repeated window summaries
- Portfolio Simulator generates a normalized portfolio equity curve
- Prediction storage and evaluation are available for research tracking

## Known limitations

- Some data paths still rely on fallback/mock data when yfinance is unavailable
- The signal engine is rule-based rather than a full statistical model
- The portfolio simulator is simple and does not include transaction costs
- The backtesting helpers are intentionally lightweight and educational
- The UI is research-focused and not yet a polished production dashboard

## What is mock or rule-based

- Research Agent summaries are rule-based
- News fallback behavior is rule-based
- Mock data is used when live yfinance data is unavailable
- Signal scoring is heuristic and designed for learning

## What uses real data

- yfinance market history when available
- yfinance news headlines when available
- Real-time snapshots when available

## Next planned features

- Improve documentation and quality checks
- Add more portfolio comparison views
- Add cleaner export and notes workflows
- Add stronger validation around fallback data
- Refine the readability of dashboards and charts

## Safety note

This project is research-only. It is **not** financial advice, and it does not execute trades or connect to broker APIs.
