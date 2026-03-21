class Colors:
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

class Console:
    @staticmethod
    def log_info(message: str, color: str = Colors.CYAN) -> None:
        print(f"{color}ℹ️  {message}{Colors.END}")

    @staticmethod
    def log_success(message: str) -> None:
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")

    @staticmethod
    def log_error(message: str) -> None:
        print(f"{Colors.RED}❌ {message}{Colors.END}")

    @staticmethod
    def log_warning(message: str) -> None:
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

    @staticmethod
    def log_header(message: str) -> None:
        print(f"\n{Colors.BOLD}{Colors.PURPLE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}🚀 {message}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{'=' * 60}{Colors.END}\n")
