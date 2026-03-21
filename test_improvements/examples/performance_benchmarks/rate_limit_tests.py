import pytest
import time
import threading
from agent_x.core.rate_limiter import RateLimiter
from agent_x.core.retry_handler import RetryHandler
from agent_x.api.openai_client import OpenAIClient
from agent_x.utils.benchmark import BenchmarkTimer

class TestRateLimiting:
    """Performance tests for rate limiting and retry mechanisms"""

    @pytest.fixture
def basic_rate_limiter(self):
        """Basic rate limiter fixture"""
        return RateLimiter(max_calls=10, period=60)

    @pytest.fixture
def burst_rate_limiter(self):
        """Rate limiter with burst capacity"""
        return RateLimiter(max_calls=100, period=60, burst_capacity=20)

    @pytest.fixture
def token_bucket_limiter(self):
        """Token bucket rate limiter"""
        return RateLimiter(
            max_calls=100,
            period=60,
            refill_rate=5,
            bucket_size=20
        )

    def test_rate_limiter_basic_throttling(self, basic_rate_limiter):
        """Test basic rate limiting behavior"""
        limiter = basic_rate_limiter

        # First 10 calls should succeed
        for i in range(10):
            assert limiter.allow() == True

        # 11th call should be blocked
        assert limiter.allow() == False

    def test_rate_limiter_periodic_reset(self, basic_rate_limiter):
        """Test rate limiter resets after period"""
        limiter = basic_rate_limiter

        # Fill the bucket
        for i in range(10):
            assert limiter.allow() == True

        # Wait for period to reset
        time.sleep(60.1)

        # Should be able to make 10 more calls
        for i in range(10):
            assert limiter.allow() == True

    def test_burst_rate_limiter_capacity(self, burst_rate_limiter):
        """Test burst capacity functionality"""
        limiter = burst_rate_limiter

        # Should allow up to burst capacity immediately
        for i in range(20):
            assert limiter.allow() == True

        # Additional calls should be rate limited
        for i in range(80):
            assert limiter.allow() == False

    def test_token_bucket_refill(self, token_bucket_limiter):
        """Test token bucket refill behavior"""
        limiter = token_bucket_limiter

        # Fill the bucket
        for i in range(20):
            assert limiter.allow() == True

        # Should be empty now
        assert limiter.allow() == False

        # Wait for refill
        time.sleep(12.1)  # 12 seconds for 1 token (5 per minute)

        # Should have 1 token now
        assert limiter.allow() == True
        assert limiter.allow() == False  # Bucket should be empty again

    def test_rate_limiter_concurrent_access(self, basic_rate_limiter):
        """Test rate limiter handles concurrent access"""
        limiter = basic_rate_limiter

        results = []
        lock = threading.Lock()

        def worker():
            result = limiter.allow()
            with lock:
                results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(15)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Only 10 should succeed
        assert results.count(True) == 10
        assert results.count(False) == 5

    @pytest.mark.parametrize("max_calls,period,burst,expected_success", [
        (10, 60, 0, 10),
        (100, 60, 20, 20),
        (50, 30, 10, 10),
        (1000, 3600, 100, 100),
    ])
    def test_rate_limiter_configurations(
        self, max_calls, period, burst, expected_success
    ):
        """Test various rate limiter configurations"""
        limiter = RateLimiter(max_calls=max_calls, period=period, burst_capacity=burst)

        success_count = 0
        for _ in range(max_calls + burst + 10):
            if limiter.allow():
                success_count += 1

        assert success_count == expected_success

    def test_rate_limiter_reset_behavior(self, basic_rate_limiter):
        """Test rate limiter reset behavior"""
        limiter = basic_rate_limiter

        # Make 5 calls
        for _ in range(5):
            assert limiter.allow() == True

        # Reset manually
        limiter.reset()

        # Should be able to make 10 calls again
        for _ in range(10):
            assert limiter.allow() == True

    def test_rate_limiter_statistics(self, basic_rate_limiter):
        """Test rate limiter statistics tracking"""
        limiter = basic_rate_limiter

        # Make 3 calls
        for _ in range(3):
            limiter.allow()

        stats = limiter.get_statistics()

        assert stats["allowed"] == 3
        assert stats["blocked"] == 0
        assert stats["total"] == 3
        assert stats["available"] == 7

    def test_rate_limiter_blocking_behavior(self, basic_rate_limiter):
        """Test rate limiter blocking behavior"""
        limiter = basic_rate_limiter

        # Fill the bucket
        for _ in range(10):
            assert limiter.allow() == True

        # Should block on 11th call
        start_time = time.time()
        assert limiter.allow() == False
        elapsed_time = time.time() - start_time

        # Blocking should be immediate (no sleep)
        assert elapsed_time < 0.01

    def test_retry_handler_with_rate_limiter(self):
        """Test retry handler works with rate limiter"""
        limiter = RateLimiter(max_calls=5, period=60)
        handler = RetryHandler(max_attempts=3)

        attempt_count = 0

        def rate_limited_operation():
            nonlocal attempt_count
            attempt_count += 1
            if limiter.allow():
                return "success"
            raise RateLimitError("Rate limited", retry_after=0.1)

        # Should succeed on first attempt if within limit
        result = handler.execute_with_retry(rate_limited_operation)
        assert result == "success"
        assert attempt_count == 1

    @pytest.mark.integration
    def test_openai_client_rate_limiting(self, sample_api_response):
        """Test OpenAI client respects rate limits"""
        from agent_x.api.openai_client import OpenAIClient

        with patch('openai.OpenAI') as MockOpenAI:
            mock_client = MagicMock()
            # First call succeeds, second fails with rate limit
            mock_client.chat.completions.create.side_effect = [
                MagicMock(**sample_api_response),
                RateLimitError("Rate limited", retry_after=0.1)
            ]
            MockOpenAI.return_value = mock_client

            client = OpenAIClient(api_key="test_key", retry_attempts=2)

            # First call should succeed
            response = client.generate(prompt="Test 1")
            assert response is not None

            # Second call should retry and fail
            with pytest.raises(RateLimitError):
                client.generate(prompt="Test 2")

            assert mock_client.chat.completions.create.call_count == 2

    def test_rate_limiter_memory_usage(self):
        """Test rate limiter memory usage is reasonable"""
        limiter = RateLimiter(max_calls=1000, period=3600)

        # Measure memory before and after
        import sys
        before = sys.getsizeof(limiter)

        # Make 1000 calls
        for _ in range(1000):
            limiter.allow()

        after = sys.getsizeof(limiter)

        # Memory usage should be reasonable
        assert after - before < 10000  # Less than 10KB increase

    def test_rate_limiter_thread_safety(self, basic_rate_limiter):
        """Test rate limiter is thread-safe"""
        limiter = basic_rate_limiter

        def worker():
            return limiter.allow()

        # Test with many concurrent threads
        threads = []
        results = []
        lock = threading.Lock()

        for _ in range(100):
            t = threading.Thread(target=lambda: results.append(worker()))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have consistent results
        allowed_count = results.count(True)
        blocked_count = results.count(False)

        # Total should not exceed max_calls
        assert allowed_count <= 10

    def test_rate_limiter_custom_clock(self):
        """Test rate limiter works with custom clock"""
        from agent_x.utils.time import MockClock

        clock = MockClock()
        limiter = RateLimiter(
            max_calls=10,
            period=60,
            clock=clock
        )

        # Make 5 calls
        for _ in range(5):
            assert limiter.allow() == True

        # Advance clock manually
        clock.advance(60.1)

        # Should be able to make 10 more calls
        for _ in range(10):
            assert limiter.allow() == True

    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleanup functionality"""
        limiter = RateLimiter(max_calls=10, period=60)

        # Make 10 calls
        for _ in range(10):
            assert limiter.allow() == True

        # Should be full now
        assert limiter.allow() == False

        # Cleanup should reset state
        limiter.cleanup()

        # Should be able to make 10 calls again
        for _ in range(10):
            assert limiter.allow() == True

    def test_rate_limiter_with_benchmark_timer(self):
        """Test rate limiter with benchmarking timer"""
        limiter = RateLimiter(max_calls=5, period=60)
        timer = BenchmarkTimer()

        timer.start("rate_limit_test")

        # Make 5 calls
        for _ in range(5):
            limiter.allow()

        timer.stop("rate_limit_test")

        stats = timer.get_stats()
        assert "rate_limit_test" in stats
        assert stats["rate_limit_test"]["elapsed_time"] > 0

    @pytest.mark.parametrize("max_calls,period,burst,expected_elapsed", [
        (10, 60, 0, 0.01),
        (100, 60, 20, 0.01),
        (50, 30, 10, 0.01),
        (1000, 3600, 100, 0.01),
    ])
    def test_rate_limiter_performance(
        self, max_calls, period, burst, expected_elapsed
    ):
        """Test rate limiter performance characteristics"""
        limiter = RateLimiter(max_calls=max_calls, period=period, burst_capacity=burst)

        timer = BenchmarkTimer()
        timer.start("performance_test")

        # Make max_calls + burst calls
        for _ in range(max_calls + burst):
            limiter.allow()

        timer.stop("performance_test")

        stats = timer.get_stats()
        elapsed = stats["performance_test"]["elapsed_time"]

        # Should be very fast (microseconds per call)
        assert elapsed < expected_elapsed

    def test_rate_limiter_with_retry_handler(self):
        """Test rate limiter with retry handler integration"""
        limiter = RateLimiter(max_calls=3, period=60)
        handler = RetryHandler(max_attempts=3, base_delay=0.05)

        attempt_count = 0

        def operation_with_rate_limit():
            nonlocal attempt_count
            attempt_count += 1
            if limiter.allow():
                return "success"
            raise RateLimitError("Rate limited", retry_after=0.05)

        # Should succeed on first attempt if within limit
        result = handler.execute_with_retry(operation_with_rate_limit)
        assert result == "success"
        assert attempt_count == 1

        # Should retry if rate limited
        limiter.reset()  # Reset to allow testing retry
        result = handler.execute_with_retry(operation_with_rate_limit)
        assert result == "success"

    def test_rate_limiter_edge_cases(self):
        """Test rate limiter edge cases"""
        limiter = RateLimiter(max_calls=1, period=60)

        # Test with zero max_calls (should always block)
        zero_limiter = RateLimiter(max_calls=0, period=60)
        assert zero_limiter.allow() == False

        # Test with zero period (should allow unlimited calls)
        unlimited_limiter = RateLimiter(max_calls=10, period=0)
        for _ in range(100):
            assert unlimited_limiter.allow() == True

        # Test with negative values (should raise)
        with pytest.raises(ValueError, match="max_calls must be positive"):
            RateLimiter(max_calls=-1, period=60)

        with pytest.raises(ValueError, match="period must be positive"):
            RateLimiter(max_calls=10, period=-1)