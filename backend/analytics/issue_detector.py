from collections import Counter, defaultdict

from auth.mock_auth import Principal
from data.ticket_store import TicketStore


class IssueDetector:
    def run(self, principal: Principal) -> dict:
        if principal.role not in {"support", "ops_manager"}:
            raise PermissionError("internal role required")
        tickets = TicketStore().list_visible(principal)
        signals = []

        for ticket in tickets:
            if ticket["status"] != "resolved" and ticket["created_hours_ago"] > ticket["sla_hours"] * 0.8:
                signals.append(self._signal("sla_breach_risk", [ticket], 80))
            if ticket["priority"] == "P1" and ticket["status"] != "resolved" and ticket["last_update_hours_ago"] > 4:
                signals.append(self._signal("stale_high_priority", [ticket], 95))

        by_issue = defaultdict(list)
        by_carrier = defaultdict(list)
        for ticket in tickets:
            by_issue[ticket["issue_type"]].append(ticket)
            by_carrier[ticket["carrier_id"]].append(ticket)

        seen_multi_customer: set[tuple[str, ...]] = set()
        for group in list(by_issue.values()) + list(by_carrier.values()):
            accounts = {item["account_id"] for item in group}
            ticket_ids = tuple(sorted(item["ticket_id"] for item in group))
            if len(accounts) >= 2 and ticket_ids not in seen_multi_customer:
                seen_multi_customer.add(ticket_ids)
                signals.append(self._signal("multi_customer_impact", group, 90))

        priorities = Counter(ticket["priority"] for ticket in tickets if ticket["created_hours_ago"] <= 24)
        if priorities["P1"] + priorities["P2"] >= 2:
            signals.append(self._signal("severity_spike", tickets, 70))

        signals.sort(key=lambda item: item["urgency_score"], reverse=True)
        return {"signals": signals}

    def _signal(self, signal_type: str, tickets: list[dict], score: int) -> dict:
        return {
            "signal_type": signal_type,
            "affected_accounts": sorted({ticket["account_id"] for ticket in tickets}),
            "ticket_ids": [ticket["ticket_id"] for ticket in tickets],
            "urgency_score": score,
            "query": f"Investigate {signal_type} for {', '.join(ticket['ticket_id'] for ticket in tickets)}",
        }
