# ParcelPilot AI Support System Design

## Interpretation

Build a local, assessment-ready ParcelPilot support system with customer and internal chatbot contexts. The implementation uses seeded representative data because no candidate PDF/Excel data pack is present. The backend keeps production-shaped boundaries: auth, account-scoped stores, retrieval, authority resolution, tools, agent orchestration, action confirmation, and issue detection.

## Architecture

FastAPI exposes `/chat`, `/confirm`, `/issues`, `/tokens`, and `/health`. Mock bearer tokens map to customer and internal principals. Data access is enforced in `backend/data` and `backend/retrieval`, not in prompts. Retrieval uses seeded chunks with the same authority metadata required for Chroma ingestion, including customer scope, deprecated flags, page numbers, and source type.

The frontend is a Vite React support console with auth switching, chat, tool traces, source badges, confirmation modal, and internal IssueRadar. It calls the FastAPI API and displays active tool names on each agent step.

## Assumptions

- No source PDFs or Excel pack exists in `C:\ParcelPilot`, so seeded data stands in for ingestion output.
- `MOCK_MODE=true` is default. State-changing actions write JSONL drafts to `data/mock_actions.jsonl` only after confirmation.
- Tool selection is represented by a deterministic agent router for the two required assessment flows; tool functions remain distinct and testable.

## Success Criteria Coverage

- Customer data scope enforced in `AccountStore`, `TicketStore`, and `search_documents`.
- Internal roles use mock role tokens and see scoped data according to role.
- Six distinct tools are exported from `backend.agent.tools`.
- Escalation, ticket update, and task creation return drafts and execute only through `/confirm`.
- Required ORD-1001 cancellation and late pickup credit flows are covered by tests.
- Authority metadata and conflict reports are encoded on chunks and returned with answers.
- Deprecated and historical sources are labeled as context only.
- Frontend shows tool trace and source badges.
- External services are mocked.
