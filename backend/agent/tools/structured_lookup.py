from typing import Literal

from auth.mock_auth import Principal
from data.account_store import AccountStore
from data.ticket_store import TicketStore


SIGNAL_QUERY_MAP = {
    "sla_breach_risk": {
        "query_type": "ticket",
        "fields": ["ticket_id", "priority", "status", "created_at", "sla_hours", "account_id"],
    },
    "stale_high_priority": {
        "query_type": "ticket",
        "fields": ["ticket_id", "priority", "status", "last_updated", "account_id"],
    },
    "multi_customer_impact": {
        "query_type": "ticket",
        "fields": ["ticket_id", "issue_type", "account_id", "carrier_id", "status"],
    },
    "severity_spike": {
        "query_type": "ticket",
        "fields": ["ticket_id", "priority", "created_at", "account_id", "status"],
    },
}


def _select_fields(row: dict, fields: list[str]) -> dict:
    out = dict(row)
    if "created_hours_ago" in row:
        out["created_at"] = row["created_hours_ago"]
    if "last_update_hours_ago" in row:
        out["last_updated"] = row["last_update_hours_ago"]
    selected = {field: out.get(field) for field in fields}
    for field in ["sla_hours", "created_hours_ago", "last_update_hours_ago", "issue_type", "carrier_id", "description", "created_at", "last_updated"]:
        if field in out and field not in selected:
            selected[field] = out[field]
    return selected


def structured_lookup_tool(
    principal: Principal,
    query_type: Literal["order", "account", "ticket", "sla_status", "signal"],
    account_id: str | None = None,
    filters: dict | None = None,
) -> dict:
    filters = filters or {}
    accounts = AccountStore()
    tickets = TicketStore()
    if query_type == "order":
        if "order_id" in filters:
            data = accounts.get_order(principal, filters["order_id"], account_id)
        else:
            data = accounts.find_active_late_pickup(principal, account_id or principal.account_id)
    elif query_type == "account":
        data = accounts.get_account(principal, account_id or principal.account_id or "")
    elif query_type == "ticket":
        data = tickets.get_ticket(principal, filters["ticket_id"])
    elif query_type == "signal":
        signal_type = filters["signal_type"]
        ticket_ids = filters.get("ticket_ids", [])
        config = SIGNAL_QUERY_MAP.get(signal_type, {
            "query_type": "ticket",
            "fields": ["ticket_id", "priority", "status", "created_at", "sla_hours", "account_id"]
        })
        rows = []
        for ticket_id in ticket_ids:
            try:
                row = tickets.get_ticket(principal, ticket_id)
                rows.append(_select_fields(row, config["fields"]))
            except (KeyError, PermissionError):
                pass
        data = {"signal_type": signal_type, "tickets": rows, "query_type": config["query_type"], "fields": config["fields"]}
    elif query_type == "sla_status":
        data = [ticket for ticket in tickets.list_visible(principal) if ticket["status"] != "resolved"]
    else:
        raise ValueError("unsupported query type")
    return {"result": data, "metadata": {"snapshot_time": "2026-08-21T12:00:00+05:30", "fields_redacted_for_role": []}}
