from typing import Literal

from auth.mock_auth import Principal
from data.account_store import AccountStore
from data.ticket_store import TicketStore


def structured_lookup_tool(
    principal: Principal,
    query_type: Literal["order", "account", "ticket", "sla_status"],
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
    elif query_type == "sla_status":
        data = [ticket for ticket in tickets.list_visible(principal) if ticket["status"] != "resolved"]
    else:
        raise ValueError("unsupported query type")
    return {"result": data, "metadata": {"snapshot_time": "2026-08-21T12:00:00+05:30", "fields_redacted_for_role": []}}
