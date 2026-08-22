from auth.mock_auth import Principal


def can_read_account(principal: Principal, account_id: str) -> bool:
    if principal.role == "customer":
        return principal.account_id == account_id
    return principal.role in {"support", "ops_manager"}


def can_cross_account_analytics(principal: Principal) -> bool:
    return principal.role == "ops_manager"


def can_update_ticket(principal: Principal, account_id: str) -> bool:
    if principal.role == "customer":
        return False
    return can_read_account(principal, account_id)


def require_account_read(principal: Principal, account_id: str) -> None:
    if not can_read_account(principal, account_id):
        raise PermissionError("account scope denied")
