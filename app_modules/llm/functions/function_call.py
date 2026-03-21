from rich import print
from ollama import chat, ChatResponse

from app.repl.console import Console
from app_modules.llm.functions.route import Route

class QueryRouter:
    def __init__(self, routes: list[Route]):
        self._routes = routes

    def function_call(self, model = "functiongemma:270m-it-fp16"):
        messages = [{"role": "user", "content": "best game in year in the past, like 2023?"}]
        Console.log_success(f"Prompt: {messages[0]['content']}")

        routes_functions = [x.route for x in self._routes]
        response = chat(model, messages=messages, tools=routes_functions)

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
            Console.log_error(str(e))
            return

        tool = tool_to_call.tool_calls[0]
        function_name = tool.function.name
        function_args = tool.function.arguments

        Console.log_success(f"Calling function: {function_name}")
        Console.log_success(f"Functions args: ({function_args})")

        result: str = ""
        routes_lookup_table = { x.name: x.route for x in self._routes }
        if function_name not in routes_lookup_table.keys():
            return

        match function_name:
            case "get_weather":
                result = routes_lookup_table["get_weather"](**function_args)
            case "get_best_game":
                result = routes_lookup_table["get_best_game"](**function_args)
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
        Console.log_success(f"Response: {final.message.content}")

