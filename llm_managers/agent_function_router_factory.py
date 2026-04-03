from agents.function_tool_router.function_call import QueryRouter
from agents.function_tool_router.functions import get_weather, get_best_game
from agents.function_tool_router.route import Route


def create_agent_function_router_local():
    routes = [
        Route("get_weather", get_weather),
        Route("get_best_game", get_best_game)
    ]
    return QueryRouter(routes)