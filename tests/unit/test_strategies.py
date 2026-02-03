"""Unit tests for evaluation strategies"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from core.domain.strategies.single import SingleStrategy
from core.domain.strategies.comprehensive import ComprehensiveStrategy
from core.domain.strategies.code_eval import CodeEvalStrategy
from core.domain.strategies.router import RouterStrategy
from core.domain.strategies.skills import SkillsStrategy
from core.domain.strategies.trajectory import TrajectoryStrategy
from core.domain.strategies.template_eval import TemplateEvalStrategy
from core.domain.strategies.custom_metric_eval import CustomMetricStrategy
from core.domain.models import EvaluationRequest, EvaluationResult

# Create mock app module if it doesn't exist
if 'app' not in sys.modules:
    mock_app = MagicMock()
    sys.modules['app'] = mock_app


class TestSingleStrategy:
    """Test cases for SingleStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = SingleStrategy()
        assert strategy.name == "single"
    
    def test_evaluate_success(self):
        """Test successful evaluation"""
        with patch('backend.services.evaluation_functions.judge_single') as mock_judge_single:
            mock_judge_single.return_value = {
                "success": True,
                "judgment": "Test judgment",
                "metrics": {"score": 8.5}
            }
            strategy = SingleStrategy()
            request = EvaluationRequest(
                evaluation_type="single",
                question="Test question",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Test judgment"
            assert result.scores == {"score": 8.5}
            mock_judge_single.assert_called_once()
    
    def test_evaluate_missing_response(self):
        """Test evaluation with missing response"""
        strategy = SingleStrategy()
        request = EvaluationRequest(
            evaluation_type="single",
            question="Test question",
            response=None,
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in result.error
    
    def test_evaluate_with_error(self):
        """Test evaluation with error"""
        with patch('backend.services.evaluation_functions.judge_single') as mock_judge_single:
            mock_judge_single.return_value = {
                "success": False,
                "error": "Test error"
            }
            strategy = SingleStrategy()
            request = EvaluationRequest(
                evaluation_type="single",
                question="Test question",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "Test error"

    def test_evaluate_missing_response_error_message(self):
        """Ensure missing response returns expected error text"""
        strategy = SingleStrategy()
        request = EvaluationRequest(
            evaluation_type="single",
            question="Test question",
            response=None,
            judge_model="llama3",
            options={}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in (result.error or "")

    def test_evaluate_uses_criteria_default(self):
        """Ensure criteria default string is passed when not provided"""
        with patch('backend.services.evaluation_functions.judge_single') as mock_judge_single:
            mock_judge_single.return_value = {"success": True, "judgment": "ok", "metrics": {}}
            strategy = SingleStrategy()
            request = EvaluationRequest(
                evaluation_type="single",
                question="Q",
                response="R",
                judge_model="llama3",
                options={}  # no criteria
            )
            strategy.evaluate(request)
            call_args = mock_judge_single.call_args
            assert call_args[1]["criteria"] == "Accuracy, relevance, clarity, completeness, helpfulness"
    
    def test_evaluate_verifies_criteria_default(self):
        """Test that criteria defaults correctly"""
        with patch('backend.services.evaluation_functions.judge_single') as mock_judge_single:
            mock_judge_single.return_value = {
                "success": True,
                "judgment": "Test",
                "metrics": {}
            }
            strategy = SingleStrategy()
            request = EvaluationRequest(
                evaluation_type="single",
                question="Test question",
                response="Test response",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default criteria is used (mutation: criteria = "" would fail)
            call_args = mock_judge_single.call_args
            assert call_args[1]["criteria"] == "Accuracy, relevance, clarity, completeness, helpfulness"
    
    def test_evaluate_verifies_judgment_fallback(self):
        """Test that judgment falls back to judgment_text"""
        with patch('backend.services.evaluation_functions.judge_single') as mock_judge_single:
            mock_judge_single.return_value = {
                "success": True,
                "judgment_text": "Fallback judgment",  # No "judgment" key
                "metrics": {}
            }
            strategy = SingleStrategy()
            request = EvaluationRequest(
                evaluation_type="single",
                question="Test question",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify fallback (mutation: result.get("judgment") -> result.get("judgment_text") would fail)
            assert result.judgment == "Fallback judgment"


class TestComprehensiveStrategy:
    """Test cases for ComprehensiveStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = ComprehensiveStrategy()
        assert strategy.name == "comprehensive"
    
    def test_evaluate_success(self):
        """Test successful evaluation"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test judgment",
                "metrics": {"accuracy": 9.0}
            }
            strategy = ComprehensiveStrategy()
            request = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Test question",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Test judgment"
            assert result.scores == {"accuracy": 9.0}
    
    def test_evaluate_missing_response(self):
        """Test evaluation with missing response"""
        strategy = ComprehensiveStrategy()
        request = EvaluationRequest(
            evaluation_type="comprehensive",
            question="Test question",
            response=None,
            response_a=None,
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in result.error
    
    def test_evaluate_with_options(self):
        """Test evaluation with options"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "Test"}
            strategy = ComprehensiveStrategy()
            request = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Test question",
                response="Test response",
                judge_model="llama3",
                options={"reference": "Ref", "task_type": "qa", "include_additional_properties": False}
            )
            result = strategy.evaluate(request)
            assert result.success is True
            mock_evaluate.assert_called_once()
            call_kwargs = mock_evaluate.call_args[1]
            assert call_kwargs["reference"] == "Ref"
            assert call_kwargs["task_type"] == "qa"
            assert call_kwargs["include_additional_properties"] is False
    
    def test_evaluate_verifies_response_fallback(self):
        """Test that response falls back to response_a"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "Test", "metrics": {}}
            strategy = ComprehensiveStrategy()
            # Test with response_a (no response)
            request1 = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Test",
                response_a="Response from response_a",
                judge_model="llama3"
            )
            result1 = strategy.evaluate(request1)
            assert result1.success is True
            call_args1 = mock_evaluate.call_args
            assert call_args1[1]["response"] == "Response from response_a"
            
            # Test with response (should take precedence)
            request2 = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Test",
                response="Response from response",
                response_a="Response from response_a",
                judge_model="llama3"
            )
            result2 = strategy.evaluate(request2)
            assert result2.success is True
            call_args2 = mock_evaluate.call_args
            assert call_args2[1]["response"] == "Response from response"  # response takes precedence
    
    def test_evaluate_verifies_task_type_default(self):
        """Test that task_type defaults to 'general'"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "Test", "metrics": {}}
            strategy = ComprehensiveStrategy()
            request = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default task_type (mutation: task_type = "" would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["task_type"] == "general"
    
    def test_evaluate_verifies_include_additional_properties_default(self):
        """Test that include_additional_properties defaults to True"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "Test", "metrics": {}}
            strategy = ComprehensiveStrategy()
            request = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default (mutation: include_additional_properties = False would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["include_additional_properties"] is True

    def test_evaluate_propagates_error(self):
        """Test that errors from evaluate_comprehensive propagate"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "comp error"}
            strategy = ComprehensiveStrategy()
            request = EvaluationRequest(
                evaluation_type="comprehensive",
                question="Q",
                response="R",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "comp error"

    def test_evaluate_missing_response_returns_error(self):
        """Ensure missing response path returns expected error"""
        strategy = ComprehensiveStrategy()
        request = EvaluationRequest(
            evaluation_type="comprehensive",
            question="Q",
            response=None,
            response_a=None,
            judge_model="llama3",
            options={}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in (result.error or "")


class TestCodeEvalStrategy:
    """Test cases for CodeEvalStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = CodeEvalStrategy()
        assert strategy.name == "code"
    
    def test_evaluate_success(self):
        """Test successful code evaluation"""
        with patch('backend.services.evaluation_functions.evaluate_code_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Code is valid",
                "results": {"syntax": 10.0}
            }
            strategy = CodeEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="code",
                question="Test code",
                response="print('hello')",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Code is valid"
            assert result.scores == {"syntax": 10.0}
    
    def test_evaluate_verifies_code_fallback_chain(self):
        """Test that code falls back through options -> response -> response_a -> """""
        with patch('backend.services.evaluation_functions.evaluate_code_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "results": {}
            }
            strategy = CodeEvalStrategy()
            # Test with response_a (no code in options, no response)
            request1 = EvaluationRequest(
                evaluation_type="code",
                question="Test",
                response_a="code from response_a",
                judge_model="llama3",
                options={}
            )
            result1 = strategy.evaluate(request1)
            assert result1.success is True
            call_args1 = mock_evaluate.call_args
            assert call_args1[1]["code"] == "code from response_a"
            
            # Test with code in options (should take precedence)
            request2 = EvaluationRequest(
                evaluation_type="code",
                question="Test",
                response="code from response",
                judge_model="llama3",
                options={"code": "code from options"}
            )
            result2 = strategy.evaluate(request2)
            assert result2.success is True
            call_args2 = mock_evaluate.call_args
            assert call_args2[1]["code"] == "code from options"  # Options take precedence
    
    def test_evaluate_verifies_language_default(self):
        """Test that language defaults to 'python'"""
        with patch('backend.services.evaluation_functions.evaluate_code_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "results": {}
            }
            strategy = CodeEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="code",
                question="Test",
                response="print('hello')",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default language (mutation: language = "" would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["language"] == "python"
    
    def test_evaluate_verifies_optional_parameters(self):
        """Test that optional parameters are passed correctly"""
        with patch('backend.services.evaluation_functions.evaluate_code_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "results": {}
            }
            strategy = CodeEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="code",
                question="Test",
                response="print('hello')",
                judge_model="llama3",
                options={
                    "language": "javascript",
                    "test_inputs": ["input1", "input2"],
                    "expected_output": "output"
                }
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["language"] == "javascript"
            assert call_args[1]["test_inputs"] == ["input1", "input2"]
            assert call_args[1]["expected_output"] == "output"
    
    def test_evaluate_missing_code(self):
        """Test evaluation with missing code"""
        strategy = CodeEvalStrategy()
        request = EvaluationRequest(
            evaluation_type="code",
            question="Test",
            judge_model="llama3",
            options={}  # No code anywhere
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "code is required" in result.error

    def test_evaluate_propagates_error(self):
        """Test that errors from evaluate_code_comprehensive propagate"""
        with patch('backend.services.evaluation_functions.evaluate_code_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "code error"}
            strategy = CodeEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="code",
                question="Test",
                response="print('hi')",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "code error"

    def test_evaluate_defaults_language_when_missing(self):
        """Ensure language defaults to 'python' when not provided"""
        with patch('backend.services.evaluation_functions.evaluate_code_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "ok", "results": {}}
            strategy = CodeEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="code",
                question="Q",
                response="print('hi')",
                judge_model="llama3",
                options={}  # no language
            )
            strategy.evaluate(request)
            call_args = mock_evaluate.call_args
            assert call_args[1]["language"] == "python"


class TestRouterStrategy:
    """Test cases for RouterStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = RouterStrategy()
        assert strategy.name == "router"
    
    def test_evaluate_success(self):
        """Test successful router evaluation"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Router decision is correct",
                "metrics": {"tool_accuracy_score": 8.5}
            }
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test query",
                response="Test decision",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Router decision is correct"
            assert result.scores == {"tool_accuracy_score": 8.5}
    
    def test_evaluate_verifies_options_defaults(self):
        """Test that options.get() defaults are used correctly"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test query",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify defaults are used (mutation: opts.get("available_tools", None) would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["available_tools"] == []  # Default
            assert call_args[1]["selected_tool"] == ""  # Default
    
    def test_evaluate_verifies_options_passed(self):
        """Test that options are passed correctly to evaluate_router_decision"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test query",
                judge_model="llama3",
                options={
                    "available_tools": [{"name": "tool1"}],
                    "selected_tool": "tool1",
                    "context": "Test context",
                    "expected_tool": "tool1",
                    "routing_strategy": "test_strategy"
                }
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify all options are passed (mutation: opts.get("context") -> opts.get("context", None) would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["query"] == "Test query"
            assert call_args[1]["available_tools"] == [{"name": "tool1"}]
            assert call_args[1]["selected_tool"] == "tool1"
            assert call_args[1]["context"] == "Test context"
            assert call_args[1]["expected_tool"] == "tool1"
            assert call_args[1]["routing_strategy"] == "test_strategy"
            assert call_args[1]["judge_model"] == "llama3"
    
    def test_evaluate_with_error(self):
        """Test evaluation with error"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": False,
                "error": "Router error"
            }
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test query",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "Router error"
    
    def test_evaluate_with_exception(self):
        """Test evaluation with exception"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.side_effect = Exception("Router exception")
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test query",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert "Router exception" in result.error
            # Verify exception is caught and converted to error (mutation: except Exception -> pass would fail)

    def test_evaluate_defaults_are_used(self):
        """Test defaults for context, expected_tool, routing_strategy"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "ok", "metrics": {}}
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Q",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["context"] is None
            assert call_args[1]["expected_tool"] is None
            assert call_args[1]["routing_strategy"] is None


class TestSkillsStrategy:
    """Test cases for SkillsStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = SkillsStrategy()
        assert strategy.name == "skills"
    
    def test_evaluate_success(self):
        """Test successful skills evaluation"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Skill assessment complete",
                "metrics": {"proficiency": 8.5}
            }
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test question",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Skill assessment complete"
            assert result.scores == {"proficiency": 8.5}
    
    def test_evaluate_verifies_skill_type_default(self):
        """Test that skill_type defaults to 'general'"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default skill_type (mutation: skill_type = "" would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["skill_type"] == "general"
    
    def test_evaluate_verifies_response_fallback(self):
        """Test that response falls back to empty string"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test",
                response=None,  # No response
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify fallback to empty string (mutation: response or "" -> response would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["response"] == ""
    
    def test_evaluate_verifies_optional_parameters(self):
        """Test that optional parameters are passed correctly"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={
                    "skill_type": "coding",
                    "reference_answer": "Reference",
                    "domain": "Python"
                }
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["skill_type"] == "coding"
            assert call_args[1]["reference_answer"] == "Reference"
            assert call_args[1]["domain"] == "Python"
    
    def test_evaluate_with_exception(self):
        """Test evaluation with exception"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.side_effect = Exception("Skills exception")
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert "Skills exception" in result.error

    def test_evaluate_missing_response_returns_error(self):
        """Test missing response falls back to empty string and succeeds"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "ok", "metrics": {}}
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Q",
                response=None,
                judge_model="llama3",
                options={}
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["response"] == ""

    def test_evaluate_propagates_error(self):
        """Test error propagation from evaluate_skill"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "skills error"}
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Q",
                response="R",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "skills error"

    def test_evaluate_missing_response_returns_empty_string(self):
        """Test missing response falls back to empty string and succeeds"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "ok", "metrics": {}}
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Q",
                response=None,
                judge_model="llama3",
                options={}
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["response"] == ""

    def test_evaluate_propagates_error(self):
        """Test error propagation from evaluate_skill"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "skills error"}
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Q",
                response="R",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "skills error"


class TestTrajectoryStrategy:
    """Test cases for TrajectoryStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = TrajectoryStrategy()
        assert strategy.name == "trajectory"
    
    def test_evaluate_success(self):
        """Test successful trajectory evaluation"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Trajectory evaluation complete",
                "metrics": {"accuracy": 8.5}
            }
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Test trajectory",
                response="Test steps",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Trajectory evaluation complete"
            assert result.scores == {"accuracy": 8.5}
    
    def test_evaluate_verifies_trajectory_default(self):
        """Test that trajectory defaults to empty list"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Test",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default trajectory (mutation: trajectory = None would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["trajectory"] == []
    
    def test_evaluate_verifies_optional_parameters(self):
        """Test that optional parameters are passed correctly"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Test",
                judge_model="llama3",
                options={
                    "trajectory": [{"step": 1}, {"step": 2}],
                    "expected_trajectory": [{"step": 1}],
                    "trajectory_type": "sequential"
                }
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["trajectory"] == [{"step": 1}, {"step": 2}]
            assert call_args[1]["expected_trajectory"] == [{"step": 1}]
            assert call_args[1]["trajectory_type"] == "sequential"
            assert call_args[1]["task_description"] == "Test"

    def test_evaluate_missing_trajectory_defaults(self):
        """Test default empty trajectory and None expected_trajectory"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.return_value = {"success": True, "judgment_text": "ok", "metrics": {}}
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Q",
                judge_model="llama3",
                options={}
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["trajectory"] == []
            assert call_args[1]["expected_trajectory"] is None

    def test_evaluate_propagates_error(self):
        """Test trajectory evaluation error propagation"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "traj error"}
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Q",
                judge_model="llama3",
                options={"trajectory": []}
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "traj error"
    
    def test_evaluate_with_exception(self):
        """Test evaluation with exception"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.side_effect = Exception("Trajectory exception")
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert "Trajectory exception" in result.error


class TestTemplateEvalStrategy:
    """Test cases for TemplateEvalStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = TemplateEvalStrategy()
        assert strategy.name == "template"
    
    def test_evaluate_success(self):
        """Test successful template evaluation"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Template evaluation complete",
                "metrics": {"score": 8.5}
            }
            strategy = TemplateEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="template",
                question="Test question",
                response="Test response",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Template evaluation complete"
            assert result.scores == {"score": 8.5}
    
    def test_evaluate_verifies_response_fallback_chain(self):
        """Test that response falls back through response -> response_a -> """""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = TemplateEvalStrategy()
            # Test with response_a (no response)
            request1 = EvaluationRequest(
                evaluation_type="template",
                question="Test",
                response_a="Response from response_a",
                judge_model="llama3"
            )
            result1 = strategy.evaluate(request1)
            assert result1.success is True
            call_args1 = mock_evaluate.call_args
            assert call_args1[1]["response"] == "Response from response_a"
            
            # Test with response (should take precedence)
            request2 = EvaluationRequest(
                evaluation_type="template",
                question="Test",
                response="Response from response",
                response_a="Response from response_a",
                judge_model="llama3"
            )
            result2 = strategy.evaluate(request2)
            assert result2.success is True
            call_args2 = mock_evaluate.call_args
            assert call_args2[1]["response"] == "Response from response"
    
    def test_evaluate_missing_response(self):
        """Test evaluation with missing response"""
        strategy = TemplateEvalStrategy()
        request = EvaluationRequest(
            evaluation_type="template",
            question="Test",
            judge_model="llama3",
            options={}  # No response anywhere
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in result.error

    def test_evaluate_propagates_error(self):
        """Test template evaluation error propagation"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "template error"}
            strategy = TemplateEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="template",
                question="Q",
                response="R",
                judge_model="llama3",
                options={}
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "template error"
    
    def test_evaluate_verifies_task_type_default(self):
        """Test that task_type defaults to 'general'"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = TemplateEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="template",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default task_type (mutation: task_type = "" would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["task_type"] == "general"
    
    def test_evaluate_verifies_include_additional_properties_default(self):
        """Test that include_additional_properties defaults to True"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "metrics": {}
            }
            strategy = TemplateEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="template",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={}  # Empty options
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify default (mutation: include_additional_properties = False would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["include_additional_properties"] is True


class TestCustomMetricStrategy:
    """Test cases for CustomMetricStrategy"""
    
    def test_name_property(self):
        """Test name property"""
        strategy = CustomMetricStrategy()
        assert strategy.name == "custom_metric"
    
    def test_evaluate_success(self):
        """Test successful custom metric evaluation"""
        with patch('backend.services.evaluation_functions.evaluate_with_custom_metric') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Custom metric evaluation complete",
                "scores": {"custom_score": 8.5}
            }
            strategy = CustomMetricStrategy()
            request = EvaluationRequest(
                evaluation_type="custom_metric",
                question="Test question",
                response="Test response",
                judge_model="llama3",
                options={"metric_id": "test_metric_id"}
            )
            result = strategy.evaluate(request)
            assert result.success is True
            assert result.judgment == "Custom metric evaluation complete"
            assert result.scores == {"custom_score": 8.5}
    
    def test_evaluate_missing_metric_id(self):
        """Test evaluation with missing metric_id"""
        strategy = CustomMetricStrategy()
        request = EvaluationRequest(
            evaluation_type="custom_metric",
            question="Test",
            response="Test response",
            judge_model="llama3",
            options={}  # No metric_id
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "metric_id is required" in result.error

    def test_evaluate_propagates_error(self):
        """Test custom metric evaluation error propagation"""
        with patch('backend.services.evaluation_functions.evaluate_with_custom_metric') as mock_evaluate:
            mock_evaluate.return_value = {"success": False, "error": "metric error"}
            strategy = CustomMetricStrategy()
            request = EvaluationRequest(
                evaluation_type="custom_metric",
                question="Q",
                response="R",
                judge_model="llama3",
                options={"metric_id": "id1"}
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert result.error == "metric error"

    def test_evaluate_missing_response_returns_error(self):
        """Ensure missing response path returns expected error"""
        strategy = CustomMetricStrategy()
        request = EvaluationRequest(
            evaluation_type="custom_metric",
            question="Q",
            response=None,
            response_a=None,
            judge_model="llama3",
            options={"metric_id": "id1"}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in (result.error or "")
    
    def test_evaluate_missing_response(self):
        """Test evaluation with missing response"""
        strategy = CustomMetricStrategy()
        request = EvaluationRequest(
            evaluation_type="custom_metric",
            question="Test",
            judge_model="llama3",
            options={"metric_id": "test_metric"}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in result.error
    
    def test_evaluate_verifies_response_fallback(self):
        """Test that response falls back to response_a"""
        with patch('backend.services.evaluation_functions.evaluate_with_custom_metric') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "scores": {}
            }
            strategy = CustomMetricStrategy()
            request = EvaluationRequest(
                evaluation_type="custom_metric",
                question="Test",
                response_a="Response from response_a",
                judge_model="llama3",
                options={"metric_id": "test_metric"}
            )
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify fallback (mutation: response or "" -> response would fail)
            call_args = mock_evaluate.call_args
            assert call_args[1]["response"] == "Response from response_a"
    
    def test_evaluate_verifies_optional_reference(self):
        """Test that optional reference parameter is passed"""
        with patch('backend.services.evaluation_functions.evaluate_with_custom_metric') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": True,
                "judgment_text": "Test",
                "scores": {}
            }
            strategy = CustomMetricStrategy()
            request = EvaluationRequest(
                evaluation_type="custom_metric",
                question="Test",
                response="Test response",
                judge_model="llama3",
                options={
                    "metric_id": "test_metric",
                    "reference": "Reference answer"
                }
            )
            result = strategy.evaluate(request)
            assert result.success is True
            call_args = mock_evaluate.call_args
            assert call_args[1]["reference"] == "Reference answer"

