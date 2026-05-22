"""Stdio-safe logging for the knowledge-base library.

The MCP server uses stdio transport: anything written to stdout corrupts the
JSON-RPC stream. All library log output therefore goes through this module,
which routes records to **stderr only**.

Usage:
    from .logging import get_logger
    logger = get_logger()
    logger.warning("something fishy: %s", value)
"""

import logging
import sys

_LOGGER_NAME = "kb"
_CONFIGURED = False


def get_logger() -> logging.Logger:
    """Return the package logger, configuring a stderr handler on first use."""
    global _CONFIGURED
    logger = logging.getLogger(_LOGGER_NAME)
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        _CONFIGURED = True
    return logger
