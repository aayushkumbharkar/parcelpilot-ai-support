from backend.agent.graph import run_agent
from backend.auth.mock_auth import authenticate


def test_ord_1001_cancellation_fee_flow():
    result = run_agent(authenticate("customer_northstar"), "Can Northstar cancel ORD-1001 without a cancellation fee? Explain why.")

    assert "without a cancellation fee" in result["answer"]
    assert "$0.00" in result["answer"]
    assert [step["tool"] for step in result["tool_trace"]] == ["structured_lookup", "document_search", "calculator"]
    assert result["sources"][0]["source_type"] == "customer_agreement"


def test_service_credit_eligibility_flow():
    result = run_agent(authenticate("customer_northstar"), "A pickup is 3 hours late due to carrier fault. Should I get a service credit?")

    assert "eligible" in result["answer"]
    assert "$150.00" in result["answer"]
    assert [step["tool"] for step in result["tool_trace"]] == ["structured_lookup", "document_search", "calculator", "calculator"]
    assert result["sources"][0]["source_type"] == "customer_agreement"
