import json


def get_weather(city: str) -> str:
    """
    Get the current weather for a city.

    Args:
        city: The name of the city

    Returns:
        A string describing the weather
    """
    return json.dumps(
        {"city": city, "temperature": 22, "unit": "celsius", "condition": "sunny"}
    )


def get_best_game(year: str):
    """
    Get best game of the year.

    Args:
        year: Year

    Returns:
        A string describing the best game given a year
    """
    return json.dumps({"year": year, "game": "dark souls"})
