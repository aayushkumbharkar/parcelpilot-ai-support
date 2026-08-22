# ParcelPilot AI Support System

FastAPI plus React/Vite MVP for ParcelPilot support. It includes customer and internal chat contexts, account-scoped data access, authority-ranked source retrieval, confirmation-gated actions, and an internal issue radar.

## Setup In 5 Commands

1. cd C:/ParcelPilot/backend
2. python.exe -m pip install -r requirements.txt
3. python.exe -m pytest tests/ -v
4. python.exe -m uvicorn main:app --reload --port 8010
5. cd C:/ParcelPilot/frontend && npm install && VITE_API_URL=http://localhost:8010 npm run dev

Open http://localhost:5174 if 5173 is already occupied. Otherwise Vite will print the local URL.

## Demo Queries

- Can Northstar cancel ORD-1001 without a cancellation fee? Explain why.
- A pickup is 3 hours late due to carrier fault. Should I get a service credit?
- Please escalate this late pickup issue.

## Mock Tokens

- customer_northstar
- customer_lumenworks
- internal_support
- internal_ops

Frontend header switches tokens. API calls use Authorization: Bearer TOKEN.

## Architecture Note

Access control lives in data and retrieval code, not prompts. AccountStore, TicketStore, and document search enforce customer account scope and internal role visibility. Source chunks carry source_type, authority_rank, customer_scope, is_deprecated, is_current, and page_number metadata.

State-changing tools return drafts. The confirm endpoint executes only after explicit confirmation and writes mock actions to data/mock_actions.jsonl when confirmed.

The seeded data covers ORD-1001 cancellation and a 3-hour carrier-fault pickup delay. The deterministic agent graph uses distinct tools for lookup, document search, calculation, and action staging, so the assessment paths are runnable without external LLM credentials.

## Docker

Run docker compose up --build from C:/ParcelPilot.

## Product Note

Problem 1 chosen: proactive issue detection. Metric: escalation rate, the percentage of user queries routed to human support.

## Local Port Note

On this machine, port 8000 is unavailable, so the verified local backend runs on 8010 and Vite selected 5174 because 5173 was already occupied.
