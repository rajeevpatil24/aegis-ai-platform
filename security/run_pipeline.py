# security/run_pipeline.py

import requests
from attack_engine import generate_attacks
from evaluator import evaluate_response

API_URL = "http://localhost:8090/rag/ask"

normal_queries = [
    "team collaboration",
    "salary is not satisfactory"
]

attack_queries = generate_attacks()

all_queries = normal_queries + attack_queries

for q in all_queries:
    try:
        res = requests.get(API_URL, params={"q": q})
        data = res.json()

        response = data.get("response", "")

        scores = evaluate_response(q, [], response)

        print("\n====================")
        print("Query:", q)
        print("Response:", response)
        print("Scores:", scores)

        if scores["attack_success"] == 1:
            print(" SECURITY BREACH DETECTED")
            exit(1)

    except Exception as e:
        print(" Error:", str(e))
        exit(1)

print("\n Pipeline Passed Successfully")