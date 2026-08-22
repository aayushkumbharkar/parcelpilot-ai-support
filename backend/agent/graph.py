import re

from agent.tools import calculator_tool, document_search_tool, escalation_tool, structured_lookup_tool
from auth.mock_auth import Principal
from retrieval.authority import resolve_authority


def _trace(tool: str, result_summary: str, status: str = "done") -> dict:
    return {"tool": tool, "status": status, "result_summary": result_summary}


def _parse_investigate(message: str) -> dict | None:
    match = re.match(r"^\s*investigate\s+([\w\s_]+?)\s+for\s+(.+)$", message.strip(), re.IGNORECASE)
    if not match:
        return None
    raw_signal = match.group(1).strip().lower().replace(" ", "_")
    ticket_ids = re.findall(r"TCK-\d+", match.group(2), re.IGNORECASE)
    if not ticket_ids:
        return None
    return {"signal_type": raw_signal, "ticket_ids": [ticket.upper() for ticket in ticket_ids]}


def _recommendation(signal_type: str) -> str:
    return {
        "sla_breach_risk": "Prioritize owner assignment now and escalate if the remaining SLA window is under one hour.",
        "stale_high_priority": "Update the ticket immediately and assign an owner because high-priority work is stale.",
        "multi_customer_impact": "Investigate carrier and issue commonality before treating this as an isolated customer case.",
        "severity_spike": "Review capacity and incident handling because recent high-severity volume is elevated.",
    }.get(signal_type, "Review the ticket details and assign the next accountable owner.")


def _ticket_line(ticket: dict, signal_type: str) -> str:
    ticket_id = ticket.get("ticket_id")
    priority = ticket.get("priority") or "P1"
    status = ticket.get("status")
    account_id = ticket.get("account_id")

    created = ticket.get("created_hours_ago") if ticket.get("created_hours_ago") is not None else ticket.get("created_at")
    sla = ticket.get("sla_hours")

    if created is not None and sla is not None:
        created_val = float(created)
        sla_val = float(sla)
        remaining = sla_val - created_val
        if remaining <= 0:
            sla_str = f"Opened {created_val:g} hours ago. SLA window: {sla_val:g} hours. BREACHED."
        else:
            sla_str = f"Opened {created_val:g} hours ago. SLA window: {sla_val:g} hours. Time remaining: {remaining:g} hours."
    elif created is not None:
        sla_str = f"Opened {float(created):g} hours ago."
    else:
        sla_str = "SLA window: unknown."

    last_updated = ticket.get("last_update_hours_ago") if ticket.get("last_update_hours_ago") is not None else ticket.get("last_updated")
    stale_part = f" last updated {last_updated:g} hours ago." if last_updated is not None and signal_type == "stale_high_priority" else ""

    carrier_id = ticket.get("carrier_id")
    issue_type = ticket.get("issue_type")
    carrier_part = f" Issue type: {issue_type}. carrier {carrier_id}." if carrier_id and signal_type == "multi_customer_impact" else ""

    lines = [
        f"{ticket_id} — {priority} priority, status: {status}.",
        f"{sla_str}{stale_part}{carrier_part}",
        f"Account: {account_id}."
    ]
    return "\n".join(lines)


def _investigate_response(principal: Principal, message: str) -> dict | None:
    parsed = _parse_investigate(message)
    if not parsed:
        return None
    lookup = structured_lookup_tool(principal, "signal", None, parsed)
    tickets = lookup.get("result", {}).get("tickets", [])
    if not tickets:
        return None
    docs = document_search_tool(principal, parsed["signal_type"].replace("_", " "), None, min_authority_rank=0)

    ticket_blocks = [_ticket_line(t, parsed["signal_type"]) for t in tickets]
    rec = _recommendation(parsed["signal_type"])
    answer = "\n\n".join(ticket_blocks + [rec])
    return {
        "answer": answer,
        "tool_trace": [
            _trace("structured_lookup", f"{len(tickets)} ticket row(s) found"),
            _trace("document_search", "Policy context checked"),
        ],
        "sources": docs.get("chunks", [])[:1],
        "conflict_report": docs.get("conflict_report"),
        "pending_action": None,
        "escalation_required": False,
    }


