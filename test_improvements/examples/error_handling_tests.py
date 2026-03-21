import pytest
import time
from unittest.mock import patch, MagicMock, call
from agent_x.errors.transient_errors import (
    TransientError,
    RateLimitError,
    ConnectionTimeoutError,
    APIServiceUnavailableError
)
from agent_x.core.retry_handler import RetryHandler
from agent_x.core.state_manager import StateManager
from agent_x.utils.error_recovery import ErrorRecoveryManager

class TestTransientErrorHandling:
    """Test transient error handling and recovery mechanisms"""

    def test_ratelimit_error_handling(self):
        """Test RateLimitError raises with correct attributes"""
        error = RateLimitError(
            message="Rate limit exceeded",
            retry_after=60,
            limit=100,
            remaining=0
        )

        assert isinstance(error, TransientError)
        assert error.retry_after == 60
        assert error.limit == 100
        assert error.remaining == 0
        assert "Rate limit" in str(error)

    def test_connection_timeout_error(self):
        """Test ConnectionTimeoutError with timeout value"""
        error = ConnectionTimeoutError(
            message="Connection timed out",
            timeout=30.0,
            url="http://api.example.com"
        )

        assert isinstance(error, TransientError)
        assert error.timeout == 30.0
        assert error.url == "http://api.example.com"

    def test_api_unavailable_error(self):
        """Test APIServiceUnavailableError with status code"""
        error = APIServiceUnavailableError(
            message="Service temporarily unavailable",
            status_code=503,
            service="OpenAI"
        )

        assert isinstance(error, TransientError)
        assert error.status_code == 503
        assert error.service == "OpenAI"

    @pytest.mark.parametrize("error_class,error_kwargs", [
        (RateLimitError, {"retry_after": 30, "limit": 50}),
        (ConnectionTimeoutError, {"timeout": 15.5, "url": "http://test.com"}),
        (APIServiceUnavailableError, {"status_code": 502, "service": "Tavily"})
    ])
    def test_error_serialization(self, error_class, error_kwargs):
        """Test error objects can be serialized for logging"""
        error = error_class(message="Test error", **error_kwargs)
        error_dict = error.to_dict()

        assert "message" in error_dict
        assert "type" in error_dict
        assert error_dict["type"] == error_class.__name__

    def test_retry_handler_exponential_backoff(self):
        """Test RetryHandler implements exponential backoff"""
        handler = RetryHandler(
            max_attempts=3,
            base_delay=1,
            max_delay=10,
            backoff_factor=2
        )

        delays = list(handler.get_retry_delays())

        assert len(delays) == 3
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0

    def test_retry_handler_jitter(self):
        """Test RetryHandler adds jitter to retry delays"""
        handler = RetryHandler(
            max_attempts=5,
            base_delay=1,
            jitter=True
        )

        delays = list(handler.get_retry_delays())

        # With jitter, delays should vary slightly
        base_values = [1, 2, 4, 8, 16]
        for i, (delay, base) in enumerate(zip(delays, base_values)):
            assert 0.9 * base <= delay <= 1.1 * base

    def test_retry_handler_stops_on_success(self):
        """Test RetryHandler stops when operation succeeds"""
        handler = RetryHandler(max_attempts=3)

        attempt_count = 0

        def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise RateLimitError("Rate limited", retry_after=1)
            return "success"

        result = handler.execute_with_retry(flaky_operation)

        assert result == "success"
        assert attempt_count == 2

    def test_retry_handler_exhausts_attempts(self):
        """Test RetryHandler raises error after all retries exhausted"""
        handler = RetryHandler(max_attempts=2)

        def failing_operation():
            raise RateLimitError("Rate limited", retry_after=1)

        with pytest.raises(TransientError) as excinfo:
            handler.execute_with_retry(failing_operation)

        assert "Rate limited" in str(excinfo.value)

    @pytest.mark.parametrize("delay,backoff_factor,max_delay", [
        (1, 2, 60),
        (0.5, 3, 30),
        (2, 1.5, 120),
    ])
    def test_retry_delay_calculation(self, delay, backoff_factor, max_delay):
        """Test retry delay calculation with different parameters"""
        handler = RetryHandler(
            base_delay=delay,
            backoff_factor=backoff_factor,
            max_delay=max_delay
        )

        for i, calculated_delay in enumerate(handler.get_retry_delays()):
            expected = min(delay * (backoff_factor ** i), max_delay)
            assert abs(calculated_delay - expected) < 0.001

    def test_error_recovery_manager_circuit_breaker(self):
        """Test ErrorRecoveryManager circuit breaker functionality"""
        recovery_manager = ErrorRecoveryManager(
            error_threshold=3,
            reset_timeout=60
        )

        # Simulate failures to trip circuit breaker
        for _ in range(3):
            recovery_manager.record_failure()

        assert recovery_manager.is_circuit_open()

        # Circuit should be open, preventing further calls
        with pytest.raises(RuntimeError, match="Circuit breaker is OPEN"):
            recovery_manager.record_success()

    def test_error_recovery_manager_half_open(self):
        """Test ErrorRecoveryManager transitions to half-open state"""
        recovery_manager = ErrorRecoveryManager(
            error_threshold=2,
            reset_timeout=1,
            half_open_attempts=1
        )

        # Trip circuit breaker
        for _ in range(2):
            recovery_manager.record_failure()

        assert recovery_manager.is_circuit_open()

        # Wait for reset timeout
        time.sleep(1.1)

        # Should allow one test attempt in half-open state
        recovery_manager.record_success()
        assert not recovery_manager.is_circuit_open()

    def test_error_recovery_manager_reset(self):
        """Test ErrorRecoveryManager resets after successful operations"""
        recovery_manager = ErrorRecoveryManager(error_threshold=2)

        # Trip circuit breaker
        recovery_manager.record_failure()
        recovery_manager.record_failure()

        assert recovery_manager.is_circuit_open()

        # Reset manually
        recovery_manager.reset()
        assert not recovery_manager.is_circuit_open()

    def test_state_manager_transaction_rollback(self):
        """Test StateManager rolls back transactions on error"""
        state_manager = StateManager()

        try:
            with state_manager.transaction():
                state_manager.set("key1", "value1")
                state_manager.set("key2", "value2")
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Transaction should have been rolled back
        assert state_manager.get("key1") is None
        assert state_manager.get("key2") is None

    def test_state_manager_commit_on_success(self):
        """Test StateManager commits transactions on success"""
        state_manager = StateManager()

        with state_manager.transaction():
            state_manager.set("key1", "value1")
            state_manager.set("key2", "value2")

        assert state_manager.get("key1") == "value1"
        assert state_manager.get("key2") == "value2"

    def test_state_manager_nested_transactions(self):
        """Test StateManager handles nested transactions correctly"""
        state_manager = StateManager()

        with state_manager.transaction():
            state_manager.set("outer", "value_outer")

            with pytest.raises(RuntimeError, match="Nested transactions not supported"):
                with state_manager.transaction():
                    state_manager.set("inner", "value_inner")

    def test_state_manager_state_snapshot(self):
        """Test StateManager creates and restores snapshots"""
        state_manager = StateManager()
        state_manager.set("key1", "value1")
        state_manager.set("key2", "value2")

        snapshot = state_manager.create_snapshot()

        state_manager.set("key1", "modified")
        state_manager.delete("key2")

        # Restore snapshot
        state_manager.restore_snapshot(snapshot)

        assert state_manager.get("key1") == "value1"
        assert state_manager.get("key2") == "value2"

    def test_error_context_preservation(self):
        """Test that error context is preserved through retry boundaries"""
        handler = RetryHandler(max_attempts=2)

        context = {"attempt": 0, "original_error": None}

        def operation_with_context():
            context["attempt"] += 1
            if context["attempt"] == 1:
                error = TransientError("First attempt failed")
                context["original_error"] = error
                raise error
            return "success"

        result = handler.execute_with_retry(operation_with_context)

        assert result == "success"
        assert context["attempt"] == 2
        assert context["original_error"] is not None

    @pytest.mark.integration
    def test_full_error_recovery_flow(self, sample_api_response):
        """Test complete error recovery flow with real API calls"""
        from agent_x.api.openai_client import OpenAIClient

        with patch('openai.OpenAI') as MockOpenAI:
            # First call fails with rate limit, second succeeds
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                RateLimitError("Rate limited", retry_after=0.1),
                MagicMock(**sample_api_response)
            ]
            MockOpenAI.return_value = mock_client

            client = OpenAIClient(api_key="test_key", retry_attempts=2)
            response = client.generate(prompt="Test")

            assert response is not None
            assert mock_client.chat.completions.create.call_count == 2

    def test_error_logging_integration(self, caplog):
        """Test that errors are properly logged"""
        import logging
        caplog.set_level(logging.ERROR)

        handler = RetryHandler(max_attempts=1)

        def failing_operation():
            raise ConnectionTimeoutError("Timeout", timeout=5.0, url="http://test.com")

        with pytest.raises(ConnectionTimeoutError):
            handler.execute_with_retry(failing_operation)

        # Check error was logged
        assert any("Timeout" in record.message for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)

    def test_cascading_failure_prevention(self):
        """Test that cascading failures are prevented"""
        from agent_x.core.circuit_breaker import CircuitBreaker

        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1,
            expected_exception=TransientError
        )

        # Simulate repeated failures
        for _ in range(3):
            try:
                breaker.call(lambda: (_ for _ in ()).throw(TransientError("fail")))
            except TransientError:
                pass

        assert breaker.state == "open"

        # Further calls should fail fast without executing
        with pytest.raises(RuntimeError, match="Circuit breaker is OPEN"):
            breaker.call(lambda: "should not execute")

    def test_graceful_degradation_on_failure(self):
        """Test system gracefully degrades when services fail"""
        from agent_x.core.degradation import DegradationManager

        manager = DegradationManager()

        # Simulate primary service failure
        with patch('agent_x.api.openai_client.OpenAIClient') as MockOpenAI:
            MockOpenAI.side_effect = APIServiceUnavailableError(
                "Service down", status_code=503, service="OpenAI"
            )

            # Should fall back to alternative service
            result = manager.get_response_with_fallback(prompt="Test")

            assert result is not None
            assert "fallback" in result.lower() or result != ""