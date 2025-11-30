from src.utils.utils import safe_int

def add(arguments):
    match arguments:
        case (x, y):
            if safe_int(x) and safe_int(y):
                result = str(int(x) + int(y))
                return f"{result}"
            else:
                return "invalid params for sum command"
        case _:
            return "invalid command"