def _safe_float(value, default=0.0):
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _benchmark_return(benchmark_returns):
    if benchmark_returns is None:
        return 0.0
    if isinstance(benchmark_returns, dict):
        if "best_benchmark" in benchmark_returns:
            return _safe_float((benchmark_returns.get("best_benchmark") or {}).get("return_pct", 0.0))
        if "benchmark_return_pct" in benchmark_returns:
            return _safe_float(benchmark_returns.get("benchmark_return_pct", 0.0))
        values = [_safe_float(value) for value in benchmark_returns.values()]
        return sum(values) / len(values) if values else 0.0
    if isinstance(benchmark_returns, (list, tuple)):
        values = [_safe_float(value) for value in benchmark_returns]
        return sum(values) / len(values) if values else 0.0
    return _safe_float(benchmark_returns)


def _is_positive_signal(signal):
    return signal in {"Strong Watch", "Watch", "Paper Buy Candidate", "Research Candidate"}


def _is_defensive_signal(signal):
    return signal in {"Caution", "Avoid", "Reduce Exposure", "Thesis Broken"}


def _is_success(prediction, realized_return):
    label = str(prediction.get("evaluation_label", ""))
    if label in {"Strong Hit", "Partial Hit", "Good"}:
        return True
    if label in {"Miss", "Poor"}:
        return False

    signal = str(prediction.get("signal", prediction.get("suggested_action", "")))
    if _is_positive_signal(signal):
        return realized_return > 0
    if _is_defensive_signal(signal):
        return realized_return <= 0
    return abs(realized_return) <= 1


def _best_holding_window(predictions):
    windows = {}
    for prediction in predictions:
        window = str(prediction.get("time_horizon", "") or "Unspecified")
        realized = _safe_float(
            prediction.get("realized_return_pct", prediction.get("realized_return", 0.0))
        )
        if window not in windows:
            windows[window] = []
        windows[window].append(realized)

    if not windows:
        return "Not enough data"

    best_window = max(
        windows.items(),
        key=lambda item: sum(item[1]) / len(item[1]) if item[1] else -999,
    )
    return best_window[0]


def _worst_holding_window(predictions):
    windows = {}
    for prediction in predictions:
        window = str(prediction.get("time_horizon", "") or "Unspecified")
        realized = _safe_float(
            prediction.get("realized_return_pct", prediction.get("realized_return", 0.0))
        )
        windows.setdefault(window, []).append(realized)

    if not windows:
        return "Not enough data"

    worst_window = min(
        windows.items(),
        key=lambda item: sum(item[1]) / len(item[1]) if item[1] else 999,
    )
    return worst_window[0]


def _sample_confidence(total):
    if total <= 0:
        return "No evidence yet"
    if total < 5:
        return "Not enough evidence"
    if total < 15:
        return "Early evidence"
    return "Reviewable sample"


def _group_key(prediction, field, default):
    value = prediction.get(field, default)
    if value in (None, ""):
        return default
    return str(value)


def _grouped_summary(evaluated, field, default):
    groups = {}
    for item in evaluated:
        key = _group_key(item["prediction"], field, default)
        groups.setdefault(key, []).append(item)

    rows = []
    for key, items in sorted(groups.items()):
        total = len(items)
        wins = sum(1 for item in items if item["success"])
        avg_return = sum(item["realized_return"] for item in items) / total if total else 0.0
        drawdowns = [abs(item["drawdown"]) for item in items if item["drawdown"] != 0]
        avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else 0.0
        rows.append(
            {
                "group": key,
                "count": total,
                "win_rate": round((wins / total) * 100, 2) if total else 0.0,
                "avg_return": round(avg_return, 2),
                "avg_drawdown": round(avg_drawdown, 2),
                "sample_confidence": _sample_confidence(total),
            }
        )
    return rows


