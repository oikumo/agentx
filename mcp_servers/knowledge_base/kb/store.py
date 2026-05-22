"""Encapsulated ChromaDB persistence for the knowledge base.

`KBStore` owns the ChromaDB client and collection. There are no module-level
globals — callers obtain the default instance via `kb.get_default_store()`
(lazy, process-wide) or instantiate their own (typically in tests, with an
isolated `persist_directory`).

Persistence directory resolution:

* If `persist_directory` is passed explicitly, it is used as-is.
* Otherwise the default is `<this-package>/../chroma_db`, i.e.
  `mcp_servers/knowledge_base/chroma_db/`.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from .logging import get_logger


_DEFAULT_COLLECTION_NAME = "knowledge_base"


class KBStore:
    """ChromaDB persistent client + collection wrapper."""

    def __init__(self, persist_directory: Optional[Path] = None,
                 collection_name: str = _DEFAULT_COLLECTION_NAME):
        if persist_directory is None:
            persist_directory = Path(__file__).resolve().parent.parent / "chroma_db"
        self._persist_directory = Path(persist_directory)
        self._collection_name = collection_name
        self._client = None
        self._collection = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self):
        if self._client is None:
            import chromadb
            self._persist_directory.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self._persist_directory))
        return self._client

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        client = self._get_client()
        existing = client.list_collections()
        if any(c.name == self._collection_name for c in existing):
            self._collection = client.get_collection(name=self._collection_name)
        else:
            self._collection = client.create_collection(
                name=self._collection_name,
                metadata={
                    "description": "Meta Project Harness Knowledge Base",
                    "created_at": datetime.now().isoformat(),
                },
            )
        return self._collection

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def persist_directory(self) -> Path:
        return self._persist_directory

    @property
    def collection(self):
        """Return the live ChromaDB collection (lazy)."""
        return self._get_collection()

    def count(self) -> int:
        return self.collection.count()

    def add(self, *, entry_id: str, document_text: str,
            metadata: Dict[str, Any]) -> None:
        """Insert one entry into the collection."""
        self.collection.add(
            documents=[document_text],
            metadatas=[metadata],
            ids=[entry_id],
        )

    def sample_metadata(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Return up to `limit` metadata dicts (for stats computation)."""
        sample = self.collection.get(limit=limit)
        if not sample or "metadatas" not in sample or not sample["metadatas"]:
            return []
        return [m for m in sample["metadatas"] if m]

    def reset(self) -> None:
        """Delete and recreate the collection. All entries are lost."""
        logger = get_logger()
        client = self._get_client()
        try:
            existing = client.list_collections()
            if any(c.name == self._collection_name for c in existing):
                client.delete_collection(name=self._collection_name)
        except Exception as exc:  # collection may not exist; that's fine
            logger.warning("Ignoring delete_collection error: %s", exc)

        self._collection = client.create_collection(
            name=self._collection_name,
            metadata={
                "description": "Meta Project Harness Knowledge Base",
                "created_at": datetime.now().isoformat(),
            },
        )


# ---------------------------------------------------------------------------
# Default store (lazy, process-wide)
# ---------------------------------------------------------------------------

_default_store: Optional[KBStore] = None


def get_default_store() -> KBStore:
    """Return (and lazily create) the process-wide default `KBStore`."""
    global _default_store
    if _default_store is None:
        _default_store = KBStore()
    return _default_store


def set_default_store(store: Optional[KBStore]) -> None:
    """Override the process-wide default store. Pass `None` to clear it."""
    global _default_store
    _default_store = store
