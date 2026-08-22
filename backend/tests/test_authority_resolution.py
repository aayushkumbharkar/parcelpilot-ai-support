from auth.mock_auth import authenticate
from retrieval.authority import label_chunk, resolve_authority
from retrieval.search import search_documents


def test_customer_agreement_overrides_current_policy():
    principal = authenticate("customer_northstar")

    result = search_documents(principal, "cancellation fee", customer_id="northstar")
    winner = resolve_authority(result["chunks"])["winner"]

    assert winner["source_type"] == "customer_agreement"
    assert winner["authority_rank"] == 100


def test_deprecated_policy_never_cited_as_current():
    principal = authenticate("internal_support")

    result = search_documents(principal, "cancellation fee", customer_id="northstar", include_deprecated=True)
    deprecated = [chunk for chunk in result["chunks"] if chunk["is_deprecated"]]

    assert deprecated
    assert deprecated[0]["text"].startswith("[DEPRECATED - context only]")


def test_historical_ticket_labeled_unverified():
    chunk = {
        "source_type": "historical_ticket",
        "text": "Manual rebook fixed this once.",
    }

    assert label_chunk(chunk)["text"].startswith("[UNVERIFIED PRIOR RESOLUTION]")


def test_conflict_detected_and_surfaced():
    principal = authenticate("internal_support")

    result = search_documents(principal, "cancellation fee", customer_id="northstar", include_deprecated=True)

    assert result["conflict_report"]["has_conflicts"] is True
    assert result["conflict_report"]["conflicts"][0]["highest_authority_source"] == "05_Northstar_Logistics_Enterprise_Agreement.pdf"


def test_customer_agreement_beats_current_policy():
    principal = authenticate("customer_northstar")

    result = search_documents(principal, "cancellation fee", customer_id="northstar")
    winner = resolve_authority(result["chunks"])["winner"]

    assert winner["source_type"] == "customer_agreement"
    assert winner["authority_rank"] > 80


def test_deprecated_chunk_always_labeled():
    principal = authenticate("internal_support")

    result = search_documents(principal, "cancellation fee", customer_id="northstar", include_deprecated=True)
    deprecated = [chunk for chunk in result["chunks"] if chunk["source_type"] == "deprecated_policy"]

    assert deprecated
    assert deprecated[0]["text"].startswith("[DEPRECATED - context only]")
