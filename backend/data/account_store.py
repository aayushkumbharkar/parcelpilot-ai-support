from auth.access_control import require_account_read
from auth.mock_auth import Principal
from data.seed import ACCOUNTS, ORDERS


def _visible_accounts(principal: Principal) -> set[str]:
    if principal.role == "customer":
        return {principal.account_id or ""}
    return {row["account_id"] for row in ACCOUNTS}


class AccountStore:
    def query_order(self, order_id: str, account_id: str) -> list[dict]:
        return [dict(row) for row in ORDERS if row["order_id"].lower() == order_id.lower() and row["account_id"] == account_id]

    def get_order(self, principal: Principal, order_id: str, account_id: str | None = None) -> dict:
        matches = [row for row in ORDERS if row["order_id"].lower() == order_id.lower()]
        if not matches:
            raise KeyError("order not found")
        order = matches[0]
        if account_id and order["account_id"] != account_id:
            raise PermissionError("order account mismatch")
        require_account_read(principal, order["account_id"])
        return dict(order)

    def find_active_late_pickup(self, principal: Principal, account_id: str | None = None) -> dict:
        accounts = {account_id} if account_id else _visible_accounts(principal)
        for row in ORDERS:
            if row["account_id"] in accounts and row["pickup_delay_hours"] >= 2 and row["carrier_fault"]:
                require_account_read(principal, row["account_id"])
                return dict(row)
        raise KeyError("late pickup order not found")

    def get_account(self, principal: Principal, account_id: str) -> dict:
        require_account_read(principal, account_id)
        for row in ACCOUNTS:
            if row["account_id"] == account_id:
                return dict(row)
        raise KeyError("account not found")
