import json
from rich import print

from agent_x.common.logger import log_error, log_info
from agent_x.llm_factory import LLMFactory
from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)

from ollama import chat, ChatResponse

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


def function_call(model = "functiongemma:270m-it-fp16"):
    messages = [{"role": "user", "content": "best game in year in the past, like 2023?"}]
    print(f"Prompt: {messages[0]['content']}")
    response = chat(model, messages=messages, tools=[get_weather, get_best_game, calculate])

    try:
        match response:
            case [ChatResponse()] as response_messages:
                tool_to_call = response_messages[0].message
            case ChatResponse() as res:
                tool_to_call = res.message
            case _:
                print("Response:", "Invalid")
                return
    except Exception as e:
        log_error(str(e))
        return

    tool = tool_to_call.tool_calls[0]
    function_name = tool.function.name
    function_args = tool.function.arguments

    print(f"Calling function: {function_name}")
    print(f"Functions args: ({function_args})")

    result: str = ""

    match function_name:
        case "get_weather":
            result = get_weather(**function_args)
        case "get_best_game":
            result = get_best_game(**function_args)
        case _:
            result = ""

    if not result:
        print(f"Result: {result}")
        return

    messages.append(response.message)
    messages.append(
        {"role": "tool", "content": result, "name": function_name}
    )

    final = chat(model, messages)
    print("Response:", final.message.content)

