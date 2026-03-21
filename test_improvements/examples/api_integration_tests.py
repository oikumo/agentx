import pytest
from unittest.mock import patch, MagicMock
from agent_x.api.openai_client import OpenAIClient
from agent_x.api.tavily_client import TavilyClient
from agent_x.api.ollama_client import OllamaClient

class TestAPIIntegration:
    """Integration tests for external API interactions"""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return {
            "choices": [{
                "message": {"content": "Mock response"}
            }],
            "usage": {"total_tokens": 100}
        }

    @pytest.fixture
    def mock_tavily_response(self):
        """Mock Tavily search response"""
        return {
            "results": [
                {"title": "Result 1", "url": "http://example.com", "content": "Content 1"},
                {"title": "Result 2", "url": "http://example2.com", "content": "Content 2"}
            ]
        }

    @pytest.mark.parametrize("model,max_tokens,temperature,expected_params", [
        ("gpt-3.5-turbo", 100, 0.0, {"model": "gpt-3.5-turbo", "max_tokens": 100, "temperature": 0.0}),
        ("gpt-4", 2000, 0.7, {"model": "gpt-4", "max_tokens": 2000, "temperature": 0.7}),
        ("gpt-4-turbo", 4096, 1.0, {"model": "gpt-4-turbo", "max_tokens": 4096, "temperature": 1.0}),
    ])
    def test_openai_client_parameters(self, mock_openai_response, model, max_tokens, temperature, expected_params):
        """Test OpenAI client sends correct parameters"""
        with patch('openai.OpenAI') as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = MagicMock(**mock_openai_response)
            MockOpenAI.return_value = mock_client

            client = OpenAIClient(api_key="test_key")
            response = client.generate(
                prompt="Test prompt",
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )

            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args

            # Verify sent parameters
            assert call_args.kwargs["model"] == expected_params["model"]
            assert call_args.kwargs["max_tokens"] == expected_params["max_tokens"]
            assert call_args.kwargs["temperature"] == expected_params["temperature"]

    @pytest.mark.integration
    def test_openai_api_error_handling(self):
        """Test OpenAI client handles API errors gracefully"""
        with patch('openai.OpenAI') as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error: 429 Too Many Requests")
            MockOpenAI.return_value = mock_client

            client = OpenAIClient(api_key="test_key")

            with pytest.raises(RuntimeError) as excinfo:
                client.generate(prompt="Test", retry_attempts=3)

            assert "429" in str(excinfo.value) or "API Error" in str(excinfo.value)

    def test_openai_rate_limit_retry(self, mock_openai_response):
        """Test OpenAI client retries on rate limit errors"""
        with patch('openai.OpenAI') as MockOpenAI:
            mock_client = MagicMock()
            # Simulate rate limit on first call, then success
            mock_client.chat.completions.create.side_effect = [
                Exception("Rate limit exceeded"),
                MagicMock(**mock_openai_response)
            ]
            MockOpenAI.return_value = mock_client

            client = OpenAIClient(api_key="test_key", retry_attempts=3)
            response = client.generate(prompt="Test")

            assert response is not None
            assert mock_client.chat.completions.create.call_count == 2

    def test_tavily_search_integration(self, mock_tavily_response):
        """Test Tavily search API integration"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_tavily_response

            client = TavilyClient(api_key="test_key")
            results = client.search("Python testing frameworks")

            assert len(results["results"]) == 2
            assert results["results"][0]["title"] == "Result 1"
            mock_post.assert_called_once()

    def test_tavily_search_error_handling(self):
        """Test Tavily client handles errors correctly"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {"error": "Invalid request"}

            client = TavilyClient(api_key="test_key")

            with pytest.raises(ValueError) as excinfo:
                client.search("")
            assert "Invalid" in str(excinfo.value)

    def test_ollama_local_model_integration(self):
        """Test Ollama local model integration"""
        with patch('requests.post') as mock_post:
            mock_response = {
                "response": "Local model response",
                "done": True
            }
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            client = OllamaClient(base_url="http://localhost:11434")
            result = client.generate("Test prompt", model="llama2")

            assert result == "Local model response"
            mock_post.assert_called_with(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": "Test prompt", "stream": False}
            )

    @pytest.mark.parametrize("api_key,base_url,timeout,expected_timeout", [
        (None, "http://localhost", 5, 5),
        ("key123", "http://localhost", None, 30),
        ("key456", "http://localhost", 10, 10),
    ])
    def test_api_client_configuration(self, api_key, base_url, timeout, expected_timeout):
        """Test API client configuration handling"""
        if api_key:
            client = OpenAIClient(api_key=api_key, base_url=base_url, timeout=expected_timeout)
        else:
            with pytest.raises(ValueError):
                OpenAIClient(api_key=api_key, base_url=base_url, timeout=expected_timeout)

    def test_api_request_headers(self):
        """Test that API requests include proper headers"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"results": []}

            client = TavilyClient(api_key="test_key")
            client.search("query", headers={"User-Agent": "Agent-X/1.0"})

            call_args = mock_post.call_args
            assert "Authorization" in call_args.kwargs.get("headers", {})
            assert "Content-Type" in call_args.kwargs.get("headers", {})

    def test_api_response_caching(self, mock_openai_response):
        """Test API response caching mechanism"""
        with patch('openai.OpenAI') as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = MagicMock(**mock_openai_response)
            MockOpenAI.return_value = mock_client

            client = OpenAIClient(api_key="test_key", enable_cache=True, cache_ttl=300)

            # First call
            response1 = client.generate(prompt="Test")
            # Second call should use cache
            response2 = client.generate(prompt="Test")

            assert mock_client.chat.completions.create.call_count == 1
            assert response1 == response2

    def test_api_response_parsing(self, mock_openai_response):
        """Test parsing of API responses"""
        client = OpenAIClient(api_key="test_key")
        parsed = client.parse_response(mock_openai_response)

        assert "content" in parsed
        assert parsed["content"] == "Mock response"
        assert "tokens" in parsed
        assert parsed["tokens"] == 100

    def test_api_timeout_configuration(self):
        """Test API client timeout settings"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"results": []}

            client = TavilyClient(api_key="test_key", timeout=15)
            client.search("query")

            mock_post.assert_called_once()
            assert mock_post.call_args.kwargs.get("timeout") == 15

    def test_api_connection_retry_failure(self):
        """Test API connection retry exhausts all attempts"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = ConnectionError("Connection failed")

            client = TavilyClient(api_key="test_key", max_retries=2)

            with pytest.raises(ConnectionError):
                client.search("query")

            assert mock_post.call_count == 2