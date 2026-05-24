import pandas as pd

from market_data import get_price_history


def _normalize_allocations(selected_assets, allocations):
    if not selected_assets:
        return {}

    if isinstance(allocations, dict):
        asset_allocations = {asset: float(allocations.get(asset, 0.0)) for asset in selected_assets}
    else:
        asset_allocations = {}
        for index, asset in enumerate(selected_assets):
            asset_allocations[asset] = float(allocations[index]) if index < len(allocations) else 0.0

    total = sum(asset_allocations.values())
    if total <= 0:
        equal_weight = 100 / len(selected_assets)
        return {asset: equal_weight for asset in selected_assets}

    if abs(total - 100) < 1e-9:
        return asset_allocations

    return {asset: (asset_allocations[asset] / total) * 100 for asset in selected_assets}


def simulate_portfolio(selected_assets, allocations, period="6mo"):
    """Simulate a simple portfolio using normalized asset returns."""
    assets = list(selected_assets or [])
    if not assets:
        return {
            "portfolio_equity_curve": pd.DataFrame(columns=["Date", "Portfolio"]),
            "total_return_pct": 0.0,
            "best_asset": "N/A",
            "worst_asset": "N/A",
        }

    normalized_allocations = _normalize_allocations(assets, allocations)
    asset_series = {}
    asset_returns = {}

    for asset in assets:
        price_data = get_price_history(asset, period=period)
        data = price_data.get("data") if isinstance(price_data, dict) else price_data
        if data is None:
            continue

        if hasattr(data, "set_index"):
            df = data.copy()
        else:
            df = pd.DataFrame(data)

        if "Date" not in df.columns or "Close" not in df.columns:
            continue

        df = df.dropna(subset=["Close"]).copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        if df.empty or len(df) < 2:
            continue

        df["normalized"] = (df["Close"] / df["Close"].iloc[0]) * 100
        asset_series[asset] = df[["Date", "normalized"]]
        asset_returns[asset] = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100

    if not asset_series:
        return {
            "portfolio_equity_curve": pd.DataFrame(columns=["Date", "Portfolio"]),
            "total_return_pct": 0.0,
            "best_asset": "N/A",
            "worst_asset": "N/A",
        }

    merged = None
    for asset, asset_df in asset_series.items():
        weight = normalized_allocations.get(asset, 0.0)
        asset_df = asset_df.copy()
        asset_df[f"_{asset}"] = asset_df["normalized"] * (weight / 100)
        if merged is None:
            merged = asset_df[["Date", f"_{asset}"]]
        else:
            merged = merged.merge(asset_df[["Date", f"_{asset}"]], on="Date", how="inner")

    if merged is None or merged.empty:
        return {
            "portfolio_equity_curve": pd.DataFrame(columns=["Date", "Portfolio"]),
            "total_return_pct": 0.0,
            "best_asset": "N/A",
            "worst_asset": "N/A",
        }

    portfolio_equity_curve = merged.copy()
    portfolio_equity_curve["Portfolio"] = portfolio_equity_curve.drop(columns=["Date"]).sum(axis=1)
    portfolio_equity_curve = portfolio_equity_curve[["Date", "Portfolio"]]

    total_return_pct = round(float(portfolio_equity_curve["Portfolio"].iloc[-1] - 100), 2)

    best_asset = max(asset_returns, key=asset_returns.get) if asset_returns else "N/A"
    worst_asset = min(asset_returns, key=asset_returns.get) if asset_returns else "N/A"

    return {
        "portfolio_equity_curve": portfolio_equity_curve,
        "total_return_pct": total_return_pct,
        "best_asset": best_asset,
        "worst_asset": worst_asset,
    }
