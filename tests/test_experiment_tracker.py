from pathlib import Path

from experiment_tracker import (
    compare_experiment_results,
    load_experiments,
    save_experiment,
    update_experiment_result,
)


def test_experiment_tracker_save_load_update(tmp_path):
    csv_path = Path(tmp_path) / "experiments.csv"

    saved = save_experiment(
        experiment_name="Test SMA50 vs SMA20",
        experiment_type="Strategy",
        description="Compare trend windows",
        changed_modules="backtester.py",
        hypothesis="SMA50 may reduce churn.",
        metrics_before="Return 2%",
        status="Planned",
        path=csv_path,
    )
    assert saved["experiment_name"] == "Test SMA50 vs SMA20"

    rows = load_experiments(path=csv_path)
    assert len(rows) == 1
    assert rows[0]["status"] == "Planned"

    updated = update_experiment_result(
        experiment_name="Test SMA50 vs SMA20",
        result="Improved stability",
        lesson="Lower turnover but slower entries.",
        status="Completed",
        metrics_after="Return 3%",
        path=csv_path,
    )
    assert updated is not None

    rows_after = load_experiments(path=csv_path)
    assert rows_after[0]["status"] == "Completed"
    assert rows_after[0]["result"] == "Improved stability"


def test_compare_experiment_results_string_and_dict_inputs():
    result_str = compare_experiment_results(
        "win_rate=55, avg_return=4.2, avg_alpha=1.1, max_drawdown=-8, consistency_score=70",
        "win_rate=58, avg_return=4.8, avg_alpha=1.4, max_drawdown=-6.5, consistency_score=75",
    )
    assert result_str["overall_result"] == "Improved"
    assert len(result_str["improved_metrics"]) >= 1

    result_dict = compare_experiment_results(
        {"win_rate": 60, "avg_return": 5, "avg_alpha": 1.5, "max_drawdown": -7, "consistency_score": 72},
        {"win_rate": 54, "avg_return": 4, "avg_alpha": 1.1, "max_drawdown": -9, "consistency_score": 65},
    )
    assert result_dict["overall_result"] == "Worse"
    assert len(result_dict["worsened_metrics"]) >= 1
