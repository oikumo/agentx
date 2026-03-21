import pytest
from unittest.mock import patch, MagicMock
from agent_x.core.agent_x import AgentX
from agent_x.models.config import Config

class TestCoreApplication:
    """Core application component tests"""

    @pytest.mark.parametrize("user_input,expected_response", [
        ("Hello", "Hi there! How can I assist you?"),
        ("How are you?", "I'm doing well, thank you! How can I help?"),
        ("Solve 2+2", "4"),
        ("What's the weather?", "I can help you with that. URL: https://weather.com")
    ])
    def test_agentx_responses(self, test_data, user_input, expected_response):
        """Test AgentX response generation for various inputs"""
        agent = AgentX(Config.from_env())
        with patch('agent_x.core.agent_x.LLMProvider.get_response') as mock_llm:
            mock_llm.return_value = expected_response
            result = agent.process_message(user_input)
            assert result == expected_response
            mock_llm.assert_called_once()

    def test_agentx_initialization_success(self, sample_config, mock_api_client):
        """Test AgentX initialization with valid configuration"""
        with patch('agent_x.core.agent_x.LLMProvider') as MockLLM:
            MockLLM.return_value = mock_api_client
            agent = AgentX(sample_config)
            assert agent.config == sample_config
            assert agent.llm_client == mock_api_client

    def test_agentx_initialization_failure(self, sample_config):
        """Test AgentX initialization with invalid API key"""
        with patch('agent_x.core.agent_x.LLMProvider') as MockLLM:
            MockLLM.side_effect = ValueError("Invalid API key")
            with pytest.raises(ValueError) as excinfo:
                AgentX(sample_config)
            assert "Invalid API key" in str(excinfo.value)

    def test_agentx_message_history(self, sample_config):
        """Test message history tracking in AgentX"""
        agent = AgentX(sample_config)
        agent.add_message("Hello", "user")
        agent.add_message("Hi!", "assistant")

        assert len(agent.message_history) == 2
        assert agent.message_history[0]["role"] == "user"
        assert agent.message_history[1]["role"] == "assistant"

    @pytest.mark.integration
    def test_agentx_end_to_end_flow(self, mock_api_client, sample_test_data):
        """End-to-end test of AgentX message processing"""
        agent = AgentX(Config.from_env())
        agent.llm_client = mock_api_client

        user_msg = sample_test_data.create_message("What's the capital of France?")
        response = agent.process_message(user_msg)

        assert response is not None
        assert "Paris" in response
        mock_api_client.messages.create.assert_called_once()

    def test_agentx_retry_logic(self, sample_config):
        """Test retry logic for transient failures"""
        with patch('agent_x.core.agent_x.LLMProvider') as MockLLM:
            # Simulate two failures then success
            MockLLM.side_effect = [Exception("Timeout"), Exception("Timeout"), MagicMock()]
            agent = AgentX(sample_config)

            with pytest.raises(Exception) as excinfo:
                agent.retry_operation()
            assert "Timeout" in str(excinfo.value)

    def test_agentx_cleanup_on_error(self, sample_config):
        """Test that resources are properly cleaned up on error"""
        with patch('agent_x.core.agent_x.LLMProvider') as MockLLM:
            MockLLM.side_effect = Exception("Connection error")
            agent = AgentX(sample_config)

            with pytest.raises(Exception):
                agent.process_message("test")

            # Verify cleanup was called
            agent.cleanup.assert_called_once()

    def test_agentx_configuration_validation(self):
        """Test configuration validation during initialization"""
        with pytest.raises(ValueError) as excinfo:
            Config(api_key="", model="", max_tokens=None)
        assert "api_key" in str(excinfo.value)

    def test_agentx_state_isolation(self):
        """Test that multiple AgentX instances maintain independent state"""
        config1 = Config(api_key="key1", model="model1")
        config2 = Config(api_key="key2", model="model2")

        agent1 = AgentX(config1)
        agent2 = AgentX(config2)

        agent1.add_message("Message 1", "user")
        agent2.add_message("Message 2", "user")

        assert len(agent1.message_history) == 1
        assert len(agent2.message_history) == 1
        assert agent1.message_history[0]["content"] == "Message 1"
        assert agent2.message_history[0]["content"] == "Message 2"

    @pytest.mark.parametrize("invalid_input", [
        "",
        " " * 1000,
        "\x00\x01\x02",
        {"not": "a string"}
    ])
    def test_agentx_invalid_input_handling(self, sample_config, invalid_input):
        """Test AgentX handles invalid input gracefully"""
        agent = AgentX(sample_config)
        with pytest.raises(ValueError):
            agent.process_message(invalid_input)

    def test_agentx_concurrent_access(self, sample_config):
        """Test thread-safe access to AgentX instance"""
        import threading

        results = []
        lock = threading.Lock()

        def worker(agent, message):
            try:
                response = agent.process_message(message)
                with lock:
                    results.append(response)
            except Exception as e:
                with lock:
                    results.append(e)

        agent = AgentX(sample_config)
        threads = [
            threading.Thread(target=worker, args=(agent, f"Message {i}"))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
        assert all(isinstance(r, str) for r in results)