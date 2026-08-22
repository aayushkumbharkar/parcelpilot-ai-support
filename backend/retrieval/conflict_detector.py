def _topic_for(chunk: dict) -> str:
    if chunk.get("topic"):
        return str(chunk["topic"])
    text = str(chunk.get("text", "")).lower()
    if "cancel" in text or "cancellation" in text:
        return "cancellation_fee"
    if "credit" in text or "late" in text or "pickup" in text:
        return "service_credit"
    return "general"


def detect_conflicts(chunks: list[dict]) -> dict:
    conflicts = []
    by_topic: dict[str, list[dict]] = {}
    for chunk in chunks:
        by_topic.setdefault(_topic_for(chunk), []).append(chunk)

    for topic, group in by_topic.items():
        ranks = {int(item.get("authority_rank", 0)) for item in group}
        has_deprecated = any(item.get("is_deprecated") or item.get("source_type") == "deprecated_policy" for item in group)
        if len(group) > 1 and ranks and max(ranks) - min(ranks) > 20:
            winner = sorted(group, key=lambda item: int(item.get("authority_rank", 0)), reverse=True)[0]
            conflicts.append(
                {
                    "topic": topic,
                    "winner_chunk_id": winner.get("chunk_id", winner.get("source_file", "unknown")),
                    "highest_authority_source": winner.get("source_file", winner.get("source_type", "unknown")),
                    "overridden_sources": [
                        item.get("source_file", item.get("source_type", "unknown")) for item in group if item is not winner
                    ],
                    "deprecated_context_present": has_deprecated,
                }
            )
    return {"has_conflicts": bool(conflicts), "conflicts": conflicts}
