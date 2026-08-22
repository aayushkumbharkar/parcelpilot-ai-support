from data.seed import DOCUMENT_CHUNKS

SOURCE_CONFIG = {
    row["source_file"]: {
        "source_type": row["source_type"],
        "authority_rank": row["authority_rank"],
        "is_deprecated": row["is_deprecated"],
        "customer_scope": row["customer_scope"],
    }
    for row in DOCUMENT_CHUNKS
}