def evaluate_prediction_accuracy(prediction_log, benchmark_returns=None):
    """Evaluate saved research predictions against realized outcomes.

    This is a research-only calibration summary. It does not place trades,
    connect to brokers, or claim future prediction accuracy.
    """
    predictions = list(prediction_log or [])
    evaluated = []

    for prediction in predictions:
        realized = _safe_float(
            prediction.get("realized_return_pct", prediction.get("realized_return", 0.0))
        )
        drawdown = _safe_float(prediction.get("max_drawdown", prediction.get("max_drawdown_pct", 0.0)))
        success = _is_success(prediction, realized)
        evaluated.append(
            {
                "prediction": prediction,
                "realized_return": realized,
                "drawdown": drawdown,
                "success": success,
            }
        )

    total = len(evaluated)
    wins = sum(1 for item in evaluated if item["success"])
    positive_signals = [
        item
        for item in evaluated
        if _is_positive_signal(
            str(
                item["prediction"].get(
                    "signal",
                    item["prediction"].get("suggested_action", ""),
                )
            )
        )
    ]
    false_positives = sum(1 for item in positive_signals if item["realized_return"] <= 0)

    avg_return = (
        sum(item["realized_return"] for item in evaluated) / total
        if total
        else 0.0
    )
    drawdowns = [abs(item["drawdown"]) for item in evaluated if item["drawdown"] != 0]
    avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else 0.0
    false_positive_rate = (
        (false_positives / len(positive_signals)) * 100
        if positive_signals
        else 0.0
    )
    win_rate = (wins / total) * 100 if total else 0.0
    benchmark_return = _benchmark_return(benchmark_returns)
    alpha_vs_benchmark = avg_return - benchmark_return
    sample_confidence = _sample_confidence(total)

    lessons = []
    if total == 0:
        lessons.append("Save predictions first, then evaluate them after market outcomes are known.")
    elif sample_confidence == "Not enough evidence":
        lessons.append("This sample is too small to trust; treat conclusions as learning notes only.")
    elif win_rate >= 60:
        lessons.append("Signal direction has been useful so far; keep monitoring for sample-size bias.")
    else:
        lessons.append("Signal direction needs calibration before increasing trust.")

    if false_positive_rate >= 40:
        lessons.append("False positives are elevated; tighten entry filters and data-quality checks.")
    if avg_drawdown >= 15:
        lessons.append("Average drawdown after signals is high; reduce sizing or wait for cleaner setups.")
    if alpha_vs_benchmark < 0:
        lessons.append("Average signal return trails the benchmark; compare against ETF alternatives first.")
    elif total:
        lessons.append("Average signal return is ahead of the benchmark in this sample.")

    saved_lessons = [
        str(prediction.get("lesson", "")).strip()
        for prediction in predictions
        if str(prediction.get("lesson", "")).strip()
    ]
    lessons.extend(saved_lessons[:3])

    return {
        "win_rate": round(win_rate, 2),
        "avg_return_after_signal": round(avg_return, 2),
        "false_positive_rate": round(false_positive_rate, 2),
        "avg_drawdown_after_signal": round(avg_drawdown, 2),
        "best_holding_window": _best_holding_window(predictions),
        "worst_holding_window": _worst_holding_window(predictions),
        "alpha_vs_benchmark": round(alpha_vs_benchmark, 2),
        "sample_confidence": sample_confidence,
        "grouped_by_signal": _grouped_summary(evaluated, "signal", "Unspecified"),
        "grouped_by_regime": _grouped_summary(evaluated, "regime", "Unknown"),
        "grouped_by_horizon": _grouped_summary(evaluated, "time_horizon", "Unspecified"),
        "grouped_by_asset_class": _grouped_summary(evaluated, "asset_class", "Unknown"),
        "lessons": lessons,
        "disclaimer": (
            "Research-only calibration. These statistics describe past saved predictions and "
            "do not guarantee future accuracy, profits, or trade outcomes."
        ),
        "summary": (
            f"Reviewed {total} saved prediction(s). "
            f"Sample confidence: {sample_confidence}. "
            f"Win rate {win_rate:.1f}%, average return {avg_return:+.2f}%, "
            f"alpha vs benchmark {alpha_vs_benchmark:+.2f}%."
        ),
    }
