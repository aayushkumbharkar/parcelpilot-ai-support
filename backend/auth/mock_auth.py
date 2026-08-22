from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    user_id: str
    account_id: str | None
    role: str
    name: str
    can_view_all_accounts: bool = False


MOCK_TOKENS: dict[str, Principal] = {
    "customer_northstar": Principal("usr_001", "northstar", "customer", "Northstar Logistics"),
    "customer_lumenworks": Principal("usr_002", "lumenworks", "customer", "LumenWorks"),
    "internal_support": Principal("usr_003", None, "support", "Support Agent"),
    "internal_ops": Principal("usr_004", None, "ops_manager", "Ops Manager", True),
}


def authenticate(token: str) -> Principal:
    if token not in MOCK_TOKENS:
        raise PermissionError("invalid role token")
    return MOCK_TOKENS[token]
