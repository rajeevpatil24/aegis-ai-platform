# guard_rails.py

import re

ATTACK_PATTERNS = [
    r"ignore previous instructions",
    r"you are now",
    r"act as",
    r"override",
    r"system prompt",
    r"admin mode",
    r"reveal hidden",
]

def analyze_input(text):
    text_lower = text.lower()

    for pattern in ATTACK_PATTERNS:
        if re.search(pattern, text_lower):
            return {
                "is_injection": True,
                "pattern": pattern
            }

    return {
        "is_injection": False,
        "pattern": None
    }


def evaluate_response(query,context,response):
    score =0
    if any(c.lower() in response.lower() for c in context ):
        score +=1
    if "No relevant context" in context[0]:
        score =-1
    if len(response) > 50:
        score+=1
    return score