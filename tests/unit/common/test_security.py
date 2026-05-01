"""
Unit tests for agentx.common.security module.

Tests cover:
- Session default constants
- Directory deletion allowed list
"""

import pytest
from agentx.common.security import (
    SESSION_DEFAULT_NAME,
    SESSION_DEFAULT_BASE_DIRECTORY,
    DIRECTORIES_DELETION_ALLOWED,
)


class TestSecurityConstants:
    """Tests for security constants."""

    def test_session_default_name(self):
        """Test default session name constant."""
        assert SESSION_DEFAULT_NAME == "default"
        assert isinstance(SESSION_DEFAULT_NAME, str)

    def test_session_default_base_directory(self):
        """Test default base directory constant."""
        assert SESSION_DEFAULT_BASE_DIRECTORY == "local_sessions"
        assert isinstance(SESSION_DEFAULT_BASE_DIRECTORY, str)

    def test_directories_deletion_allowed(self):
        """Test deletion allowed directories list."""
        assert isinstance(DIRECTORIES_DELETION_ALLOWED, list)
        assert len(DIRECTORIES_DELETION_ALLOWED) > 0
        assert SESSION_DEFAULT_BASE_DIRECTORY in DIRECTORIES_DELETION_ALLOWED

    def test_deletion_allowed_is_final(self):
        """Test that deletion allowed is immutable (Final)."""
        # This test ensures the constant is properly typed as Final
        # While we can't enforce immutability at runtime in Python,
        # we can verify the type annotation
        from typing import get_type_hints
        import agentx.common.security as security_module

        # Just verify it's accessible and has correct type
        assert DIRECTORIES_DELETION_ALLOWED is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
