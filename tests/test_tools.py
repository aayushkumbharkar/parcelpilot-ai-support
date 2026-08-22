from backend.agent.tools import TOOLS
from backend.agent.tools.calculator import calculator_tool


def test_agent_exposes_at_least_five_distinct_tools():
    names = {tool.__name__ for tool in TOOLS}

    assert names >= {
        "document_search_tool",
        "structured_lookup_tool",
        "calculator_tool",
        "escalation_tool",
        "ticket_update_tool",
        "task_create_tool",
    }


def test_calculator_applies_northstar_credit_terms():
    result = calculator_tool(
        "service_credit_amount",
        {"subtotal": 1000.0, "pickup_delay_hours": 3, "carrier_fault": True},
        applicable_agreement="northstar",
    )

    assert result["amount"] == 150.0
    assert result["formula_used"] == "subtotal * 15%"
