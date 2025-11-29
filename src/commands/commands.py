from src.utils.utils import safe_int

def add(arguments):
    match arguments:
        case (x, y):
            if safe_int(x) and safe_int(y):
                result = str(int(x) + int(y))
                return f"-> {result}"
            else:
                return "Invalid params for sum command"
        case _:
            return "Invalid command"