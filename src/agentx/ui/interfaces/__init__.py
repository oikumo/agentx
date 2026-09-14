"""UI Interfaces package - re-exports split contracts for backwards compatibility.

Split of the former 910-line ``ui/interfaces.py`` into per-domain modules.
All existing ``from agentx.ui.interfaces import X`` imports keep working.
"""

from __future__ import annotations

from agentx.ui.interfaces.main import IMainView, IMainViewPartner
from agentx.ui.interfaces.chat import IChatView, IChatViewPartner
from agentx.ui.interfaces.rag import IRagView, IRagViewPartner
from agentx.ui.interfaces.react import IReactView, IReactViewPartner
from agentx.ui.interfaces.coding import ICodingView, ICodingViewPartner
from agentx.ui.interfaces.models import IModelsView, IModelsViewPartner
from agentx.ui.interfaces.agent import IAgentView, IConsoleAgentViewPartner, IFastAgentView, IConsoleFastAgentViewPartner
from agentx.ui.interfaces.rag_v2 import IRagV2View, IRagV2ViewPartner, IRagV2CreateRepositoryView, IRagV2CreateRepositoryViewPartner, IRagV2RepositorySelectionView, IRagV2RepositorySelectionViewPartner, IRagV2WebIngestionView, IRagV2WebIngestionViewPartner, IRagV2PdfIngestionView, IRagV2PdfIngestionViewPartner, IRagV2MdIngestionView, IRagV2MdIngestionViewPartner
from agentx.ui.interfaces.provider import IUIProvider

__all__ = [
    "IMainView",
    "IMainViewPartner",
    "IChatView",
    "IChatViewPartner",
    "IRagView",
    "IRagViewPartner",
    "IReactView",
    "IReactViewPartner",
    "ICodingView",
    "ICodingViewPartner",
    "IModelsView",
    "IModelsViewPartner",
    "IAgentView",
    "IConsoleAgentViewPartner",
    "IFastAgentView",
    "IConsoleFastAgentViewPartner",
    "IRagV2View",
    "IRagV2ViewPartner",
    "IRagV2CreateRepositoryView",
    "IRagV2CreateRepositoryViewPartner",
    "IRagV2RepositorySelectionView",
    "IRagV2RepositorySelectionViewPartner",
    "IRagV2WebIngestionView",
    "IRagV2WebIngestionViewPartner",
    "IRagV2PdfIngestionView",
    "IRagV2PdfIngestionViewPartner",
    "IRagV2MdIngestionView",
    "IRagV2MdIngestionViewPartner",
    "IUIProvider",
]
