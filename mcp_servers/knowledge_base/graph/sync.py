#!/usr/bin/env python3
"""
Knowledge Graph Incremental Sync for KB MCP v4.

Provides incremental synchronization with git repository to track changes
and update only affected entities in the knowledge graph.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .engine import KnowledgeGraph
from .models import Entity


class GraphSync:
    """
    Incremental git sync for knowledge graph.
    
    This class tracks git commits and only re-analyzes changed files,
    making graph updates efficient for large codebases.
    
    Attributes:
        graph: The KnowledgeGraph to sync
        repo_path: Path to git repository
        last_sync_commit: Hash of last synced commit
    """
    
    def __init__(self, graph: KnowledgeGraph, repo_path: str):
        """
        Initialize graph sync.
        
        Args:
            graph: The KnowledgeGraph instance to sync
            repo_path: Path to the git repository root
        """
        self._graph = graph
        self._repo_path = Path(repo_path)
        self._last_sync_commit: Optional[str] = None
        self._stale_entities: set[str] = set()
        self._sync_metadata: dict[str, Any] = {}
    
    def sync(self) -> dict[str, Any]:
        """
        Perform incremental sync from git.
        
        Returns:
            Dictionary with sync statistics:
            - files_changed: Number of files changed
            - entities_updated: Number of entities updated
            - entities_deleted: Number of entities deleted
            - new_commit: New HEAD commit hash
        """
        if not self._is_git_repo():
            raise ValueError(f"Not a git repository: {self._repo_path}")
        
        current_commit = self._get_head_commit()
        
        if not current_commit:
            return {
                "files_changed": 0,
                "entities_updated": 0,
                "entities_deleted": 0,
                "new_commit": None,
                "warnings": ["No commits found in repository"],
            }
        
        changed_files = self._get_changed_files_since(self._last_sync_commit)
        
        stats = {
            "files_changed": len(changed_files),
            "entities_updated": 0,
            "entities_deleted": 0,
            "new_commit": current_commit,
            "changed_files": changed_files,
        }
        
        for file_path in changed_files:
            entities_updated = self._update_entities_in_file(file_path)
            stats["entities_updated"] += entities_updated
        
        deleted_count = self._detect_deletions(changed_files)
        stats["entities_deleted"] = deleted_count
        
        self._last_sync_commit = current_commit
        self._sync_metadata["last_sync"] = datetime.now().isoformat()
        self._sync_metadata["total_syncs"] = self._sync_metadata.get("total_syncs", 0) + 1
        
        return stats
    
    def get_changed_since(self, commit_hash: str) -> list[str]:
        """
        Get list of files changed since a specific commit.
        
        Args:
            commit_hash: Git commit hash to compare against
            
        Returns:
            List of file paths that changed since the commit
        """
        if not self._is_git_repo():
            return []
        
        return self._get_changed_files_since(commit_hash)
    
    def mark_stale(self, entity_id: str) -> None:
        """
        Mark an entity as stale (needs re-analysis).
        
        Args:
            entity_id: The entity ID to mark as stale
        """
        self._stale_entities.add(entity_id)
    
    def get_stale_entities(self) -> set[str]:
        """
        Get set of stale entity IDs.
        
        Returns:
            Set of entity IDs marked as stale
        """
        return self._stale_entities.copy()
    
    def clear_stale(self) -> None:
        """Clear all stale entity markers."""
        self._stale_entities.clear()
    
    def get_sync_metadata(self) -> dict[str, Any]:
        """
        Get sync metadata.
        
        Returns:
            Dictionary with sync metadata
        """
        return self._sync_metadata.copy()
    
    def _is_git_repo(self) -> bool:
        """Check if repo_path is a valid git repository."""
        git_dir = self._repo_path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def _get_head_commit(self) -> Optional[str]:
        """Get current HEAD commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, OSError):
            pass
        return None
    
    def _get_changed_files_since(self, commit_hash: Optional[str]) -> list[str]:
        """
        Get files changed since a commit.
        
        Args:
            commit_hash: Previous commit hash, or None for all files
            
        Returns:
            List of changed file paths (relative to repo root)
        """
        try:
            if commit_hash:
                cmd = ["git", "diff", "--name-only", commit_hash]
            else:
                cmd = ["git", "ls-files"]
            
            result = subprocess.run(
                cmd,
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
                return files
        except (subprocess.SubprocessError, OSError):
            pass
        
        return []
    
    def _update_entities_in_file(self, file_path: str) -> int:
        """
        Update entities for a changed file.
        
        This method should be integrated with the graph builder
        to re-analyze the file and update affected entities.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            Number of entities updated
        """
        full_path = self._repo_path / file_path
        
        if not full_path.exists():
            return self._remove_entities_for_file(file_path)
        
        entities_updated = 0
        
        for entity in self._graph.get_all_entities():
            if entity.file_path == str(full_path):
                entity_id = entity.id
                self._stale_entities.add(entity_id)
                entities_updated += 1
        
        return entities_updated
    
    def _remove_entities_for_file(self, file_path: str) -> int:
        """
        Remove all entities for a deleted file.
        
        Args:
            file_path: Relative path to the deleted file
            
        Returns:
            Number of entities removed
        """
        full_path = str(self._repo_path / file_path)
        entities_removed = 0
        
        for entity in self._graph.get_all_entities():
            if entity.file_path == full_path:
                if self._graph.remove_entity(entity.id):
                    entities_removed += 1
        
        return entities_removed
    
    def _detect_deletions(self, changed_files: list[str]) -> int:
        """
        Detect and handle deleted files.
        
        Args:
            changed_files: List of files that changed
            
        Returns:
            Number of entities deleted
        """
        deleted_count = 0
        
        for file_path in changed_files:
            full_path = self._repo_path / file_path
            
            if not full_path.exists():
                removed = self._remove_entities_for_file(file_path)
                deleted_count += removed
        
        return deleted_count
    
    def sync_from_git(self, branch: Optional[str] = None) -> dict[str, Any]:
        """
        Sync graph from git repository.
        
        This is the main entry point for syncing the knowledge graph
        with the git repository state.
        
        Args:
            branch: Optional branch to checkout before syncing
            
        Returns:
            Sync statistics dictionary
        """
        if branch:
            self._checkout_branch(branch)
        
        return self.sync()
    
    def _checkout_branch(self, branch: str) -> bool:
        """
        Checkout a specific branch.
        
        Args:
            branch: Branch name to checkout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False
    
    def detect_deletions(self) -> list[str]:
        """
        Detect files that were deleted from git.
        
        Returns:
            List of deleted file paths
        """
        deleted_files = []
        
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status", "HEAD"],
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("D\t"):
                        deleted_files.append(line.split("\t", 1)[1])
        except (subprocess.SubprocessError, OSError):
            pass
        
        return deleted_files
    
    def get_commit_info(self, commit_hash: str) -> Optional[dict[str, Any]]:
        """
        Get information about a specific commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            Dictionary with commit info or None if not found
        """
        try:
            result = subprocess.run(
                ["git", "show", "-s", "--format=%H|%an|%ae|%ai|%s", commit_hash],
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|")
                if len(parts) >= 5:
                    return {
                        "hash": parts[0],
                        "author_name": parts[1],
                        "author_email": parts[2],
                        "date": parts[3],
                        "message": parts[4],
                    }
        except (subprocess.SubprocessError, OSError):
            pass
        
        return None
    
    def get_recent_commits(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Get recent commits.
        
        Args:
            count: Number of commits to retrieve
            
        Returns:
            List of commit info dictionaries
        """
        commits = []
        
        try:
            result = subprocess.run(
                ["git", "log", "-n", str(count), "--format=%H|%an|%ae|%ai|%s"],
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    parts = line.strip().split("|")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                        })
        except (subprocess.SubprocessError, OSError):
            pass
        
        return commits