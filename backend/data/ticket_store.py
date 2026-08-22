from auth.access_control import require_account_read
from auth.mock_auth import Principal
from data.seed import TICKETS


class TicketStore:
    def list_visible(self, principal: Principal) -> list[dict]:
        rows = []
        for row in TICKETS:
            try:
                require_account_read(principal, row["account_id"])
                rows.append(dict(row))
            except PermissionError:
                pass
        return rows

    def get_ticket(self, principal: Principal, ticket_id: str) -> dict:
        for row in TICKETS:
            if row["ticket_id"].lower() == ticket_id.lower():
                require_account_read(principal, row["account_id"])
                out = dict(row)
                out["resolution"] = f"[UNVERIFIED PRIOR RESOLUTION] {out['resolution']}"
                return out
        raise KeyError("ticket not found")
