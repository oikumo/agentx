def parse_chat_arguments(arguments: list[str]) -> tuple[str | None, str]:
    model: str | None = None
    query_parts: list[str] = []

    i = 0
    while i < len(arguments):
        if arguments[i] == "--model":
            if i + 1 < len(arguments):
                model = arguments[i + 1]
                i += 2
            else:
                i += 1
        else:
            query_parts.append(arguments[i])
            i += 1

    query = " ".join(query_parts)
    return model, query
