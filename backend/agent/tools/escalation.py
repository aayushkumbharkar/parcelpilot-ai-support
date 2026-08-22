import json
from pathlib import Path
from typing import Literal

ACTION_LOG = Path("data/mock_actions.jsonl")


def _draft(action_type: str, payload: dict) -> dict:
    return {"requires_confirmation": True, "action_type": action_type, "payload": payload}


def escalation_tool(ticket_id: str, reason: str, priority: Literal["low", "medium", "high", "critical"], account_id: str, summary: str) -> dict:
    return _draft("create_escalation", locals())


def ticket_update_tool(ticket_id: str, status: str, note: str, account_id: str) -> dict:
    return _draft("update_ticket", locals())


def task_create_tool(account_id: str, title: str, due_at: str, owner_role: str) -> dict:
    return _draft("create_task", locals())


def execute_action(draft: dict, confirmed: bool) -> dict:
    if not confirmed:
        return {"executed": False, "reason": "cancelled"}
    ACTION_LOG.parent.mkdir(exist_ok=True)
    with ACTION_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(draft, sort_keys=True) + "\n")
    return {"executed": True, "mock_mode": True, "action_type": draft["action_type"]}
