def evaluate_prediction(prediction, current_price):
    """Evaluate a saved research signal against the current market price."""
    try:
        price_at_signal = float(prediction.get("price_at_signal", ""))
        current_price = float(current_price)
    except (TypeError, ValueError):
        return {
            "realized_return_pct": None,
            "correct_direction": False,
            "evaluation_label": "Miss",
        }

    if price_at_signal <= 0:
        return {
            "realized_return_pct": None,
            "correct_direction": False,
            "evaluation_label": "Miss",
        }

    realized_return_pct = ((current_price - price_at_signal) / price_at_signal) * 100
    signal = prediction.get("signal", "")

    if signal in {"Strong Watch", "Watch"}:
        correct_direction = realized_return_pct > 0
    elif signal in {"Caution", "Avoid"}:
        correct_direction = realized_return_pct <= 0
    else:
        correct_direction = False

    if correct_direction and abs(realized_return_pct) >= 1:
        evaluation_label = "Strong Hit"
    elif correct_direction:
        evaluation_label = "Partial Hit"
    else:
        evaluation_label = "Miss"

    return {
        "realized_return_pct": round(realized_return_pct, 2),
        "correct_direction": correct_direction,
        "evaluation_label": evaluation_label,
    }
