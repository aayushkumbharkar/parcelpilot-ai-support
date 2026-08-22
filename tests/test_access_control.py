import pytest

from backend.agent.tools.structured_lookup import structured_lookup_tool
from backend.auth.mock_auth import authenticate
from backend.retrieval.search import search_documents


def test_customer_cannot_access_other_account_data():
    principal = authenticate("customer_northstar")

    with pytest.raises(PermissionError):
        structured_lookup_tool(principal, "order", "lumenworks", {"order_id": "ORD-2001"})


def test_customer_cannot_see_deprecated_policy():
    principal = authenticate("customer_northstar")

    result = search_documents(principal, "cancellation fee", include_deprecated=True)

    assert all(not chunk["is_deprecated"] for chunk in result["chunks"])


def test_internal_role_can_cross_account_query():
    principal = authenticate("internal_ops")

    result = structured_lookup_tool(principal, "order", "lumenworks", {"order_id": "ORD-2001"})

    assert result["result"]["account_id"] == "lumenworks"
