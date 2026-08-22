from typing import Optional, TypedDict


class AgentState(TypedDict):
    messages: list[dict]
    user_id: str
    account_id: Optional[str]
    user_role: str
    pending_action: Optional[dict]
    action_confirmed: bool
    retrieved_chunks: list[dict]
    conflict_report: Optional[dict]
    tool_trace: list[dict]
    escalation_required: bool
