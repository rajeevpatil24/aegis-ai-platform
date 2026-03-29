from fastapi import APIRouter, Query
from langfuse import observe, get_client
import logging, json

from guard_rails import analyze_input
from test_rag import log_event, call_llm, retrieve_context

router = APIRouter()

@router.get("/rag/ask")
@observe()
def ask(q: str = Query(...)):
    try:
        lf = get_client()

        log_event("query_received", query=q)

        analysis = analyze_input(q)
        is_attack = getattr(analysis, "is_injection", False)

        if is_attack:
            log_event("attack_blocked", query=q)
            return {"error": "Potential prompt injection detected"}

        # 🔹 Retrieval span
        with lf.span(name="retrieval", input={"query": q}) as span:
            context = retrieve_context(q)
            span.update(output={"context": context})

        # 🔹 Prompt
        prompt = f"""
You are a helpful AI assistant.

Context:
{context}

User:
{q}

Answer the question.
"""

        # 🔹 LLM span
        with lf.span(name="llm_call", input={"prompt": prompt}) as span:
            response = call_llm(prompt)
            span.update(output={"response": response})

        log_event("response_generated", query=q, response=response)

        return {
            "query": q,
            "context": context,
            "response": response
        }

    except Exception as e:
        logging.error(json.dumps({
            "event": "error",
            "error": str(e),
            "query": q
        }))
        return {"error": str(e)}