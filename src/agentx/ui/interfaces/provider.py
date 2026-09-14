"""UI Interfaces - provider contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

class IUIProvider(ABC):
    """Abstract factory for UI components.
    
    This is the main dependency inversion interface.
    Controllers request views through this provider, never creating them directly.
    """

    @abstractmethod
    def create_main_view(self, controller: "IMainViewPartner") -> IMainView:
        """Create main view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IMainView implementation
        """
        pass

    @abstractmethod
    def create_rag_view(self, controller: "IRagViewPartner") -> IRagView:
        """Create RAG view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IRagView implementation
        """
        pass

    # --- RAG v2 (feature_027) — console-only sibling factories ---

    @abstractmethod
    def create_rag_v2_view(self, controller: "IRagV2ViewPartner") -> "IRagV2View":
        """Create the console RAG v2 outer view implementation."""
        pass

    @abstractmethod
    def create_rag_v2_create_repository_view(self, controller) -> "IRagV2CreateRepositoryView":
        """Create the console RAG v2 create-repository sub-screen view."""
        pass

    @abstractmethod
    def create_rag_v2_repository_selection_view(self, controller) -> "IRagV2RepositorySelectionView":
        """Create the console RAG v2 repository-selection sub-screen view."""
        pass

    @abstractmethod
    def create_rag_v2_web_ingestion_view(self, controller) -> "IRagV2WebIngestionView":
        """Create the console RAG v2 web-ingestion sub-screen view."""
        pass

    @abstractmethod
    def create_rag_v2_pdf_ingestion_view(self, controller) -> "IRagV2PdfIngestionView":
        """Create the console RAG v2 PDF-ingestion sub-screen view."""
        pass

    @abstractmethod
    def create_rag_v2_md_ingestion_view(self, controller) -> "IRagV2MdIngestionView":
        """Create the console RAG v2 MD-ingestion sub-screen view."""
        pass
    @abstractmethod
    def create_chat_view(self, controller: "IChatViewPartner") -> IChatView:
        """Create chat view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IChatView implementation
        """
        pass

    # --- New methods for console parity (feature_024) ---

    @abstractmethod
    def create_react_view(self, controller: "IReactViewPartner") -> "IReactView":
        """Create ReAct view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IReactView implementation
        """
        pass

    @abstractmethod
    def create_coding_view(self, controller: "ICodingViewPartner") -> "ICodingView":
        """Create Coding view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            ICodingView implementation
        """
        pass

    @abstractmethod
    def create_models_view(self, controller: "IModelsViewPartner") -> "IModelsView":
        """Create Models selector view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IModelsView implementation
        """
        pass

    @abstractmethod
    def create_agent_view(self, controller: "IConsoleAgentViewPartner") -> "IAgentView":
        """Create Advanced Agent view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IAgentView implementation
        """
        pass

    @abstractmethod
    def create_fast_agent_view(self, controller: "IConsoleFastAgentViewPartner") -> "IFastAgentView":
        """Create Fast Agent view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IFastAgentView implementation
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize UI framework."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup UI resources."""
        pass
