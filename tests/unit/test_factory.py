"""Unit tests for StrategyFactory"""
import pytest
from core.domain.factory import StrategyFactory
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
from unittest.mock import Mock


class TestStrategyFactory:
    """Test cases for StrategyFactory"""
    
    def test_factory_initialization_default(self):
        """Test factory initialization with default adapter"""
        factory = StrategyFactory()
        assert factory.llm_adapter is not None
        assert isinstance(factory.llm_adapter, OllamaAdapter)
        assert factory._strategies == {}
    
    def test_factory_initialization_custom_adapter(self):
        """Test factory initialization with custom adapter"""
        custom_adapter = Mock(spec=OllamaAdapter)
        factory = StrategyFactory(llm_adapter=custom_adapter)
        assert factory.llm_adapter == custom_adapter
    
    def test_get_pairwise_strategy(self):
        """Test getting pairwise strategy"""
        factory = StrategyFactory()
        strategy = factory.get("pairwise")
        assert isinstance(strategy, PairwiseStrategy)
        # Should be cached
        strategy2 = factory.get("pairwise")
        assert strategy is strategy2
    
    def test_get_single_strategy(self):
        """Test getting single strategy"""
        factory = StrategyFactory()
        strategy = factory.get("single")
        assert isinstance(strategy, SingleStrategy)
    
    def test_get_comprehensive_strategy(self):
        """Test getting comprehensive strategy"""
        factory = StrategyFactory()
        strategy = factory.get("comprehensive")
        assert isinstance(strategy, ComprehensiveStrategy)
    
    def test_get_code_eval_strategy(self):
        """Test getting code evaluation strategy"""
        factory = StrategyFactory()
        strategy = factory.get("code")
        assert isinstance(strategy, CodeEvalStrategy)
    
    def test_get_router_strategy(self):
        """Test getting router strategy"""
        factory = StrategyFactory()
        strategy = factory.get("router")
        assert isinstance(strategy, RouterStrategy)
    
    def test_get_skills_strategy(self):
        """Test getting skills strategy"""
        factory = StrategyFactory()
        strategy = factory.get("skills")
        assert isinstance(strategy, SkillsStrategy)
    
    def test_get_trajectory_strategy(self):
        """Test getting trajectory strategy"""
        factory = StrategyFactory()
        strategy = factory.get("trajectory")
        assert isinstance(strategy, TrajectoryStrategy)
    
    def test_get_template_eval_strategy(self):
        """Test getting template evaluation strategy"""
        factory = StrategyFactory()
        strategy = factory.get("template")
        assert isinstance(strategy, TemplateEvalStrategy)
    
    def test_get_custom_metric_strategy(self):
        """Test getting custom metric strategy"""
        factory = StrategyFactory()
        strategy = factory.get("custom_metric")
        assert isinstance(strategy, CustomMetricStrategy)
    
    def test_get_unknown_strategy(self):
        """Test getting unknown strategy raises ValueError"""
        factory = StrategyFactory()
        with pytest.raises(ValueError, match="Unknown strategy"):
            factory.get("unknown_strategy")
    
    def test_strategy_caching(self):
        """Test that strategies are cached"""
        factory = StrategyFactory()
        strategy1 = factory.get("single")
        strategy2 = factory.get("single")
        assert strategy1 is strategy2
        assert "single" in factory._strategies
    
    def test_multiple_strategies(self):
        """Test getting multiple different strategies"""
        factory = StrategyFactory()
        pairwise = factory.get("pairwise")
        single = factory.get("single")
        comprehensive = factory.get("comprehensive")
        
        assert isinstance(pairwise, PairwiseStrategy)
        assert isinstance(single, SingleStrategy)
        assert isinstance(comprehensive, ComprehensiveStrategy)
        assert len(factory._strategies) == 3


