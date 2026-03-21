import json
from rich import print

from agent_x.llm_factory import LLMFactory
from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)


def get_llm():
    """Get the LLM for function calling."""
    config = AgentXConfiguration()
    # Add functiongemma configuration if not present
    if config.get_llm_config("functiongemma:270m-it-fp16") is None:
        config.add_llm_config(
            LLMConfig(
                name="functiongemma:270m-it-fp16",
                provider=LLMProvider.OLLAMA,
                model_name="functiongemma:270m-it-fp16",
                temperature=0,
            )
        )
    factory = LLMFactory(config)
    return factory.get_chat_model("functiongemma:270m-it-fp16")


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


def function_call():
    messages = [
        {"role": "user", "content": "best game in year in the past, like 2023?"}
    ]
    # messages = [{'role': 'user', 'content': 'how is the weather in Chile?'}]
    print(f"Prompt: {messages[0]['content']}")

    llm = get_llm()
    response = llm.invoke(messages, tools=[get_weather, get_best_game, calculate])

    if response.tool_calls:
        tool = response.tool_calls[0]
        print(f"Calling: {tool['function']['name']}({tool['function']['arguments']})")

        if tool["function"]["name"] == "get_weather":
            result = get_weather(**tool["function"]["arguments"])
        elif tool["function"]["name"] == "get_best_game":
            result = get_best_game(**tool["function"]["arguments"])
        else:
            result = calculate(**tool["function"]["arguments"])

        print(f"Result: {result}")

        # First append the assistant's tool-call message, then the tool result
        messages.append(response)
        messages.append(
            {"role": "tool", "content": result, "name": tool["function"]["name"]}
        )

        final = llm.invoke(messages)
        print("Response:", final.content)
    else:
        print("Response:", response.content)
