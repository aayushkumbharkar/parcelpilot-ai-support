from auth.mock_auth import Principal
from retrieval.search import search_documents


def document_search_tool(
    principal: Principal,
    query: str,
    customer_id: str | None = None,
    include_deprecated: bool = False,
    min_authority_rank: int = 0,
) -> dict:
    return search_documents(principal, query, customer_id, include_deprecated, min_authority_rank)
