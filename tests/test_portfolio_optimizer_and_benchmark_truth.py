from benchmark_engine import compare_to_benchmarks
from portfolio_optimizer import optimize_portfolio


def test_optimize_portfolio_returns_allocations():
    ranked_assets = [
        {
            "symbol": "AAPL",
            "conviction": 78,
            "volatility_pct": 20,
            "max_drawdown_pct": -10,
            "regime": "Bull Trend",
        },
        {
            "symbol": "MSFT",
            "conviction": 68,
            "volatility_pct": 16,
            "max_drawdown_pct": -8,
            "regime": "Recovery",
        },
    ]
    result = optimize_portfolio(ranked_assets, research_mode="Balanced")
    assert "recommended_allocations" in result
    assert "cash_allocation_pct" in result
    assert isinstance(result["recommended_allocations"], list)
    if result["recommended_allocations"]:
        assert result["recommended_allocations"][0]["allocation_pct"] >= 0


def test_compare_to_benchmarks_returns_verdict():
    portfolio_returns = {
        "total_unrealized_pnl_pct": 6.0,
        "volatility_pct": 14.0,
        "drawdown_pct": -7.0,
    }
    benchmark_data = {
        "benchmarks": [
            {"benchmark": "SPY", "return_pct": 4.0, "volatility_pct": 12.0, "max_drawdown_pct": -8.0, "sharpe": 0.33},
            {"benchmark": "VTI", "return_pct": 4.2, "volatility_pct": 12.5, "max_drawdown_pct": -8.3, "sharpe": 0.34},
            {"benchmark": "QQQ", "return_pct": 5.1, "volatility_pct": 16.0, "max_drawdown_pct": -10.0, "sharpe": 0.32},
            {"benchmark": "60/40 basket", "return_pct": 3.0, "volatility_pct": 8.0, "max_drawdown_pct": -5.0, "sharpe": 0.38},
        ]
    }
    result = compare_to_benchmarks(portfolio_returns, benchmark_data)
    assert result["best_benchmark"] in {"SPY", "VTI", "QQQ", "60/40 basket", "Equal Weight Basket"}
    assert "verdict" in result
