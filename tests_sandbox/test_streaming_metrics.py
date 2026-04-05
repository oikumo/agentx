import unittest
from unittest.mock import patch, MagicMock

from app.utils import StreamingMetrics


class TestStreamingMetricsInitialization(unittest.TestCase):
    def test_metrics_starts_with_zero_tokens(self):
        metrics = StreamingMetrics()
        self.assertEqual(metrics.total_tokens, 0)

    def test_metrics_starts_with_zero_elapsed(self):
        metrics = StreamingMetrics()
        self.assertEqual(metrics.elapsed_time, 0.0)

    def test_metrics_not_started_initially(self):
        metrics = StreamingMetrics()
        self.assertFalse(metrics.is_started)


class TestStreamingMetricsTiming(unittest.TestCase):
    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_start_records_start_time(self, mock_time):
        mock_time.return_value = 100.0
        metrics = StreamingMetrics()
        metrics.start()

        self.assertTrue(metrics.is_started)
        self.assertEqual(metrics._start_time, 100.0)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_stop_records_elapsed(self, mock_time):
        mock_time.side_effect = [100.0, 105.0]
        metrics = StreamingMetrics()
        metrics.start()
        metrics.stop()

        self.assertEqual(metrics.elapsed_time, 5.0)
        self.assertFalse(metrics.is_started)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_stop_without_start_raises(self, mock_time):
        metrics = StreamingMetrics()
        with self.assertRaises(RuntimeError):
            metrics.stop()


class TestStreamingMetricsTokenCounting(unittest.TestCase):
    def test_add_tokens_increments_count(self):
        metrics = StreamingMetrics()
        metrics.add_tokens(10)
        self.assertEqual(metrics.total_tokens, 10)

    def test_add_tokens_accumulates(self):
        metrics = StreamingMetrics()
        metrics.add_tokens(10)
        metrics.add_tokens(20)
        self.assertEqual(metrics.total_tokens, 30)

    def test_add_tokens_accepts_string_length(self):
        metrics = StreamingMetrics()
        metrics.add_text("hello world")
        self.assertEqual(metrics.total_tokens, 11)


class TestStreamingMetricsCalculation(unittest.TestCase):
    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_tokens_per_second_basic(self, mock_time):
        mock_time.side_effect = [100.0, 102.0]
        metrics = StreamingMetrics()
        metrics.start()
        metrics.add_tokens(20)
        metrics.stop()

        self.assertEqual(metrics.tokens_per_second, 10.0)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_tokens_per_second_zero_when_no_time(self, mock_time):
        mock_time.return_value = 100.0
        metrics = StreamingMetrics()
        metrics.start()
        metrics.add_tokens(10)

        self.assertEqual(metrics.tokens_per_second, 0.0)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_tokens_per_second_zero_when_no_tokens(self, mock_time):
        mock_time.side_effect = [100.0, 110.0]
        metrics = StreamingMetrics()
        metrics.start()
        metrics.stop()

        self.assertEqual(metrics.tokens_per_second, 0.0)

    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_format_metrics_returns_readable_string(self, mock_time):
        mock_time.side_effect = [100.0, 105.0]
        metrics = StreamingMetrics()
        metrics.start()
        metrics.add_tokens(50)
        metrics.stop()

        result = metrics.format()
        self.assertIn("50", result)
        self.assertIn("10.0", result)
        self.assertIn("tok/s", result)


class TestStreamingMetricsContextManager(unittest.TestCase):
    @patch("app.common.utils.streaming_metrics.time.perf_counter")
    def test_context_manager_measures_time(self, mock_time):
        mock_time.side_effect = [100.0, 103.0]
        metrics = StreamingMetrics()

        with metrics:
            metrics.add_tokens(30)

        self.assertEqual(metrics.elapsed_time, 3.0)
        self.assertEqual(metrics.total_tokens, 30)
        self.assertEqual(metrics.tokens_per_second, 10.0)


if __name__ == "__main__":
    unittest.main()
