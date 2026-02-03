"""Factory for creating evaluation strategies and LLM adapters"""
from typing import Dict, Optional
from core.domain.strategies.base import EvaluationStrategy
from core.domain.strategies.pairwise import PairwiseStrategy
from core.domain.strategies.single import SingleStrategy
from core.domain.strategies.comprehensive import ComprehensiveStrategy
from core.domain.strategies.code_eval import CodeEvalStrategy
from core.domain.strategies.router import RouterStrategy
from core.domain.strategies.skills import SkillsStrategy
from core.domain.strategies.trajectory import TrajectoryStrategy
from core.domain.strategies.template_eval import TemplateEvalStrategy
from core.domain.strategies.custom_metric_eval import CustomMetricStrategy
from core.infrastructure.llm.ollama_client import OllamaAdapter


class StrategyFactory:
    """Factory for creating evaluation strategies"""

    def __init__(self, llm_adapter: Optional[OllamaAdapter] = None):
        self.llm_adapter = llm_adapter or OllamaAdapter()
        self._strategies: Dict[str, EvaluationStrategy] = {}

    def get(self, strategy_name: str) -> EvaluationStrategy:
        if strategy_name in self._strategies:
            return self._strategies[strategy_name]
        strategy = self._create_strategy(strategy_name)
        self._strategies[strategy_name] = strategy
        return strategy

    def _create_strategy(self, strategy_name: str) -> EvaluationStrategy:
        if strategy_name == "pairwise":
            return PairwiseStrategy(self.llm_adapter)
        if strategy_name == "single":
            return SingleStrategy()
        if strategy_name == "comprehensive":
            return ComprehensiveStrategy()
        if strategy_name == "code":
            return CodeEvalStrategy()
        if strategy_name == "router":
            return RouterStrategy()
        if strategy_name == "skills":
            return SkillsStrategy()
        if strategy_name == "trajectory":
            return TrajectoryStrategy()
        if strategy_name == "template":
            return TemplateEvalStrategy()
        if strategy_name == "custom_metric":
            return CustomMetricStrategy()
        raise ValueError(f"Unknown strategy: {strategy_name}")


