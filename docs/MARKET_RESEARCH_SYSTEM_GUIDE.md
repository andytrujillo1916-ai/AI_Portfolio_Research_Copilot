# AI Portfolio Research Copilot: Beginner Market Research Guide

## What This App Is

AI Portfolio Research Copilot is a research-only learning system. It helps you study assets, compare ideas against benchmarks, save predictions, review outcomes, and improve your research process over time.

It is not a trading bot.

- No broker APIs
- No live trading
- No order placement
- No futures contracts or margin workflows
- No guaranteed profit or guaranteed prediction claims
- Outputs are educational decision support, not financial advice

## How The System Works

### 1. Market Snapshot

The app starts with the selected asset. It loads price, daily change, volume, and price history. If live data is unavailable, the app falls back to mock data and marks it clearly. Mock data is useful for testing the app, but it should not be trusted for real market research.

### 2. Risk Metrics

The app calculates:

- Return: how much the asset moved over the selected period.
- Volatility: how jumpy the asset has been.
- Max drawdown: the worst peak-to-trough decline in the sample.

Drawdown matters because a strategy can make money on paper while still being emotionally or financially difficult to hold.

### 3. News And Catalyst Context

The news engine looks for recent headlines, sentiment, event tags, and risk flags. News is context, not proof. A bullish headline does not guarantee a bullish market reaction.

### 4. Signal Engine

The signal engine combines quant context, risk context, and news context into a research label such as Watch, Caution, or Avoid. These labels are not trade instructions. They are a way to organize evidence.

### 5. ETF Baselines

Every idea should be compared with simple ETF alternatives. A stock thesis is weaker if it cannot beat or justify its risk versus boring baselines such as SPY, QQQ, VTI, or SCHD.

The key question is:

> Is this idea actually better than a simple ETF basket after volatility and drawdown?

### 6. Backtesting And Walk-Forward Testing

Backtests show how simple rules would have behaved historically. They are useful, but easy to overfit. A backtest can look good because it accidentally matched the past. Walk-forward testing helps by checking whether a rule remains useful across different time windows.

Good research asks:

- Did this work outside the period where it was designed?
- Was the result better than buy-and-hold or ETF baselines?
- Did drawdown make the idea impractical?
- Is the sample large enough to trust?

### 7. Prediction Log

When you save a prediction, the app stores the signal, score, price, risk context, horizon, and later outcome. The point is not to prove you are always right. The point is to learn which setups deserve more or less trust.

The accuracy dashboard tracks:

- Hit rate
- False positive rate
- Average return after signal
- Average drawdown after signal
- Alpha versus ETF benchmark
- Best and worst holding window
- Results by signal, regime, horizon, and asset class
- Sample confidence, including "Not enough evidence"

### 8. Crash Watch

Crash Watch is hypothesis testing. If you think the market may crash, the app checks broad proxies such as SPY, QQQ, IWM, VTI, SCHD, TLT, HYG, GLD, and sometimes ^VIX.

It looks for:

- Trend deterioration
- Volatility expansion
- Drawdowns
- Weak risk-on breadth
- Defensive rotation
- High-yield credit weakness
- Volatility proxy pressure

The output is only a posture:

- Normal
- Elevated
- Stress
- Needs More Data

This is not a crash prediction. A feeling that the market has gone up too much is a hypothesis, not statistical evidence.

### 9. Adaptive Learning

The adaptive learning engine reviews saved predictions and research runs. It summarizes what worked, what failed, and which scoring weights might deserve review.

It never changes code by itself. It never places trades. It only suggests small, bounded, human-reviewable adjustments.

### 10. Swing Trading And Futures

Swing trading means holding for days or weeks rather than minutes or years. The app can help research swing ideas by checking trend, volatility, drawdown, catalysts, ETF baselines, and prior signal outcomes.

Futures are different. Futures involve leverage, margin, contract specifications, expiration, and fast losses. This app keeps futures proxy-only. That means it may study broad market proxies, but it does not add futures contracts, margin, leverage, or execution.

## Research Workflow Checklist

1. Form a thesis in plain English.
2. Check whether the data is real or fallback/mock.
3. Compare the asset to ETF baselines.
4. Review return, volatility, and max drawdown.
5. Check market regime and Crash Watch posture.
6. Read news context and identify catalyst risk.
7. Run backtests and walk-forward checks.
8. Save a prediction before the outcome is known.
9. Review the prediction after the market moves.
10. Update the thesis only after evidence accumulates.

## Best-Practice Research Principles

- Diversification and asset allocation matter because concentrated ideas can be wrong.
- Market timing is hard; missing a few strong days can damage results.
- Backtest overfitting is dangerous; impressive historical results can be false discoveries.
- Trend-following has research support, but still needs risk controls and out-of-sample testing.
- Futures require special caution because leverage can amplify losses quickly.

Useful references:

- FINRA, Market Timing: https://www.finra.org/investors/insights/market-timing
- SEC, Asset Allocation: https://www.sec.gov/about/reports-publications/investorpubsassetallocationhtm
- Bailey and Lopez de Prado, Backtest Overfitting: https://academic.oup.com/jrssig/article/18/6/22/7038278
- Two Centuries of Trend Following: https://arxiv.org/abs/1404.3274
- CFTC, Futures Market Basics: https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/FuturesMarketBasics/index.htm

## Bottom Line

The app should help you become a better researcher, not a more impulsive trader. The best use is to write down predictions, compare them to simple alternatives, measure what happened, and slowly improve your process with evidence.
