from datetime import datetime


DISCLAIMER = (
    "Research-only packet for education, review, and paper-trading context. "
    "This is not financial advice, does not guarantee returns, does not place trades, "
    "and does not connect to broker APIs."
)


def _safe_get(data, key, default="N/A"):
    if isinstance(data, dict):
        value = data.get(key, default)
        return default if value in (None, "") else value
    return default


def _is_missing(value):
    return value in (None, "", "N/A")


def _fmt_number(value, suffix="", default="N/A"):
    try:
        if _is_missing(value):
            return default
        return f"{float(value):.2f}{suffix}"
    except (TypeError, ValueError):
        return default


def _yes_no(value):
    return "Yes" if value else "No"


def _bullet_list(items):
    if not items:
        return "- None noted."
    return "\n".join(f"- {item}" for item in items)


def _list_text(items):
    if not items:
        return "None"
    return ", ".join(str(item) for item in items)


def _source_note(data):
    if not isinstance(data, dict):
        return "N/A"
    source = data.get("source", "unknown")
    is_fallback = bool(data.get("is_fallback") or source == "mock")
    if is_fallback:
        reason = data.get("error") or "fallback/mock data was used"
        return f"{source} (fallback/mock: {reason})"
    return str(source)


def _news_source_note(news_context):
    if not isinstance(news_context, dict):
        return "N/A"
    headlines = news_context.get("recent_headlines") or []
    if headlines:
        return "Headlines available"
    return "Fallback/mock rule-based context; no recent headlines were available."


def _summarize_portfolio_comparison(portfolio_comparison):
    portfolio_comparison = portfolio_comparison or {}
    if portfolio_comparison.get("summary"):
        return portfolio_comparison.get("summary")
    if portfolio_comparison.get("benchmark_context"):
        return portfolio_comparison.get("benchmark_context")
    if portfolio_comparison.get("strategy_return_pct") is not None:
        return (
            f"Strategy return: {_fmt_number(portfolio_comparison.get('strategy_return_pct'), '%')}; "
            f"benchmark return: {_fmt_number(portfolio_comparison.get('benchmark_return_pct'), '%')}; "
            f"edge: {_fmt_number(portfolio_comparison.get('edge_vs_benchmark_pct'), '%')}."
        )
    return "No portfolio comparison summary available."


def build_research_packet_markdown(
    symbol,
    snapshot,
    risk,
    news_context,
    signal_data,
    backtest_results,
    portfolio_comparison,
    timestamp=None,
):
    """Build a clean Markdown packet from already-computed dashboard outputs."""
    symbol = str(symbol or "Unknown").upper()
    timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    snapshot = snapshot or {}
    risk = risk or {}
    news_context = news_context or {}
    signal_data = signal_data or {}
    backtest_results = backtest_results or {}

    signal_score = _safe_get(signal_data, "score", 0)
    signal_label = _safe_get(signal_data, "signal", "Unknown")
    news_sentiment = _safe_get(news_context, "market_sentiment", "Neutral")
    signal_reasons = signal_data.get("reasons", []) if isinstance(signal_data, dict) else []
    signal_risks = signal_data.get("risks", []) if isinstance(signal_data, dict) else []
    news_risks = news_context.get("risk_flags", []) if isinstance(news_context, dict) else []
    key_risks = []
    key_risks.extend(signal_risks[:4])
    key_risks.extend(news_risks[:4])
    if risk.get("volatility_pct") not in (None, "", 0, "N/A"):
        key_risks.append(f"Volatility is {_fmt_number(risk.get('volatility_pct'), '%')}.")
    if risk.get("max_drawdown_pct") not in (None, "", 0, "N/A"):
        key_risks.append(f"Recent max drawdown is {_fmt_number(risk.get('max_drawdown_pct'), '%')}.")
    if not key_risks:
        key_risks.append("No major dashboard risk flag is present, but research should still be reviewed.")

    signal_changes = _safe_get(
        backtest_results,
        "signal_changes",
        _safe_get(backtest_results, "number_of_signal_changes"),
    )

    bull_case = [
        f"Signal engine currently reads {signal_label} with score {signal_score}/100.",
        f"News sentiment is {news_sentiment}.",
    ]
    if not _is_missing(_safe_get(risk, "return_pct")):
        bull_case.append(f"Recent return context is {_fmt_number(risk.get('return_pct'), '%')}.")
    bull_case.extend(signal_reasons[:3])

    bear_case = []
    bear_case.extend(signal_risks[:3])
    bear_case.extend(news_risks[:3])
    if not bear_case:
        bear_case.append("No major dashboard risk flag is present, but the thesis still requires review.")

    uncertainty = [
        "Market data may be delayed, unofficial, stale, or incomplete depending on source quality.",
        "Backtests are historical and may not generalize to future regimes.",
        "News and catalyst context can change quickly and should be rechecked before any real-world decision.",
    ]

    lines = [
        f"# Research Packet: {symbol}",
        "",
        "## Asset",
        f"- Symbol: {symbol}",
        f"- Timestamp: {timestamp}",
        "",
        "## Market Snapshot",
        f"- Price: {_safe_get(snapshot, 'price')}",
        f"- Daily change: {_fmt_number(_safe_get(snapshot, 'change_pct'), '%')}",
        f"- Volume: {_safe_get(snapshot, 'volume')}",
        f"- Source: {_source_note(snapshot)}",
        f"- Fallback/mock data: {_yes_no(snapshot.get('is_fallback') or snapshot.get('source') == 'mock')}",
        "",
        "## Risk Metrics",
        f"- Return: {_fmt_number(_safe_get(risk, 'return_pct'), '%')}",
        f"- Volatility: {_fmt_number(_safe_get(risk, 'volatility_pct'), '%')}",
        f"- Max drawdown: {_fmt_number(_safe_get(risk, 'max_drawdown_pct'), '%')}",
        "",
        "## News Context",
        f"- Sentiment: {news_sentiment}",
        f"- Context source: {_news_source_note(news_context)}",
        f"- Headline summary: {_safe_get(news_context, 'headline_summary')}",
        f"- Event tags: {_list_text(news_context.get('event_tags', []) if isinstance(news_context, dict) else [])}",
        f"- Risk flags: {_list_text(news_risks)}",
        "",
        "## Signal Summary",
        f"- Signal: {signal_label}",
        f"- Score: {signal_score}/100",
        f"- Quant score: {_safe_get(signal_data, 'quant_score', 'N/A')}",
        f"- News score: {_safe_get(signal_data, 'news_score', 'N/A')}",
        "",
        "## Backtest Summary",
        f"- Strategy return: {_fmt_number(_safe_get(backtest_results, 'strategy_return_pct'), '%')}",
        f"- Buy-and-hold return: {_fmt_number(_safe_get(backtest_results, 'buy_and_hold_return_pct'), '%')}",
        f"- Max drawdown: {_fmt_number(_safe_get(backtest_results, 'max_drawdown_pct'), '%')}",
        f"- Signal changes: {signal_changes}",
        "",
        "## Portfolio Comparison Summary",
        _summarize_portfolio_comparison(portfolio_comparison),
        "",
        "## Bull Case",
        _bullet_list(bull_case),
        "",
        "## Bear Case",
        _bullet_list(bear_case),
        "",
        "## Key Risks",
        _bullet_list(key_risks),
        "",
        "## Uncertainty / Limitations",
        _bullet_list(uncertainty),
        "",
        "## Research-Only Disclaimer",
        DISCLAIMER,
        "",
    ]
    return "\n".join(lines)
