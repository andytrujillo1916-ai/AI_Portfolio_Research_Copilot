from market_data import get_price_history, get_risk_metrics, get_sector_watchlist


def _clamp(value, low, high):
    return max(low, min(high, value))


def _weights_for_mode(research_mode):
    if research_mode == "Conservative":
        return {"return_weight": 0.4, "vol_weight": 0.3, "drawdown_weight": 0.3}
    if research_mode == "Aggressive":
        return {"return_weight": 0.6, "vol_weight": 0.2, "drawdown_weight": 0.2}
    return {"return_weight": 0.5, "vol_weight": 0.25, "drawdown_weight": 0.25}


def analyze_sector_rotation(period="3mo", research_mode="Balanced"):
    """Analyze sector ETF rotation with simple research-only scoring."""
    sectors = get_sector_watchlist()
    weights = _weights_for_mode(research_mode)
    ranked_sectors = []

    for sector, ticker in sectors.items():
        try:
            price_data = get_price_history(ticker, period=period)
            risk_input = price_data.get("data") if isinstance(price_data, dict) else price_data
            risk = get_risk_metrics(risk_input)

            return_pct = float(risk.get("return_pct", 0.0))
            volatility_pct = float(risk.get("volatility_pct", 0.0))
            max_drawdown_pct = float(risk.get("max_drawdown_pct", 0.0))

            return_score = _clamp(return_pct + 50, 0, 100)
            volatility_score = _clamp(100 - (volatility_pct * 2), 0, 100)
            drawdown_score = _clamp(100 - (abs(max_drawdown_pct) * 3), 0, 100)

            sector_score = (
                return_score * weights["return_weight"]
                + volatility_score * weights["vol_weight"]
                + drawdown_score * weights["drawdown_weight"]
            )
            sector_score = round(_clamp(sector_score, 0, 100), 2)

            summary = (
                f"Return {return_pct:+.2f}%, volatility {volatility_pct:.2f}%, "
                f"drawdown {max_drawdown_pct:.2f}%."
            )

            ranked_sectors.append(
                {
                    "sector": sector,
                    "ticker": ticker,
                    "return_pct": round(return_pct, 2),
                    "volatility_pct": round(volatility_pct, 2),
                    "max_drawdown_pct": round(max_drawdown_pct, 2),
                    "sector_score": sector_score,
                    "summary": summary,
                }
            )
        except Exception:
            # Continue with remaining sectors if one fails.
            continue

    ranked_sectors.sort(key=lambda row: row.get("sector_score", 0), reverse=True)
    strongest = ranked_sectors[0] if ranked_sectors else {}
    weakest = ranked_sectors[-1] if ranked_sectors else {}

    if not ranked_sectors:
        rotation_summary = "No sector rotation results were available for this run."
    else:
        rotation_summary = (
            f"{research_mode} mode sector ranking compares return with volatility and drawdown controls. "
            "Use this as research context, not a certainty signal."
        )

    return {
        "ranked_sectors": ranked_sectors,
        "strongest_sector": strongest,
        "weakest_sector": weakest,
        "rotation_summary": rotation_summary,
    }
