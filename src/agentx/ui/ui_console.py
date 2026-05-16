from agentx.ui.ui import UIConsoleBase, UIMessage, UIMessageType

class UIConsoleColors:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class UIPrompt:
    base: str
    parts: list[str]

    def __init__(self, base: str, parts: list[str] | None = None) -> None:
        self.base = base or ""
        self.parts = list(parts or [])

    def prompt(self) -> str:
        suffix = "/" + "/".join(self.parts) if self.parts else ""
        return f"({self.base}{suffix}) "

    def reset_prompt(self) -> None:
        self.parts.clear()

class UIConsole(UIConsoleBase):

    def __init__(self, ui_prompt: UIPrompt):
        super().__init__()
        self.ui_prompt = ui_prompt

    def reset_prompt(self) -> None:
        self.ui_prompt.reset_prompt()

    def set_prompt_additional(self, part: str):
        self.ui_prompt.parts.append(part)


    def print_now(self, message: str) -> None:
        print(message, end="", flush=True)

    def capture_input(self) -> str | None:
        try:
            user_input = input(self.ui_prompt.prompt()).strip()
            if user_input:
                return user_input

        except KeyboardInterrupt:
            self.print_line(UIMessage("received interrupt, exiting...", UIMessageType.ERROR))
        except EOFError:
            self.print_line(UIMessage("EOF received, exiting...", UIMessageType.ERROR))

        return None


    def print_line(self, line: UIMessage) -> None :
        match line.message_type:
            case UIMessageType.INFO:
                print(f"{UIConsoleColors.DARKCYAN} {line.message}{UIConsoleColors.END}")

            case UIMessageType.SUCCESS:
                print(f"{UIConsoleColors.GREEN}✅ {line.message}{UIConsoleColors.END}")

            case UIMessageType.ERROR:
                print(f"{UIConsoleColors.RED}❌ {line.message}{UIConsoleColors.END}")

            case UIMessageType.WARNING:
                print(f"{UIConsoleColors.YELLOW}⚠️ {line.message}{UIConsoleColors.END}")

            case UIMessageType.HEADER:
                print(f"\n{UIConsoleColors.BOLD}{UIConsoleColors.PURPLE}{'=' * 60}{UIConsoleColors.END}")
                print(f"{UIConsoleColors.BOLD}{UIConsoleColors.PURPLE}🚀 {line.message}{UIConsoleColors.END}")
                print(f"{UIConsoleColors.BOLD}{UIConsoleColors.PURPLE}{'=' * 60}{UIConsoleColors.END}\n")








