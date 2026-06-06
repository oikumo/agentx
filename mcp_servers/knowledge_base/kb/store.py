"""Encapsulated ChromaDB persistence for the knowledge base.

`KBStore` owns the ChromaDB client and collection. There are no module-level
globals — callers obtain the default instance via `kb.get_default_store()`
(lazy, process-wide) or instantiate their own (typically in tests, with an
isolated `persist_directory`).

Persistence directory resolution:

* If `persist_directory` is passed explicitly, it is used as-is.
* Otherwise the default is `<this-package>/../chroma_db`, i.e.
  `mcp_servers/knowledge_base/chroma_db/`.

Multi-collection support:

* Each embedding model gets its own collection (``kb_dense_{model_name}``).
* The original ``knowledge_base`` collection is used as the metadata store
  for parent-child chunk relationships.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from .logging import get_logger


_DEFAULT_COLLECTION_NAME = "knowledge_base"


class KBStore:
    """ChromaDB persistent client + collection wrapper.

    Supports multiple named collections for different embedding models
    and a primary collection for chunk metadata tracking.
    """

    def __init__(self, persist_directory: Optional[Path] = None,
                 collection_name: str = _DEFAULT_COLLECTION_NAME):
        if persist_directory is None:
            persist_directory = Path(__file__).resolve().parent.parent / "chroma_db"
        self._persist_directory = Path(persist_directory)
        self._collection_name = collection_name
        self._client = None
        self._collection = None
        self._collections: Dict[str, Any] = {}

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
        return self.get_or_create_collection(self._collection_name)

    def get_or_create_collection(self, name: str,
                                 embedding_function: Optional[Any] = None) -> Any:
        """Return an existing collection by name, or create it.

        Args:
            name: Collection name (e.g., ``"kb_dense_bge-small-en"``).
            embedding_function: Optional ChromaDB embedding function to use
                                for this collection. If None, uses the default
                                (ONNX all-MiniLM-L6-v2).

        Returns:
            A ChromaDB ``Collection`` object.
        """
        if name in self._collections:
            return self._collections[name]

        client = self._get_client()
        existing = client.list_collections()
        match = [c for c in existing if c.name == name]

        if match:
            col = match[0]
        else:
            kwargs = {
                "name": name,
                "metadata": {
                    "description": f"KB collection: {name}",
                    "created_at": datetime.now().isoformat(),
                },
            }
            if embedding_function is not None:
                kwargs["embedding_function"] = embedding_function
            col = client.create_collection(**kwargs)

        self._collections[name] = col
        if name == self._collection_name:
            self._collection = col
        return col

    def list_collections(self) -> List[str]:
        """Return the names of all known collections."""
        client = self._get_client()
        return [c.name for c in client.list_collections()]

    def delete_collection(self, name: str) -> None:
        """Delete a collection by name."""
        client = self._get_client()
        self._collections.pop(name, None)
        if self._collection_name == name:
            self._collection = None
        try:
            client.delete_collection(name=name)
        except Exception as exc:
            get_logger().warning("delete_collection(%s) error: %s", name, exc)

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

    def count(self, collection_name: Optional[str] = None) -> int:
        """Count entries in a collection (default: primary collection)."""
        if collection_name:
            col = self.get_or_create_collection(collection_name)
            return col.count()
        return self.collection.count()

    def add(self, *, entry_id: str, document_text: str,
            metadata: Dict[str, Any],
            collection_name: Optional[str] = None) -> None:
        """Insert one entry into the collection.

        Args:
            entry_id: Unique ID for the entry.
            document_text: The document text to embed.
            metadata: Metadata dict to store alongside.
            collection_name: Target collection (default: primary).
        """
        col = self.get_or_create_collection(
            collection_name or self._collection_name
        )
        col.add(
            documents=[document_text],
            metadatas=[metadata],
            ids=[entry_id],
        )

    def add_chunks(self, *, chunks: List[Any],
                   collection_name: Optional[str] = None) -> List[str]:
        """Add multiple chunk entries to a collection.

        Args:
            chunks: List of ``Chunk`` objects (from ``kb.chunking``).
            collection_name: Target collection (default: primary).

        Returns:
            List of chunk IDs that were added.
        """
        if not chunks:
            return []

        chunk_ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            cid = f"{chunk.parent_id}_chunk_{chunk.chunk_index:04d}"
            chunk_ids.append(cid)
            documents.append(chunk.text)
            metadatas.append({
                "entry_id": cid,
                "parent_id": chunk.parent_id,
                "chunk_index": chunk.chunk_index,
                "chunk_type": chunk.chunk_type,
                "section_hierarchy": " > ".join(chunk.section_hierarchy),
                "chunk_count": chunk.metadata.get("chunk_count", 1),
                **chunk.metadata,
            })

        col = self.get_or_create_collection(
            collection_name or self._collection_name
        )
        col.add(
            documents=documents,
            metadatas=metadatas,
            ids=chunk_ids,
        )
        return chunk_ids

    def get(self, entry_id: str,
            collection_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a single entry by ID from a collection."""
        col = self.get_or_create_collection(
            collection_name or self._collection_name
        )
        result = col.get(ids=[entry_id])
        if result and result["ids"] and result["ids"][0]:
            return {
                "id": result["ids"][0],
                "document": result["documents"][0] if result.get("documents") else "",
                "metadata": result["metadatas"][0] if result.get("metadatas") else {},
            }
        return None

    def get_children(self, parent_id: str,
                     collection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all chunks belonging to a parent entry."""
        col = self.get_or_create_collection(
            collection_name or self._collection_name
        )
        # ChromaDB doesn't support regex, so we get all and filter
        all_data = col.get()
        if not all_data or not all_data["ids"]:
            return []

        children = []
        for i, cid in enumerate(all_data["ids"]):
            meta = all_data["metadatas"][i] if all_data.get("metadatas") else {}
            if meta and meta.get("parent_id") == parent_id:
                children.append({
                    "id": cid,
                    "document": all_data["documents"][i] if all_data.get("documents") else "",
                    "metadata": meta,
                })
        return sorted(children, key=lambda x: x["metadata"].get("chunk_index", 0))

    def sample_metadata(self, limit: int = 1000,
                        collection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return up to ``limit`` metadata dicts from a collection."""
        col = self.get_or_create_collection(
            collection_name or self._collection_name
        )
        sample = col.get(limit=limit)
        if not sample or "metadatas" not in sample or not sample["metadatas"]:
            return []
        return [m for m in sample["metadatas"] if m]

    def reset(self, collection_name: Optional[str] = None) -> None:
        """Delete and recreate a collection. All entries are lost.

        Args:
            collection_name: Collection to reset (default: primary).
        """
        logger = get_logger()
        target = collection_name or self._collection_name
        client = self._get_client()
        try:
            existing = client.list_collections()
            if any(c.name == target for c in existing):
                client.delete_collection(name=target)
        except Exception as exc:
            logger.warning("Ignoring delete_collection error: %s", exc)

        self._collections.pop(target, None)
        if target == self._collection_name:
            self._collection = None

        new_col = client.create_collection(
            name=target,
            metadata={
                "description": f"KB collection: {target}",
                "created_at": datetime.now().isoformat(),
            },
        )
        self._collections[target] = new_col
        if target == self._collection_name:
            self._collection = new_col

    def query(self, query_texts: List[str], n_results: int = 10,
              where: Optional[Dict[str, Any]] = None,
              collection_name: Optional[str] = None,
              include: Optional[List[str]] = None) -> Any:
        """Run a query against a collection.

        Args:
            query_texts: List of query strings.
            n_results: Number of results to return.
            where: Optional metadata filter.
            collection_name: Target collection (default: primary).
            include: What to include in results.

        Returns:
            Raw ChromaDB query result.
        """
        col = self.get_or_create_collection(
            collection_name or self._collection_name
        )
        kwargs: Dict[str, Any] = {
            "query_texts": query_texts,
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where
        if include:
            kwargs["include"] = include
        return col.query(**kwargs)


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
