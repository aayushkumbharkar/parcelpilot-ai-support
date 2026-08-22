# Product Note

Additional problem chosen: Problem 1, Proactive Issue Detection.

The backend includes an IssueDetector for internal users. It ranks operational signals from ticket data: stale high-priority tickets, SLA breach risk, multi-customer impact, and severity spike. The frontend includes IssueRadar for support and ops roles. It shows ranked cards with signal type, affected accounts, ticket IDs, urgency score, and an Investigate action that pre-fills the chat with a focused query.

Intentionally left out: scheduled background jobs, embeddings-based clustering, real carrier integrations, and write-back to production ticketing systems. Those would be premature without the real data pack, ticket volume, and deployment environment. Instead, detection runs on demand over seeded data and mock actions write to a local JSONL file only after user confirmation.

Primary metric: escalation rate, defined as the percentage of chatbot conversations routed to human support. It tracks whether the assistant handles routine customer and internal operations questions without increasing risk. A good system should reduce avoidable escalations while still escalating low-confidence, conflicting, or state-changing cases that need human review.
