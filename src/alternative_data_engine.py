def generate_alternative_data_context(symbol):
    """Create a rule-based alternative data context for research support only.

    V1 uses placeholder logic only. It does not call paid APIs or claim that
    alternative data creates a guaranteed edge.
    """
    symbol = str(symbol or "").upper()

    future_data_sources = {
        "quiver_quantitative": "Future optional source for congressional, lobbying, and institutional-style datasets.",
        "sec_disclosures": "Future optional source for SEC Form 4 and ownership disclosures.",
        "capitol_trades": "Future optional source for congressional transaction disclosures.",
        "insider_transactions": "Future optional source for director/officer transaction context.",
        "institutional_filings": "Future optional source for 13F and fund ownership changes.",
        "unusual_options_activity": "Future optional source for options flow research context.",
    }

    positive_signals = []
    risk_flags = []

    politician_trade_signal = "No tracked signal"
    insider_activity_signal = "No tracked signal"
    institutional_attention_signal = "No tracked signal"
    score = 50

    mega_cap_symbols = {"AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA"}
    defense_policy_symbols = {"LMT", "RTX", "NOC", "GD", "BA"}
    financial_symbols = {"JPM", "BAC", "GS", "MS", "WFC", "BLK"}
    high_attention_etfs = {"SPY", "QQQ", "VTI", "VOO", "IWM"}

    if symbol in mega_cap_symbols:
        institutional_attention_signal = "High institutional/news attention"
        positive_signals.append(
            "Large-cap symbol likely has broad institutional and media coverage."
        )
        score += 6

    if symbol in defense_policy_symbols:
        politician_trade_signal = "Policy-sensitive watch"
        positive_signals.append(
            "Policy-sensitive sector can be worth monitoring for delayed congressional disclosures."
        )
        risk_flags.append(
            "Policy headlines can move quickly while disclosure data may arrive late."
        )
        score += 3

    if symbol in financial_symbols:
        institutional_attention_signal = "Institutional filing watch"
        positive_signals.append(
            "Financial-sector ownership changes may be useful future 13F context."
        )
        score += 2

    if symbol in high_attention_etfs:
        institutional_attention_signal = "Benchmark-level attention"
        positive_signals.append(
            "Broad ETF can serve as a comparison baseline for institutional/news attention."
        )
        score += 2

    if not positive_signals:
        risk_flags.append(
            "No strong placeholder alternative-data signal is available for this symbol."
        )
        score -= 3

    if symbol.endswith("Q") or symbol in {"GME", "AMC", "CVNA"}:
        insider_activity_signal = "Speculative attention risk"
        risk_flags.append(
            "Speculative or distressed attention can create noisy alternative-data readings."
        )
        score -= 6
    else:
        insider_activity_signal = "Neutral / unverified"

    data_limitations = [
        "Congressional and politician trade disclosures are delayed.",
        "Disclosures may be incomplete, amended, or filed late.",
        "Correlation does not imply causation.",
        "Alternative data is not a guaranteed edge.",
        "Use this only as supporting evidence, not as the primary signal.",
        "V1 uses placeholder logic and does not call paid APIs.",
    ]

    if politician_trade_signal == "No tracked signal":
        politician_trade_signal = "Neutral / delayed-data watch"

    score = max(0, min(100, int(round(score))))
    if score >= 60:
        summary = (
            f"{symbol} has a modest supportive alternative-data context, but it should only "
            "support the main research thesis."
        )
    elif score <= 40:
        summary = (
            f"{symbol} has weak or noisy alternative-data context. Treat it as a caution flag, "
            "not a standalone decision."
        )
    else:
        summary = (
            f"{symbol} has a neutral alternative-data context with delayed and incomplete inputs."
        )

    return {
        "politician_trade_signal": politician_trade_signal,
        "insider_activity_signal": insider_activity_signal,
        "institutional_attention_signal": institutional_attention_signal,
        "alternative_data_score": score,
        "positive_signals": positive_signals,
        "risk_flags": risk_flags,
        "data_limitations": data_limitations,
        "future_data_sources": future_data_sources,
        "summary": summary,
    }
