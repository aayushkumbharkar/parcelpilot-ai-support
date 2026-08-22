from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.graph import run_agent
from agent.tools import TOOLS, execute_action
from analytics.issue_detector import IssueDetector
from auth.mock_auth import MOCK_TOKENS, authenticate
from config import get_settings

settings = get_settings()
app = FastAPI(title="ParcelPilot AI Support System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
PENDING_ACTIONS: dict[str, dict] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ConfirmRequest(BaseModel):
    draft: dict
    confirmed: bool


def _principal(authorization: str | None):
    token = (authorization or "Bearer customer_northstar").replace("Bearer ", "")
    try:
        return authenticate(token)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def _stage_action(response: dict) -> dict:
    draft = response.get("pending_action")
    if not draft:
        return response
    session_id = str(uuid4())
    draft["awaiting_confirmation"] = True
    PENDING_ACTIONS[session_id] = draft
    response["session_id"] = session_id
    response["pending_action"] = draft
    return response


@app.get("/health")
def health():
    return {"ok": True, "tools": [tool.__name__ for tool in TOOLS], "mock_mode": settings.mock_mode}


@app.get("/tokens")
def tokens():
    return {key: value.__dict__ for key, value in MOCK_TOKENS.items()}


@app.post("/chat")
def chat(payload: ChatRequest, authorization: str | None = Header(default=None)):
    principal = _principal(authorization)
    text = payload.message.strip().lower()
    if payload.session_id and text in {"yes", "y", "confirm"}:
        draft = PENDING_ACTIONS.pop(payload.session_id, None)
        if not draft:
            raise HTTPException(status_code=404, detail="pending action not found")
        result = execute_action(draft, True)
        return {
            "answer": "Escalation created." if result.get("action_type") == "create_escalation" else "Action executed.",
            "tool_trace": [{"tool": draft["action_type"], "status": "done", "result_summary": "Executed after confirmation"}],
            "sources": [],
            "conflict_report": None,
            "pending_action": None,
            "escalation_created": result.get("action_type") == "create_escalation",
        }
    if payload.session_id and text in {"no", "n", "cancel"}:
        PENDING_ACTIONS.pop(payload.session_id, None)
        return {"answer": "Action cancelled.", "tool_trace": [], "sources": [], "conflict_report": None, "pending_action": None, "escalation_created": False}
    try:
        return _stage_action(run_agent(principal, payload.message))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/confirm")
def confirm(payload: ConfirmRequest, authorization: str | None = Header(default=None)):
    _principal(authorization)
    return execute_action(payload.draft, payload.confirmed)


@app.get("/issues")
def issues(authorization: str | None = Header(default=None)):
    principal = _principal(authorization)
    try:
        return IssueDetector().run(principal)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.get("/internal/issues")
def internal_issues(authorization: str | None = Header(default=None)):
    return issues(authorization)
