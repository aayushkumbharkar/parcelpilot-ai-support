from auth.mock_auth import Principal
from data.seed import DOCUMENT_CHUNKS
from retrieval.authority import label_chunk
from retrieval.conflict_detector import detect_conflicts


def _topic_for(query: str) -> str:
    text = query.lower()
    if "cancel" in text:
        return "cancellation_fee"
    if "credit" in text or "late" in text or "pickup" in text:
        return "service_credit"
    return "general"


def search_documents(
    principal: Principal,
    query: str,
    customer_id: str | None = None,
    include_deprecated: bool = False,
    min_authority_rank: int = 0,
) -> dict:
    if principal.role == "customer":
        customer_id = principal.account_id
        include_deprecated = False
    topic = _topic_for(query)
    rows = []
    for chunk in DOCUMENT_CHUNKS:
        if chunk["topic"] != topic:
            continue
        if chunk["authority_rank"] < min_authority_rank:
            continue
        if chunk["is_deprecated"] and not include_deprecated:
            continue
        scope = chunk["customer_scope"]
        if scope not in {None, customer_id}:
            continue
        rows.append(label_chunk(chunk))
    rows.sort(key=lambda item: item["authority_rank"], reverse=True)
    return {"chunks": rows, "conflict_report": detect_conflicts(rows)}
