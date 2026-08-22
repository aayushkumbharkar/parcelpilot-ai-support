## ParcelPilot AI Support System

Dual-context AI support agent for ParcelPilot — customer-facing chatbot and internal ops chatbot. FastAPI + LangGraph + ChromaDB + React/Vite. Authority-ranked retrieval over policy documents and structured order/ticket data. Access control enforced at data layer.

## Quick Start (5 commands)

```bash
git clone https://github.com/aayushkumbharkar/parcelpilot-ai-support
cd parcelpilot-ai-support/backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8010
cd ../frontend && npm install && npm run dev
# Backend: http://localhost:8010 | Frontend: http://localhost:5174
```

## Mock Auth Tokens

| Token | Role | Account | Access Level |
|---|---|---|---|
| customer_northstar | customer | Northstar | own account only |
| customer_lumenworks | customer | LumenWorks | own account only |
| internal_support | support | all accounts | read across accounts |
| internal_ops | ops_manager | all accounts | full access + issue dashboard |

Pass token as: `Authorization: Bearer <token>`

## Architecture

### Agent Design
LangGraph StateGraph. Nodes: `auth` → `router` → `tool_node` → `authority_resolution` → `conflict_detection` → `generation` → `escalation_check`. State carries: `user_id`, `account_id`, `role`, `retrieved_chunks` with authority metadata, `conflict_report`, `pending_action`, `tool_trace`.

### Tools
| Tool | Type | Confirmation Required |
|---|---|---|
| document_search | Retrieval | No |
| structured_lookup | Data query | No |
| calculator | Calculation | No |
| escalation_tool | Action | Yes |
| ticket_update | Action | Yes |
| task_create | Action | Yes |

### Source Authority Ranking
| Source | Type | Authority Rank |
|---|---|---|
| Customer agreements (Northstar, LumenWorks) | customer_agreement | 100 |
| Support Policy v3 CURRENT | current_policy | 80 |
| Cancellation & Credit SOP v4 | sop | 70 |
| Product Operations Guide | product_guide | 60 |
| Support Policy v2 DEPRECATED | deprecated_policy | 10 |
| Historical ticket resolutions | historical_ticket | 5 |

Conflicts surfaced explicitly. Deprecated chunks always labeled. Historical resolutions always labeled UNVERIFIED.

### Access Control
Enforced in data/retrieval layer. Customer tokens physically cannot return another account's data regardless of query.

## Example Queries

Q: Can Northstar cancel ORD-1001 without a cancellation fee?  
Flow: `structured_lookup` → `document_search` (agreement) → `document_search` (SOP) → `calculator` → answer with conflict resolution

Q: A pickup is 3 hours late due to carrier fault. Should I get a service credit?  
Flow: `structured_lookup` → `document_search` → `calculator` (eligibility) → `calculator` (amount) → cited answer

## Proactive Issue Detection (Internal Only)

GET `/internal/issues` with `internal_ops` token returns ranked signals: SLA breach risk, recurring ticket clusters, multi-customer carrier issues, severity spikes. Customer tokens return 403.

## Tests

17 tests covering: access control, authority resolution, confirmation gating, multi-step flows, deprecated policy labeling, cross-account data isolation.

```bash
cd backend && python -m pytest tests/ -v
```

## Deployment

Backend: Render (`render.yaml` included)  
Frontend: Vercel (`vercel.json` included)  
Local: `docker-compose up`

## Trade-offs and Known Gaps

- Seeded mock data used instead of real PDF ingestion (retrieval interface is production-shaped, swap ChromaDB loader for real PDFs without changing agent code)
- Mock JWT instead of real auth provider
- No persistent session store — confirmation flow uses in-memory state
- Video demo and hosted URL in submission form

## AI Tools Used

OpenAI Codex for scaffolding and implementation. Claude for architecture design, prompt engineering, and assessment strategy.
