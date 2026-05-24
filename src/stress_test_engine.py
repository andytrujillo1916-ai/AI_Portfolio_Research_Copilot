def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _risk_label(pnl_pct):
    drawdown = abs(pnl_pct)
    if drawdown >= 15:
        return "High"
    if drawdown >= 7:
        return "Medium"
    return "Low"


def run_stress_tests(paper_positions):
    """Run simple research-only stress tests on paper portfolio positions."""
    positions = {}
    if isinstance(paper_positions, dict):
        positions = paper_positions.get("positions", {}) or {}

    if not positions:
        return {
            "stress_tests": [],
            "summary": "No open paper positions found. Add paper trades to run stress tests.",
        }

    base_value = sum(
        _safe_float(item.get("market_value", 0.0)) for item in positions.values()
    )
    if base_value <= 0:
        return {
            "stress_tests": [],
            "summary": "Paper positions are available but market value is zero, so stress tests are not meaningful yet.",
        }

    largest_position = max(
        (_safe_float(item.get("market_value", 0.0)) for item in positions.values()),
        default=0.0,
    )
    concentration_pct = (largest_position / base_value) * 100 if base_value > 0 else 0.0

    scenario_shocks = [
        ("Market -5%", -5.0),
        ("Market -10%", -10.0),
        ("Market -20%", -20.0),
        ("Selected holdings +10%", 10.0),
        ("High volatility shock", -15.0),
        ("Concentration risk shock", -12.0 if concentration_pct >= 40 else -8.0),
    ]

    stress_tests = []
    for scenario_name, shock_pct in scenario_shocks:
        portfolio_value_after_shock = base_value * (1 + shock_pct / 100)
        estimated_pnl = portfolio_value_after_shock - base_value
        estimated_pnl_pct = (estimated_pnl / base_value) * 100 if base_value > 0 else 0.0
        risk_level = _risk_label(estimated_pnl_pct)

        stress_tests.append(
            {
                "scenario": scenario_name,
                "portfolio_value_after_shock": round(portfolio_value_after_shock, 2),
                "estimated_pnl": round(estimated_pnl, 2),
                "estimated_pnl_pct": round(estimated_pnl_pct, 2),
                "risk_level": risk_level,
            }
        )

    summary = (
        f"Stress tests use simple portfolio-wide shocks on paper positions only. "
        f"Current concentration in largest holding is {concentration_pct:.2f}%."
    )

    return {
        "stress_tests": stress_tests,
        "summary": summary,
    }
