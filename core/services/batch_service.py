"""Batch evaluation service with queue-based background processing"""
import uuid
import threading
import time
from typing import Dict, Any, List, Optional
from queue import Queue
from core.domain.models import RunProgress
from core.services.evaluation_service import EvaluationService
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository


class BatchService:
    """Service for batch evaluation processing with progress tracking"""

    def __init__(self, evaluation_service: Optional[EvaluationService] = None, judgments_repo: Optional[JudgmentsRepository] = None):
        self.evaluation_service = evaluation_service or EvaluationService()
        self.judgments_repo = judgments_repo or JudgmentsRepository()
        self._runs: Dict[str, RunProgress] = {}
        self._run_queues: Dict[str, Queue] = {}
        self._run_threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def start_batch_evaluation(
        self,
        test_cases: List[Dict[str, Any]],
        evaluation_type: str,
        judge_model: str,
        run_name: Optional[str] = None,
        dataset_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        run_id = str(uuid.uuid4())
        result_queue = Queue()
        run_progress = RunProgress(run_id=run_id, total_cases=len(test_cases), completed_cases=0, status="running", created_at=time.time())
        with self._lock:
            self._runs[run_id] = run_progress
            self._run_queues[run_id] = result_queue
        thread = threading.Thread(target=self._process_batch, args=(run_id, test_cases, evaluation_type, judge_model, options or {}), daemon=True)
        thread.start()
        with self._lock:
            self._run_threads[run_id] = thread
        return run_id

    def _process_batch(self, run_id: str, test_cases: List[Dict[str, Any]], evaluation_type: str, judge_model: str, options: Dict[str, Any]):
        try:
            results = []
            for i, test_case in enumerate(test_cases):
                question = test_case.get("question", "")
                response = test_case.get("response", "")
                reference = test_case.get("reference")
                case_options = options.copy()
                if reference:
                    case_options["reference"] = reference
                result = self.evaluation_service.evaluate(
                    evaluation_type=evaluation_type, question=question, judge_model=judge_model, response=response, options=case_options, save_to_db=True
                )
                results.append({"test_case_index": i, "question": question, "response": response, "result": result})
                with self._lock:
                    if run_id in self._runs:
                        self._runs[run_id].completed_cases = i + 1
                        self._runs[run_id].results = results
                        self._runs[run_id].updated_at = time.time()
                if run_id in self._run_queues:
                    self._run_queues[run_id].put({"index": i, "total": len(test_cases), "result": result})
            with self._lock:
                if run_id in self._runs:
                    self._runs[run_id].status = "completed"
                    self._runs[run_id].updated_at = time.time()
        except Exception as e:
            with self._lock:
                if run_id in self._runs:
                    self._runs[run_id].status = "failed"
                    self._runs[run_id].error = str(e)
                    self._runs[run_id].updated_at = time.time()

    def get_progress(self, run_id: str) -> Optional[RunProgress]:
        with self._lock:
            return self._runs.get(run_id)

    def get_results(self, run_id: str) -> Optional[List[Dict[str, Any]]]:
        if run_id not in self._run_queues:
            return None
        results = []
        queue = self._run_queues[run_id]
        while not queue.empty():
            try:
                results.append(queue.get_nowait())
            except Exception:
                break
        return results if results else None

    def stop_run(self, run_id: str) -> bool:
        with self._lock:
            if run_id not in self._runs:
                return False
            run = self._runs[run_id]
            if run.status != "running":
                return False
            run.status = "stopped"
            run.updated_at = time.time()
            return True


