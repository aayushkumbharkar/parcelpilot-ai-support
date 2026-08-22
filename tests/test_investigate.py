from auth.mock_auth import authenticate
from agent.graph import run_agent


def test_investigate_sla_breach_risk_uses_ticket_data():
    result = run_agent(authenticate("internal_ops"), "Investigate sla_breach_risk for TCK-9001")

    assert result["escalation_required"] is False
    assert "TCK-9001" in result["answer"]
    assert "SLA window: 6 hours" in result["answer"]
    assert [step["tool"] for step in result["tool_trace"]] == ["structured_lookup", "document_search"]


def test_investigate_stale_high_priority_uses_ticket_data():
    result = run_agent(authenticate("internal_ops"), "Investigate stale_high_priority for TCK-9001")

    assert result["escalation_required"] is False
    assert "P1 priority" in result["answer"]
    assert "last updated 5 hours ago" in result["answer"]


def test_investigate_multi_customer_impact_uses_all_ticket_ids():
    result = run_agent(authenticate("internal_ops"), "Investigate multi_customer_impact for TCK-9001, TCK-9002")

    assert result["escalation_required"] is False
    assert "TCK-9001" in result["answer"]
    assert "TCK-9002" in result["answer"]
    assert "carrier CR-77" in result["answer"]


def test_investigate_severity_spike_uses_ticket_data():
    result = run_agent(authenticate("internal_ops"), "Investigate severity_spike for TCK-9001, TCK-9002, TCK-9003")

    assert result["escalation_required"] is False
    assert "TCK-9001" in result["answer"]
    assert "TCK-9002" in result["answer"]
    assert "TCK-9003" in result["answer"]
