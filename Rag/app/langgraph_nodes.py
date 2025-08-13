from typing import Dict, Any
from app.openweather import get_weather_by_city
from app.processor import retrieve_and_answer

def decision_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = payload.get("text", "")
    triggers = ["weather", "temperature", "forecast", "rain", "sunny"]
    if any(t in text.lower() for t in triggers):
        return {"action": "weather", "city": extract_city(text)}
    return {"action": "rag", "query": text}

def extract_city(text: str) -> str:
    import re
    m = re.search(r"in ([A-Za-z\-\s]+)", text)
    if m:
        return m.group(1).strip()
    # default
    return "London"

def weather_worker(inputs: Dict[str, Any]) -> Dict[str, Any]:
    city = inputs.get("city", "London")
    try:
        data = get_weather_by_city(city)
        summary = f"{city}: {data['weather'][0]['description']}, {data['main']['temp']}°C"
        return {"result": summary}
    except Exception as e:
        return {"error": str(e)}

def rag_worker(inputs: Dict[str, Any]) -> Dict[str, Any]:
    q = inputs.get("query", "")
    try:
        ans = retrieve_and_answer(q)
        return {"result": ans}
    except Exception as e:
        return {"error": str(e)}
