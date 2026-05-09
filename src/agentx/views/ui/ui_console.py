from agentx.views.ui.ui import UIConsoleBase, UIMessage, UIMessageType

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


class UIConsole(UIConsoleBase):

    def print_now(self, message: str) -> None:
        print(message, end="", flush=True)

    def capture_input(self, mode_text: str) -> str | None:
        try:
            user_input = input(mode_text).strip()
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








