import pytest
import os
from unittest.mock import patch, MagicMock
from agent_x.utils.utils import safe_int
from agent_x.models.config import Config

@pytest.fixture
def sample_config():
    """Sample configuration for tests"""
    return Config(
        api_key="test_key",
        model="gpt-3.5-turbo",
        max_tokens=4096,
        temperature=0.7,
        base_url="http://localhost:8000"
    )

@pytest.fixture
def sample_api_response():
    """Sample API response for mocking"""
    return {
        "id": "test_message_id",
        "object": "message",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a sample response"
            }
        }]
    }

@pytest.fixture
def mock_api_client(sample_api_response):
    """Mocked API client for testing"""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = sample_api_response
    return mock_client

@pytest.fixture
def sample_user_session():
    """Sample user session data"""
    return {
        "session_id": "test_session_123",
        "user_id": "test_user_456",
        "messages": [],
        "context": {},
        "metadata": {}
    }

@pytest.fixture
def sample_test_data():
    """Sample test data factory"""
    class TestData:
        @staticmethod
        def create_message(content, role="user"):
            return {
                "role": role,
                "content": content,
                "created_at": "2024-01-01T00:00:00Z"
            }

        @staticmethod
        def create_error_response(error_type, message):
            return {
                "error": {
                    "type": error_type,
                    "message": message,
                    "code": 400
                }
            }

    return TestData()

@pytest.fixture
def monkeypatch_safe_int():
    """Monkeypatch for safe_int utility"""
    with patch('agent_x.utils.utils.safe_int', wraps=safe_int) as mock_safe_int:
        yield mock_safe_int

@pytest.fixture
def environment_variables():
    """Fixture to temporarily set environment variables"""
    original_env = os.environ.copy()

    def set_env(**kwargs):
        for key, value in kwargs.items():
            os.environ[key] = value

    yield set_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)