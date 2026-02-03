"""Domain data models (DTOs)"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class EvaluationRequest:
    evaluation_type: str
    question: str
    response_a: Optional[str] = None
    response_b: Optional[str] = None
    response: Optional[str] = None
    judge_model: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    evaluation_id: Optional[str] = None


@dataclass
class EvaluationResult:
    success: bool
    evaluation_type: str
    evaluation_id: Optional[str] = None
    judgment: Optional[str] = None
    winner: Optional[str] = None
    score_a: Optional[float] = None
    score_b: Optional[float] = None
    scores: Optional[Dict[str, float]] = None
    reasoning: Optional[str] = None
    trace: Optional[List[Dict[str, Any]]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunProgress:
    run_id: str
    total_cases: int
    completed_cases: int = 0
    status: str = "running"
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


