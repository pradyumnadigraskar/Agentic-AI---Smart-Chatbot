import requests
from app.config import OPENWEATHER_API_KEY

def get_weather_by_city(city: str) -> dict:
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY not set in environment")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()
