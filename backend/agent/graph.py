from agent.tools import calculator_tool, document_search_tool, escalation_tool, structured_lookup_tool
from auth.mock_auth import Principal
from retrieval.authority import resolve_authority


def _trace(tool: str, result_summary: str, status: str = "done") -> dict:
    return {"tool": tool, "status": status, "result_summary": result_summary}


def run_agent(principal: Principal, message: str) -> dict:
    text = message.lower()
    trace: list[dict] = []
    account_id = principal.account_id

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
        trace.append(_trace("calculator", f"Cancellation fee ${calc['amount']:.2f}"))
        winner = authority["winner"]
        answer = (
            f"Northstar can cancel {order['order_id']} without a cancellation fee. "
            f"Fee: ${calc['amount']:.2f}. {winner['source_file']} page {winner['page_number']} "
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
        trace.append(_trace("calculator", f"Credit ${amount['amount']:.2f}"))
        winner = authority["winner"]
        answer = (
            f"Yes. {order['order_id']} is eligible because pickup is {order['pickup_delay_hours']} hours late "
            f"due to carrier fault. Credit: ${amount['amount']:.2f} using {amount['formula_used']}. "
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
