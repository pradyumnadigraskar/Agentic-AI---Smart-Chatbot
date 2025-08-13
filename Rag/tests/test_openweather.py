import pytest
from app.openweather import get_weather_by_city
import os

def test_weather_missing_key(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "")
    with pytest.raises(RuntimeError):
        get_weather_by_city("London")
