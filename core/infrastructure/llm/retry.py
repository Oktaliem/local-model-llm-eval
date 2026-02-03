"""Retry policy for LLM calls with reduced num_predict on retries"""
import time
import sys


class RetryPolicy:
    """Retry policy for LLM API calls"""

    def __init__(
        self,
        max_retries: int = 2,
        retry_delay: float = 2.0,
        initial_num_predict: int = 768,
        retry_num_predict: int = 512,
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.initial_num_predict = initial_num_predict
        self.retry_num_predict = retry_num_predict

    def execute(self, func, base_options=None, *args, **kwargs):
        last_exception = None
        if base_options is None:
            base_options = {}
        for attempt in range(self.max_retries + 1):
            try:
                # Prepare per-attempt options with appropriate num_predict
                options = dict(base_options) if base_options else {}
                if attempt > 0:
                    print(f"[DEBUG] Retry attempt {attempt}/{self.max_retries} with reduced num_predict", flush=True)
                    time.sleep(self.retry_delay)
                    options["num_predict"] = self.retry_num_predict
                else:
                    options["num_predict"] = self.initial_num_predict
                sys.stdout.flush()
                # func should accept a single 'options' dict argument
                return func(options, *args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    print(f"[DEBUG] Attempt {attempt + 1} failed: {str(e)}, retrying...", flush=True)
                    sys.stdout.flush()
                else:
                    print(f"[DEBUG] All {self.max_retries + 1} attempts failed", flush=True)
                    sys.stdout.flush()
        raise last_exception


