"""Base evaluation strategy"""
from abc import ABC, abstractmethod
from core.domain.models import EvaluationRequest, EvaluationResult


class EvaluationStrategy(ABC):
    """Base class for evaluation strategies"""

    @abstractmethod
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """Execute the evaluation"""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name"""
        raise NotImplementedError


