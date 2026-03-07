import json

from rich import print
from ollama import chat

model = "functiongemma:270m"


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


def function_call():
    messages = [
        {"role": "user", "content": "best game in year in the past, like 2023?"}
    ]
    # messages = [{'role': 'user', 'content': 'how is the weather in Chile?'}]
    print(f"Prompt: {messages[0]['content']}")

    response = chat(model, messages=messages, tools=[get_weather, get_best_game])

    if response.message.tool_calls:
        tool = response.message.tool_calls[0]
        print(f"Calling: {tool.function.name}({tool.function.arguments})")

        if tool.function.name == "get_weather":
            result = get_weather(**tool.function.arguments)
        else:
            result = get_best_game(**tool.function.arguments)

        print(f"Result: {result}")

        # First append the assistant's tool-call message, then the tool result
        messages.append(response.message.model_dump())
        messages.append({"role": "tool", "content": result, "name": tool.function.name})

        final = chat(model, messages=messages)
        print("Response:", final.message.content)
    else:
        print("Response:", response.message.content)
