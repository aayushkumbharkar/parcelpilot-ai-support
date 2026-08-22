AUTHORITY_RANKS = {
    "customer_agreement": 100,
    "current_policy": 80,
    "sop": 70,
    "product_guide": 60,
    "deprecated_policy": 10,
    "historical_ticket": 5,
}


def label_chunk(chunk: dict) -> dict:
    out = dict(chunk)
    if out.get("is_deprecated"):
        out["text"] = f"[DEPRECATED - context only] {out['text']}"
    if out.get("source_type") == "historical_ticket":
        out["text"] = f"[UNVERIFIED PRIOR RESOLUTION] {out['text']}"
    return out


def resolve_authority(chunks: list[dict]) -> dict:
    ordered = sorted(chunks, key=lambda item: item["authority_rank"], reverse=True)
    winner = ordered[0] if ordered else None
    overridden = [chunk for chunk in ordered[1:] if winner and chunk["topic"] == winner["topic"]]
    return {"winner": winner, "overridden": overridden}
