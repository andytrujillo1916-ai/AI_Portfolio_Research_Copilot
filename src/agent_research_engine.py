"""Agent research task generation for portfolio assistant workflows."""


AGENT_ROLES = {
    "Needs Data": "Data Quality Agent",
    "Agent Research": "Growth Discovery Agent",
    "Buy Candidate": "Portfolio Optimizer Agent",
    "Add": "Portfolio Optimizer Agent",
    "Wait for Pullback": "Risk Agent",
    "Trim": "Portfolio Optimizer Agent",
    "Sell Candidate": "Risk Agent",
    "Avoid": "AIOS Assistant Agent",
}


def _priority(action, rank):
    if action in {"Buy Candidate", "Trim"}:
        return "High"
    if action in {"Add", "Needs Data", "Agent Research", "Wait for Pullback"} and rank <= 12:
        return "Medium"
    return "Low"


def generate_agent_research_tasks(buy_finder_rows, data_quality_rows=None, portfolio_plan=None):
    """Create trackable research tasks from buy finder and portfolio actions."""
    buy_finder_rows = buy_finder_rows or []
    data_quality_rows = data_quality_rows or []
    portfolio_plan = portfolio_plan or {}
    tasks = []
    seen = set()

    for row in buy_finder_rows:
        symbol = str(row.get("symbol", "")).upper()
        action = row.get("action", "Agent Research")
        if not symbol or action in {"Hold"}:
            continue
        task_type = "Research candidate"
        if action == "Needs Data":
            task_type = "Fix data quality"
        elif action in {"Buy Candidate", "Add"}:
            task_type = "Prepare buy review"
        elif action == "Wait for Pullback":
            task_type = "Monitor entry zone"
        elif action in {"Trim", "Sell Candidate"}:
            task_type = "Review risk reduction"
        key = (symbol, task_type)
        if key in seen:
            continue
        seen.add(key)
        tasks.append(
            {
                "symbol": symbol,
                "task_type": task_type,
                "priority": _priority(action, int(row.get("buy_finder_rank", 999))),
                "assigned_agent_role": AGENT_ROLES.get(action, "AIOS Assistant Agent"),
                "status": "Open",
                "due_check_date": "Next research session",
                "findings": " | ".join(row.get("agent_unlocks") or row.get("reasons", [])[:2]),
                "linked_final_verdict": action,
            }
        )

    blocked_symbols = {
        str(row.get("symbol", "")).upper()
        for row in data_quality_rows
        if row.get("recommendation_gate") == "Blocked"
    }
    for symbol in sorted(blocked_symbols):
        key = (symbol, "Fix data quality")
        if symbol and key not in seen:
            seen.add(key)
            tasks.append(
                {
                    "symbol": symbol,
                    "task_type": "Fix data quality",
                    "priority": "Medium",
                    "assigned_agent_role": "Data Quality Agent",
                    "status": "Open",
                    "due_check_date": "Next research session",
                    "findings": "Blocked data should be refreshed before any buy/sell label.",
                    "linked_final_verdict": "Needs Data",
                }
            )

    for action in (portfolio_plan or {}).get("actions", [])[:10]:
        portfolio_action = action.get("portfolio_action")
        if portfolio_action in {"Buy Candidate", "Add", "Trim"}:
            key = (action.get("symbol"), "Portfolio action review")
            if key not in seen:
                seen.add(key)
                tasks.append(
                    {
                        "symbol": action.get("symbol", ""),
                        "task_type": "Portfolio action review",
                        "priority": "High" if portfolio_action in {"Buy Candidate", "Trim"} else "Medium",
                        "assigned_agent_role": "Portfolio Optimizer Agent",
                        "status": "Open",
                        "due_check_date": "Next research session",
                        "findings": action.get("reason", "Review portfolio action before paper testing."),
                        "linked_final_verdict": portfolio_action,
                    }
                )

    return {
        "tasks": tasks,
        "summary": f"Generated {len(tasks)} agent research task(s).",
        "assistant_prompts": [
            "What are my best buy candidates?",
            "What needs data before it can become buyable?",
            "What portfolio action improves risk/reward?",
            "What agents are working on?",
        ],
    }

