from fastapi import FastAPI, APIRouter, Query
import logging
import json

from guard_rails import analyze_input, evaluate_response
from langfuse import observe

import time
import uuid
import mlflow


router = APIRouter()
logging.basicConfig(level=logging.INFO)

from langfuse import Langfuse

mlflow.set_tracking_uri("file:///Users/username/Desktop/projects/aegis-ai-platform/mlruns")
mlflow.set_experiment("aegis-rag")

langfuse = Langfuse(
  secret_key="sk-XXX_XXXX_XXXX_XXXX",
  public_key="pk-XXX_XXXX_XXXX_XXXX",
  host="http://localhost:3005"
)

sentences = [
    "My name is User",
    "I work in a multinational company",
    "The work culture is very toxic",
    "I enjoy working from home",
    "The team collaboration is poor",
    "The manager is very supportive",
    "There is too much workload",
    "I am learning new technologies",
    "The salary is not satisfactory",
    "The product quality is excellent",
]


def log_event(event_type, **kwargs):
    logging.info(json.dumps({"event": event_type, **kwargs}))


def retrieve_context(query):
    return [s for s in sentences if any(w.lower() in s.lower() for w in query.split())][:3] or ["No relevant context found"]


def call_llm(prompt):
    return f"[MOCK RESPONSE]\n{prompt}"



@router.get("/rag/ask")
def ask(q: str = Query(...)):
    start_time = time.time()
    trace_id = str(uuid.uuid4())

    mlflow.set_experiment("aegis-rag")

    try:
        with mlflow.start_run():

            log_event("trace_start", trace_id=trace_id, query=q)

            # 🔹 Guardrail
            analysis = analyze_input(q)
            is_attack = analysis.get("is_injection", False)

            mlflow.log_param("query", q)
            mlflow.log_param("is_attack", is_attack)

            if is_attack:
                mlflow.log_metric("blocked", 1)
                log_event("attack_blocked", trace_id=trace_id, query=q)

                return {"error": "Prompt injection detected"}

            # 🔹 Retrieval
            context = retrieve_context(q)
            log_event("retrieval", trace_id=trace_id, context=context)

            # 🔹 LLM
            prompt = f"Context: {context}\nUser: {q}"
            response = call_llm(prompt)

            latency = time.time() - start_time

            # 🔹 Evaluation
            scores = evaluate_response(q, context, response)

            # 🔹 MLflow logging
            mlflow.log_metric("latency", latency)
            mlflow.log_metric("relevance", scores["relevance"])
            mlflow.log_metric("safety", scores["safety"])
            mlflow.log_metric("attack_success", scores["attack_success"])

            mlflow.log_param("response", response[:200])

            # 🔥 Decision Engine
            if scores["attack_success"] == 1:
                mlflow.log_param("status", "CRITICAL_FAIL")

            elif scores["relevance"] < 0.5:
                mlflow.log_param("status", "LOW_QUALITY")

            else:
                mlflow.log_param("status", "PASS")

            log_event(
                "trace_complete",
                trace_id=trace_id,
                latency=latency,
                scores=scores
            )

            return {
                "trace_id": trace_id,
                "query": q,
                "context": context,
                "response": response,
                "scores": scores
            }

    except Exception as e:
        log_event("error", trace_id=trace_id, error=str(e))
        return {"error": str(e)}

app = FastAPI()
app.include_router(router)