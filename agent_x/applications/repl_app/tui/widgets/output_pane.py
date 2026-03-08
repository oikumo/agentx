"""OutputPane — scrollable Rich-markup output pane for the TUI.

Extends Textual's RichLog widget so that all the Rich markup styling
(bold, colours, tables) is rendered automatically.  The TuiOutputWriter
calls write() on this widget via a registered callback.
"""

from textual.widgets import RichLog


class OutputPane(RichLog):
    """Scrollable output area that renders Rich markup.

    Usage (inside a Textual App compose()):
        yield OutputPane(id="output-pane", wrap=True, highlight=True, markup=True)

    Usage from TuiOutputWriter callback:
        writer.set_callback(lambda m: output_pane.write(m))
    """

    DEFAULT_CSS = """
    OutputPane {
        border: solid $primary-darken-2;
        padding: 0 1;
        scrollbar-gutter: stable;
    }
    """

    def __init__(self, **kwargs) -> None:
        # Enable markup + highlight by default so Rich tags are rendered.
        kwargs.setdefault("markup", True)
        kwargs.setdefault("highlight", True)
        kwargs.setdefault("wrap", True)
        super().__init__(**kwargs)
