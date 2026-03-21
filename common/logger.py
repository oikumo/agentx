# Color codes for better logging
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


# ---------------------------------------------------------------------------
# Output handler registry
#
# All log_* functions delegate to the active handler.  The default handler
# prints to stdout with ANSI colours.  The TUI replaces it with a handler
# that writes to the OutputPane.
#
# Because every caller holds a reference to the *function* (log_info, etc.)
# and those functions always call _handler.*, redirecting the handler object
# is enough — no monkey-patching of module attributes is needed.
# ---------------------------------------------------------------------------


class _DefaultHandler:
    """Prints log messages to stdout with ANSI colour codes."""

    def info(self, message: str, color: str = Colors.CYAN) -> None:
        print(f"{color}ℹ️  {message}{Colors.END}")

    def success(self, message: str) -> None:
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")

    def error(self, message: str) -> None:
        print(f"{Colors.RED}❌ {message}{Colors.END}")

    def warning(self, message: str) -> None:
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

    def header(self, message: str) -> None:
        print(f"\n{Colors.BOLD}{Colors.PURPLE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}🚀 {message}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{'=' * 60}{Colors.END}\n")


_handler: _DefaultHandler = _DefaultHandler()


def set_handler(handler) -> None:
    """Replace the active log handler.

    The handler must expose ``info``, ``success``, ``error``, ``warning``,
    and ``header`` methods with the same signatures as :class:`_DefaultHandler`.

    Call ``set_handler(_DefaultHandler())`` to restore the default behaviour.
    """
    global _handler
    _handler = handler


def get_handler():
    """Return the currently active log handler."""
    return _handler


# ---------------------------------------------------------------------------
# Public API (unchanged call sites)
# ---------------------------------------------------------------------------


def log_info(message: str, color: str = Colors.CYAN):
    """Log info message with color"""
    _handler.info(message, color)


def log_success(message: str):
    """Log success message in green"""
    _handler.success(message)


def log_error(message: str):
    """Log error message in red"""
    _handler.error(message)


def log_warning(message: str):
    """Log warning message in yellow"""
    _handler.warning(message)


def log_header(message: str):
    """Log header message with emphasis"""
    _handler.header(message)
