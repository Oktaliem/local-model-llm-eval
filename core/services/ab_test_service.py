"""A/B testing service with queue-based background processing"""
import threading
import time
from typing import Dict, Any, Optional
from queue import Queue
from core.services.evaluation_service import EvaluationService
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository
from backend.services.ab_test_service import create_ab_test, get_ab_test, execute_ab_test  # reuse existing


class ABTestService:
    def __init__(self, evaluation_service: Optional[EvaluationService] = None, judgments_repo: Optional[JudgmentsRepository] = None):
        self.evaluation_service = evaluation_service or EvaluationService()
        self.judgments_repo = judgments_repo or JudgmentsRepository()
        self._test_progress: Dict[str, Dict[str, Any]] = {}
        self._test_queues: Dict[str, Queue] = {}
        self._test_threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def create_test(self, *args, **kwargs):
        return create_ab_test(*args, **kwargs)

    def start_test(self, test_id: str, judge_model: str) -> bool:
        test_info = get_ab_test(test_id)
        if not test_info:
            return False
        with self._lock:
            if test_id in self._test_progress and self._test_progress[test_id].get("status") == "running":
                return False
            result_queue = Queue()
            self._test_queues[test_id] = result_queue
            # test_cases_json is the field name from database, but it's already parsed to a list
            test_cases = test_info.get("test_cases_json", test_info.get("test_cases", []))
            self._test_progress[test_id] = {
                "test_id": test_id,
                "status": "running",
                "total_cases": len(test_cases),
                "completed_cases": 0,
                "started_at": time.time(),
            }
        thread = threading.Thread(target=self._run_test, args=(test_id, judge_model), daemon=True)
        thread.start()
        with self._lock:
            self._test_threads[test_id] = thread
        return True

    def _run_test(self, test_id: str, judge_model: str):
        try:
            result = execute_ab_test(test_id=test_id, judge_model=judge_model)
            with self._lock:
                if test_id in self._test_progress:
                    if result.get("success"):
                        self._test_progress[test_id]["status"] = "completed"
                        self._test_progress[test_id]["result"] = result
                    else:
                        self._test_progress[test_id]["status"] = "failed"
                        self._test_progress[test_id]["error"] = result.get("error", "Unknown error")
                    self._test_progress[test_id]["completed_at"] = time.time()
                    if test_id in self._test_queues:
                        self._test_queues[test_id].put(result)
        except Exception as e:
            with self._lock:
                if test_id in self._test_progress:
                    self._test_progress[test_id]["status"] = "failed"
                    self._test_progress[test_id]["error"] = str(e)
                    self._test_progress[test_id]["completed_at"] = time.time()

    def get_progress(self, test_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._test_progress.get(test_id)

    def get_result(self, test_id: str) -> Optional[Dict[str, Any]]:
        if test_id not in self._test_queues:
            return None
        queue = self._test_queues[test_id]
        if queue.empty():
            return None
        try:
            return queue.get_nowait()
        except Exception:
            return None

    def stop_test(self, test_id: str) -> bool:
        with self._lock:
            if test_id not in self._test_progress:
                return False
            progress = self._test_progress[test_id]
            if progress.get("status") != "running":
                return False
            progress["status"] = "stopped"
            progress["stopped_at"] = time.time()
            return True


