from agent.tools.escalation import escalation_tool, execute_action


def test_escalation_requires_confirmation():
    draft = escalation_tool("TCK-9001", "SLA risk", "high", "northstar", "Pickup delay near SLA breach")

    assert draft["requires_confirmation"] is True
    assert draft["action_type"] == "create_escalation"


def test_cancelled_action_does_not_execute():
    draft = escalation_tool("TCK-9001", "SLA risk", "high", "northstar", "Pickup delay near SLA breach")

    result = execute_action(draft, confirmed=False)

    assert result == {"executed": False, "reason": "cancelled"}


def test_escalation_returns_draft_not_executed():
    draft = escalation_tool("TCK-9001", "SLA risk", "high", "northstar", "Pickup delay near SLA breach")

    assert draft["requires_confirmation"] is True
    assert "executed" not in draft


def test_confirmed_escalation_executes():
    draft = escalation_tool("TCK-9001", "SLA risk", "high", "northstar", "Pickup delay near SLA breach")

    result = execute_action(draft, confirmed=True)

    assert result["executed"] is True
    assert result["action_type"] == "create_escalation"
