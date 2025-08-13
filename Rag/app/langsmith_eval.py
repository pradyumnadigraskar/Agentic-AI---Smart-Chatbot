from app.config import LANGSMITH_API_KEY

def evaluate(prompt: str, response: str) -> dict:
    # Basic heuristic evaluation. Replace with LangSmith SDK calls if desired.
    score = 5
    feedback = []
    if len(response) > 100:
        score += 3
    if any(x in response.lower() for x in ["error", "unknown", "i don't know"]):
        score -= 2
        feedback.append("Contains uncertainty")
    return {"score": score, "feedback": "; ".join(feedback) or "OK"}
