"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ComprehensiveEvaluationRequest(BaseModel):
    question: str = Field(..., description="The question or prompt")
    response: str = Field(..., description="The response to evaluate")
    judge_model: str = Field(default="llama3", description="Judge model to use")
    task_type: str = Field(default="general", description="Task type: general, qa, summarization, code, translation, creative")
    reference: Optional[str] = Field(default=None, description="Optional reference answer for comparison")
    include_additional_properties: bool = Field(default=True, description="Include politeness, bias, tone, and sentiment metrics")
    save_to_db: bool = Field(default=True, description="Whether to save to database")


class CodeEvaluationRequest(BaseModel):
    code: str = Field(..., description="Python code to evaluate")
    test_input: Optional[str] = Field(None, description="Test input (optional)")
    expected_output: Optional[str] = Field(None, description="Expected output (optional)")
    judge_model: str = Field(default="llama3", description="Judge model to use")
    save_to_db: bool = Field(default=True, description="Whether to save to database")


class RouterEvaluationRequest(BaseModel):
    query: str = Field(..., description="Query/request")
    available_tools: List[Dict[str, str]] = Field(..., description="List of available tools with name and description")
    selected_tool: str = Field(..., description="Tool that was selected")
    context: Optional[str] = Field(None, description="Additional context")
    expected_tool: Optional[str] = Field(None, description="Expected tool (for accuracy)")
    routing_strategy: Optional[str] = Field(None, description="Routing strategy used")
    judge_model: str = Field(default="llama3", description="Judge model to use")
    save_to_db: bool = Field(default=True, description="Whether to save to database")


class SkillsEvaluationRequest(BaseModel):
    skill_type: str = Field(..., description="Skill type: mathematics, coding, reasoning, general")
    question: str = Field(..., description="Question or task")
    response: str = Field(..., description="Response to evaluate")
    reference_answer: Optional[str] = Field(None, description="Reference answer (optional)")
    domain: Optional[str] = Field(None, description="Domain (optional)")
    judge_model: str = Field(default="llama3", description="Judge model to use")
    save_to_db: bool = Field(default=True, description="Whether to save to database")


class TrajectoryEvaluationRequest(BaseModel):
    task_description: str = Field(..., description="Task description")
    trajectory: List[Dict[str, str]] = Field(..., description="Trajectory steps with action and description")
    expected_trajectory: Optional[List[Dict[str, str]]] = Field(None, description="Expected trajectory (optional)")
    trajectory_type: Optional[str] = Field(None, description="Trajectory type")
    judge_model: str = Field(default="llama3", description="Judge model to use")
    save_to_db: bool = Field(default=True, description="Whether to save to database")


class PairwiseComparisonRequest(BaseModel):
    question: str = Field(..., description="The question")
    response_a: str = Field(..., description="First response")
    response_b: str = Field(..., description="Second response")
    model_a: Optional[str] = Field(None, description="Model for response A")
    model_b: Optional[str] = Field(None, description="Model for response B")
    judge_model: str = Field(default="llama3", description="Judge model to use")
    save_to_db: bool = Field(default=True, description="Whether to save to database")


class APIKeyResponse(BaseModel):
    api_key: str
    created_at: str
    description: Optional[str] = None


class WebhookRequest(BaseModel):
    url: str = Field(..., description="Webhook URL to call")
    events: List[str] = Field(default=["evaluation.completed"], description="Events to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")


class WebhookResponse(BaseModel):
    webhook_id: str
    url: str
    events: List[str]
    created_at: str


class CreateABTestRequest(BaseModel):
    test_name: str = Field(..., description="Name of the A/B test")
    variant_a_name: str = Field(..., description="Name of variant A")
    variant_b_name: str = Field(..., description="Name of variant B")
    variant_a_config: Dict[str, Any] = Field(..., description="Configuration for variant A")
    variant_b_config: Dict[str, Any] = Field(..., description="Configuration for variant B")
    evaluation_type: str = Field(..., description="Type of evaluation to use")
    test_cases: List[Dict[str, Any]] = Field(..., description="Test cases to evaluate")
    test_description: Optional[str] = Field(None, description="Description of the test")


class RunABTestRequest(BaseModel):
    test_id: str = Field(..., description="ID of the A/B test to run")
    judge_model: str = Field(default="llama3", description="Judge model to use")


class CreateTemplateRequest(BaseModel):
    template_name: str = Field(..., description="Name of the template")
    evaluation_type: str = Field(..., description="Type of evaluation")
    template_config: Dict[str, Any] = Field(..., description="Template configuration")
    template_description: Optional[str] = Field(None, description="Description of the template")
    industry: Optional[str] = Field(None, description="Industry this template is for")


class ApplyTemplateRequest(BaseModel):
    template_id: str = Field(..., description="ID of the template to apply")
    evaluation_data: Dict[str, Any] = Field(..., description="Evaluation data to apply template to")


class CreateCustomMetricRequest(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    evaluation_type: str = Field(..., description="Type of evaluation")
    metric_definition: str = Field(..., description="Definition of the metric")
    metric_description: Optional[str] = Field(None, description="Description of the metric")
    domain: Optional[str] = Field(None, description="Domain this metric is for")
    scoring_function: Optional[str] = Field(None, description="Scoring function")
    criteria_json: Optional[Dict[str, Any]] = Field(None, description="Criteria as JSON")
    weight: float = Field(default=1.0, description="Weight of the metric")
    scale_min: float = Field(default=0.0, description="Minimum scale value")
    scale_max: float = Field(default=10.0, description="Maximum scale value")


class EvaluateWithCustomMetricRequest(BaseModel):
    metric_id: str = Field(..., description="ID of the custom metric")
    question: str = Field(..., description="Question to evaluate")
    response: str = Field(..., description="Response to evaluate")
    reference: Optional[str] = Field(None, description="Reference answer (optional)")
    judge_model: str = Field(default="llama3", description="Judge model to use")

