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


def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression as a string (e.g., "2 + 3 * 4")

    Returns:
        The result of the calculation as a string
    """
    try:
        # Note: Using eval is dangerous in production, but acceptable for this example
        # In a real application, you would use a proper expression parser
        result = eval(expression)
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": str(expression), "message": str(e)})
