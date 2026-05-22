"""pytest configuration: put the package root on sys.path so `import kb` works."""

import sys
from pathlib import Path

# Repo layout: mcp_servers/knowledge_base/tests/conftest.py
# Parent of `tests/` holds both `kb/` and `server.py`.
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))
