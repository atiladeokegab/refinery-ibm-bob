from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/api/rag/context")
def get_rag_context(
    program: str = Query("", description="COBOL program name (without extension)"),
    snippet: str = Query("", description="Short COBOL source snippet"),
):
    try:
        from bob.rag.retriever import retrieve

        query = f"COBOL optimization mistakes {program}"
        if "COMPUTE" in snippet.upper():
            query += " financial calculations COMPUTE"
        chunks = retrieve(query, top_k=4)
        if not chunks:
            return {"context": "", "patterns": []}
        patterns = [c.text[:200] for c in chunks[:3]]
        context = ("KNOWN PATTERNS TO AVOID:\n" + "\n".join(f"- {p}" for p in patterns))[:800]
        return {"context": context, "patterns": patterns}
    except Exception as e:
        return {"context": "", "patterns": [], "error": str(e)}
