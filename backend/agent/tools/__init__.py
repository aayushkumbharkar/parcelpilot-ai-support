from agent.tools.calculator import calculator_tool
from agent.tools.document_search import document_search_tool
from agent.tools.escalation import execute_action, escalation_tool, task_create_tool, ticket_update_tool
from agent.tools.structured_lookup import structured_lookup_tool

TOOLS = [
    document_search_tool,
    structured_lookup_tool,
    calculator_tool,
    escalation_tool,
    ticket_update_tool,
    task_create_tool,
]

__all__ = [
    "TOOLS",
    "calculator_tool",
    "document_search_tool",
    "execute_action",
    "escalation_tool",
    "structured_lookup_tool",
    "task_create_tool",
    "ticket_update_tool",
]
