#!/usr/bin/env python3
"""
SQLite persistence layer for Knowledge Graph.

Provides durable storage and loading of graph data.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from .engine import KnowledgeGraph
from .models import DocstringInfo, Entity, EntityKind, GraphMetadata, Relationship, RelationshipKind


class GraphStore:
    """
    SQLite-backed persistence for KnowledgeGraph.
    
    Stores entities and relationships in SQLite tables for durability
    across server restarts.
    """
    
    def __init__(self, db_path: Path | str):
        """
        Initialize the graph store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.executescript("""
                -- Entities table
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_start INTEGER NOT NULL,
                    line_end INTEGER NOT NULL,
                    docstring_json TEXT,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                );
                
                -- Relationships table
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    metadata_json TEXT,
                    FOREIGN KEY (source_id) REFERENCES entities(id),
                    FOREIGN KEY (target_id) REFERENCES entities(id)
                );
                
                -- Metadata table (single row)
                CREATE TABLE IF NOT EXISTS graph_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                
                -- Indices for performance
                CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id);
                CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id);
                CREATE INDEX IF NOT EXISTS idx_entity_kind ON entities(kind);
                CREATE INDEX IF NOT EXISTS idx_entity_file ON entities(file_path);
            """)
            conn.commit()
        finally:
            conn.close()
    
    def save(self, graph: KnowledgeGraph) -> None:
        """
        Save graph to SQLite database.
        
        Args:
            graph: The KnowledgeGraph to save
            
        Note:
            This is a full save - clears and recreates all data.
            Uses transactions for atomicity.
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Clear existing data
            conn.execute("DELETE FROM relationships")
            conn.execute("DELETE FROM entities")
            conn.execute("DELETE FROM graph_metadata")
            
            # Save entities
            for entity in graph.get_all_entities():
                docstring_json = None
                if entity.docstring:
                    docstring_json = json.dumps({
                        "summary": entity.docstring.summary,
                        "description": entity.docstring.description,
                        "args": entity.docstring.args,
                        "returns": entity.docstring.returns,
                        "raises": entity.docstring.raises,
                        "examples": entity.docstring.examples,
                    })
                
                conn.execute(
                    """
                    INSERT INTO entities (id, kind, name, file_path, line_start, line_end, 
                                         docstring_json, metadata_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entity.id,
                        entity.kind.value if isinstance(entity.kind, EntityKind) else entity.kind,
                        entity.name,
                        entity.file_path,
                        entity.line_start,
                        entity.line_end,
                        docstring_json,
                        json.dumps(entity.metadata),
                        entity.created_at.isoformat(),
                    ),
                )
            
            # Save relationships
            for rel in graph.get_all_relationships():
                conn.execute(
                    """
                    INSERT INTO relationships (source_id, target_id, kind, metadata_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        rel.source_id,
                        rel.target_id,
                        rel.kind.value if isinstance(rel.kind, RelationshipKind) else rel.kind,
                        json.dumps(rel.metadata),
                    ),
                )
            
            # Save metadata
            metadata = [
                ("total_entities", str(graph.metadata.total_entities)),
                ("total_relationships", str(graph.metadata.total_relationships)),
                ("created_at", graph.metadata.created_at.isoformat()),
                ("updated_at", graph.metadata.updated_at.isoformat()),
                ("version", graph.metadata.version),
                ("project_root", graph.metadata.project_root or ""),
                ("languages", json.dumps(graph.metadata.languages)),
            ]
            
            for key, value in metadata:
                conn.execute(
                    "INSERT INTO graph_metadata (key, value) VALUES (?, ?)",
                    (key, value),
                )
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def load(self) -> Optional[KnowledgeGraph]:
        """
        Load graph from SQLite database.
        
        Returns:
            KnowledgeGraph or None if database is empty
            
        Note:
            Returns None if no entities exist in database.
        """
        if not self.db_path.exists():
            return None
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            
            # Check if we have any entities
            cursor.execute("SELECT COUNT(*) FROM entities")
            count = cursor.fetchone()[0]
            if count == 0:
                return None
            
            graph = KnowledgeGraph()
            
            # Load entities
            cursor.execute("SELECT * FROM entities")
            for row in cursor.fetchall():
                docstring = None
                if row["docstring_json"]:
                    ds_data = json.loads(row["docstring_json"])
                    docstring = DocstringInfo(
                        summary=ds_data.get("summary", ""),
                        description=ds_data.get("description", ""),
                        args=ds_data.get("args", {}),
                        returns=ds_data.get("returns"),
                        raises=ds_data.get("raises", []),
                        examples=ds_data.get("examples", []),
                    )
                
                entity = Entity(
                    id=row["id"],
                    kind=EntityKind(row["kind"]),
                    name=row["name"],
                    file_path=row["file_path"],
                    line_start=row["line_start"],
                    line_end=row["line_end"],
                    docstring=docstring,
                    metadata=json.loads(row["metadata_json"]) if row["metadata_json"] else {},
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                graph.add_entity(entity)
            
            # Load relationships
            cursor.execute("SELECT * FROM relationships")
            for row in cursor.fetchall():
                rel = Relationship(
                    id=row["id"],
                    source_id=row["source_id"],
                    target_id=row["target_id"],
                    kind=RelationshipKind(row["kind"]),
                    metadata=json.loads(row["metadata_json"]) if row["metadata_json"] else {},
                )
                graph.add_relationship(rel)
            
            # Load metadata
            cursor.execute("SELECT key, value FROM graph_metadata")
            for row in cursor.fetchall():
                key, value = row["key"], row["value"]
                
                if key == "total_entities":
                    graph._metadata.total_entities = int(value)
                elif key == "total_relationships":
                    graph._metadata.total_relationships = int(value)
                elif key == "created_at":
                    graph._metadata.created_at = datetime.fromisoformat(value)
                elif key == "updated_at":
                    graph._metadata.updated_at = datetime.fromisoformat(value)
                elif key == "version":
                    graph._metadata.version = value
                elif key == "project_root":
                    graph._metadata.project_root = value if value else None
                elif key == "languages":
                    graph._metadata.languages = json.loads(value)
            
            return graph
            
        finally:
            conn.close()
    
    def save_entity(self, entity: Entity) -> None:
        """
        Save or update a single entity.
        
        Args:
            entity: The entity to save
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            docstring_json = None
            if entity.docstring:
                docstring_json = json.dumps({
                    "summary": entity.docstring.summary,
                    "description": entity.docstring.description,
                    "args": entity.docstring.args,
                    "returns": entity.docstring.returns,
                    "raises": entity.docstring.raises,
                    "examples": entity.docstring.examples,
                })
            
            conn.execute(
                """
                INSERT OR REPLACE INTO entities (id, kind, name, file_path, line_start, line_end,
                                                 docstring_json, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity.id,
                    entity.kind.value if isinstance(entity.kind, EntityKind) else entity.kind,
                    entity.name,
                    entity.file_path,
                    entity.line_start,
                    entity.line_end,
                    docstring_json,
                    json.dumps(entity.metadata),
                    entity.created_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    
    def save_relationship(self, relationship: Relationship) -> None:
        """
        Save or update a single relationship.
        
        Args:
            relationship: The relationship to save
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                """
                INSERT INTO relationships (source_id, target_id, kind, metadata_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    relationship.source_id,
                    relationship.target_id,
                    relationship.kind.value if isinstance(relationship.kind, RelationshipKind) else relationship.kind,
                    json.dumps(relationship.metadata),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    
    def remove_entity(self, entity_id: str) -> None:
        """
        Remove an entity and its relationships.
        
        Args:
            entity_id: The entity ID to remove
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            # Delete relationships first (both source and target)
            conn.execute(
                "DELETE FROM relationships WHERE source_id = ? OR target_id = ?",
                (entity_id, entity_id),
            )
            # Then delete the entity
            conn.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_entity_count(self) -> int:
        """Get total number of entities in database."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM entities")
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_relationship_count(self) -> int:
        """Get total number of relationships in database."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM relationships")
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def exists(self) -> bool:
        """Check if database exists and has data."""
        if not self.db_path.exists():
            return False
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM entities")
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()
    
    def backup(self, backup_path: Path | str) -> None:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path to backup file
        """
        import shutil
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(self.db_path), str(backup_path))