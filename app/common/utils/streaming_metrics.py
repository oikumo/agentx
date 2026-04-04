import time


class StreamingMetrics:
    def __init__(self):
        self._start_time: float | None = None
        self._elapsed_time: float = 0.0
        self._total_tokens: int = 0
        self._is_started: bool = False

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    @property
    def elapsed_time(self) -> float:
        return self._elapsed_time

    @property
    def is_started(self) -> bool:
        return self._is_started

    @property
    def tokens_per_second(self) -> float:
        if self._elapsed_time == 0 or self._total_tokens == 0:
            return 0.0
        return self._total_tokens / self._elapsed_time

    def start(self) -> None:
        self._start_time = time.perf_counter()
        self._is_started = True

    def stop(self) -> None:
        if self._start_time is None:
            raise RuntimeError("Cannot stop metrics that were never started")
        self._elapsed_time = time.perf_counter() - self._start_time
        self._is_started = False

    def add_tokens(self, count: int) -> None:
        self._total_tokens += count

    def add_text(self, text: str) -> None:
        self._total_tokens += len(text)

    def format(self) -> str:
        return f"{self._total_tokens} tokens in {self._elapsed_time:.1f}s ({self.tokens_per_second:.1f} tok/s)"

    def __enter__(self) -> "StreamingMetrics":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
