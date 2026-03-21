from typing import Callable


class Route:
    def __init__(self, function_name: str, route: Callable):
        self.name = function_name
        self.route = route
    def run(self, args):
        self.route(args)