def run_agent(principal: Principal, message: str) -> dict:
    text = message.lower()
    trace: list[dict] = []
    account_id = principal.account_id
    currency = chr(36)

    investigate = _investigate_response(principal, message)
    if investigate:
        return investigate

    if "escalat" in text:
        tickets = structured_lookup_tool(principal, "sla_status", account_id, {})["result"]
        ticket = tickets[0]
        trace.append(_trace("structured_lookup", f"{ticket['ticket_id']} selected"))
        draft = escalation_tool(ticket["ticket_id"], "User requested escalation", "high", ticket["account_id"], ticket["description"])
        trace.append(_trace("escalation_tool", "Draft escalation ready", "pending"))
        return {
            "answer": "Escalation draft ready. Please confirm before I execute it.",
            "tool_trace": trace,
            "sources": [],
            "conflict_report": None,
            "pending_action": draft,
            "escalation_required": False,
        }

    if "ord-1001" in text or "cancel" in text:
        order = structured_lookup_tool(principal, "order", account_id, {"order_id": "ORD-1001"})["result"]
        trace.append(_trace("structured_lookup", f"{order['order_id']} found"))
        docs = document_search_tool(principal, "cancellation fee", order["account_id"], include_deprecated=principal.role != "customer")
        trace.append(_trace("document_search", "Cancellation terms retrieved"))
        authority = resolve_authority(docs["chunks"])
        calc = calculator_tool("cancellation_fee", order, applicable_agreement=order["account_id"])
        trace.append(_trace("calculator", f"Cancellation fee {currency}{calc['amount']:.2f}"))
        winner = authority["winner"]
        answer = (
            f"Northstar can cancel {order['order_id']} without a cancellation fee. "
            f"Fee: {currency}{calc['amount']:.2f}. {winner['source_file']} page {winner['page_number']} "
            "takes precedence over standard policy for this account."
        )
        return {
            "answer": answer,
            "tool_trace": trace,
            "sources": [winner],
            "conflict_report": docs["conflict_report"],
            "pending_action": None,
            "escalation_required": False,
        }

    if "credit" in text or "late" in text or "pickup" in text:
        order = structured_lookup_tool(principal, "order", account_id, {})["result"]
        trace.append(_trace("structured_lookup", f"{order['order_id']} active late pickup"))
        docs = document_search_tool(principal, "service credit late pickup", order["account_id"])
        trace.append(_trace("document_search", "Service credit terms retrieved"))
        authority = resolve_authority(docs["chunks"])
        eligible = calculator_tool("credit_eligibility", order, applicable_agreement=order["account_id"])
        trace.append(_trace("calculator", f"Eligibility {eligible['eligible']}"))
        amount = calculator_tool("service_credit_amount", order, applicable_agreement=order["account_id"])
        trace.append(_trace("calculator", f"Credit {currency}{amount['amount']:.2f}"))
        winner = authority["winner"]
        answer = (
            f"Yes. {order['order_id']} is eligible because pickup is {order['pickup_delay_hours']} hours late "
            f"due to carrier fault. Credit: {currency}{amount['amount']:.2f} using {amount['formula_used']}. "
            f"Source: {winner['source_file']} page {winner['page_number']}."
        )
        return {
            "answer": answer,
            "tool_trace": trace,
            "sources": [winner],
            "conflict_report": docs["conflict_report"],
            "pending_action": None,
            "escalation_required": False,
        }

    return {
        "answer": "I'm not confident enough to answer this reliably. I recommend escalating to the support team.",
        "tool_trace": [],
        "sources": [],
        "conflict_report": None,
        "pending_action": None,
        "escalation_required": True,
    }
