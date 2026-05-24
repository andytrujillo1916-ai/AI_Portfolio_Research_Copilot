from datetime import datetime
from pathlib import Path

from db_service import load_paper_trades as db_load_paper_trades
from db_service import save_paper_trade as db_save_paper_trade


def _ensure_file():
    data_path = Path(__file__).resolve().parent.parent / "data"
    data_path.mkdir(parents=True, exist_ok=True)


def load_paper_trades():
    """Load paper trades from SQLite."""
    _ensure_file()
    rows = db_load_paper_trades()
    normalized = []
    for row in rows:
        normalized.append(
            {
                "date": str(row.get("date", row.get("created_at", ""))),
                "symbol": str(row.get("symbol", "")),
                "action": str(row.get("action", "")),
                "quantity": str(row.get("quantity", row.get("size_pct", ""))),
                "price": str(row.get("price", row.get("entry_price", ""))),
                "reason": str(row.get("reason", "")),
                "status": str(row.get("status", "open")),
            }
        )
    return normalized


def add_paper_trade(symbol, action, quantity, price, reason):
    """Append a simulated trade to SQLite paper-trading storage."""
    _ensure_file()
    trade = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "action": action,
        "quantity": str(quantity),
        "price": str(price),
        "reason": reason,
        "status": "open",
    }
    db_save_paper_trade(
        symbol=symbol,
        entry_price=price,
        size_pct=quantity,
        action=action,
        status="open",
        created_at=trade["date"],
        quantity=quantity,
        price=price,
        reason=reason,
        date=trade["date"],
    )
    return trade


def calculate_paper_positions(current_prices_by_symbol):
    """Calculate open paper-trading positions from saved trades."""
    trades = load_paper_trades()
    positions = {}
    total_shares = 0
    total_cost = 0.0
    total_market_value = 0.0
    total_unrealized_pnl = 0.0

    for trade in trades:
        if trade.get("status") != "open":
            continue

        symbol = trade.get("symbol")
        action = trade.get("action", "").lower()
        quantity = float(trade.get("quantity", 0) or 0)
        price = float(trade.get("price", 0) or 0)

        if symbol not in positions:
            positions[symbol] = {
                "shares": 0.0,
                "average_cost": 0.0,
            }

        if action == "buy":
            positions[symbol]["shares"] += quantity
            positions[symbol]["average_cost"] = (
                (positions[symbol]["average_cost"] * (positions[symbol]["shares"] - quantity))
                + (price * quantity)
            ) / positions[symbol]["shares"]
        elif action == "sell":
            positions[symbol]["shares"] = max(positions[symbol]["shares"] - quantity, 0.0)

        total_shares += quantity if action == "buy" else -quantity

    summary = {}
    for symbol, position in positions.items():
        current_price = float(current_prices_by_symbol.get(symbol, 0) or 0)
        shares = position["shares"]
        if shares <= 0:
            continue

        average_cost = position["average_cost"]
        market_value = shares * current_price
        unrealized_pnl = market_value - (shares * average_cost)
        unrealized_pnl_pct = (unrealized_pnl / (shares * average_cost) * 100) if average_cost else 0.0

        total_cost += shares * average_cost
        total_market_value += market_value
        total_unrealized_pnl += unrealized_pnl

        summary[symbol] = {
            "shares": shares,
            "average_cost": round(average_cost, 2),
            "current_price": round(current_price, 2),
            "market_value": round(market_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
        }

    total_shares = sum(position["shares"] for position in summary.values())
    average_cost = round(total_cost / total_shares, 2) if total_shares else 0.0

    return {
        "positions": summary,
        "total_shares": total_shares,
        "average_cost": average_cost,
        "market_value": round(total_market_value, 2),
        "unrealized_pnl": round(total_unrealized_pnl, 2),
        "unrealized_pnl_pct": round((total_unrealized_pnl / total_cost) * 100, 2) if total_cost else 0.0,
    }


def calculate_paper_performance(current_prices_by_symbol):
    """Summarize paper-trading performance from saved trades."""
    trades = load_paper_trades()
    position_summary = calculate_paper_positions(current_prices_by_symbol)
    positions = position_summary.get("positions", {})
    number_of_trades = len(trades)

    if positions:
        best_position = max(positions.items(), key=lambda item: item[1]["unrealized_pnl"])
        worst_position = min(positions.items(), key=lambda item: item[1]["unrealized_pnl"])
    else:
        best_position = ("N/A", {"unrealized_pnl": 0.0})
        worst_position = ("N/A", {"unrealized_pnl": 0.0})

    winning_trades = 0
    win_rate = 0.0
    for trade in trades:
        if trade.get("status") != "open":
            continue
        symbol = trade.get("symbol")
        current_price = current_prices_by_symbol.get(symbol, 0) or 0
        if current_price <= 0:
            continue
        quantity = float(trade.get("quantity", 0) or 0)
        entry_price = float(trade.get("price", 0) or 0)
        if quantity <= 0 or entry_price <= 0:
            continue
        realized = (current_price - entry_price) / entry_price * 100
        if realized >= 0:
            winning_trades += 1

    if number_of_trades:
        win_rate = round((winning_trades / number_of_trades) * 100, 2)

    return {
        "total_market_value": position_summary.get("market_value", 0.0),
        "total_unrealized_pnl": position_summary.get("unrealized_pnl", 0.0),
        "total_unrealized_pnl_pct": position_summary.get("unrealized_pnl_pct", 0.0),
        "best_position": best_position[0],
        "worst_position": worst_position[0],
        "number_of_trades": number_of_trades,
        "win_rate": win_rate,
    }
