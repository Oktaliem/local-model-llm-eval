"""
Unit tests for backend.services.analytics_service
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from backend.services.analytics_service import (
    calculate_aggregate_statistics,
    prepare_time_series_data
)


class TestAnalyticsService:
    """Test suite for analytics_service functions"""
    
    def test_calculate_aggregate_statistics_comprehensive(self):
        """Test calculating aggregate statistics for comprehensive evaluations"""
        data = {
            "comprehensive": [
                {
                    "overall_score": 8.5,
                    "accuracy": 8.0,
                    "relevance": 9.0,
                    "coherence": 8.5,
                    "hallucination": 2.0,
                    "toxicity": 1.0,
                    "judge_model": "llama3"
                },
                {
                    "overall_score": 9.0,
                    "accuracy": 9.0,
                    "relevance": 9.5,
                    "coherence": 9.0,
                    "hallucination": 1.0,
                    "toxicity": 0.5,
                    "judge_model": "llama3"
                }
            ],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        stats = calculate_aggregate_statistics(data)
        
        assert "comprehensive" in stats
        assert stats["comprehensive"]["count"] == 2
        assert stats["comprehensive"]["overall_avg"] == 8.75
        assert stats["comprehensive"]["accuracy_avg"] == 8.5
        assert stats["comprehensive"]["relevance_avg"] == 9.25
        assert "llama3" in stats["comprehensive"]["by_model"]
    
    def test_calculate_aggregate_statistics_code_evaluations(self):
        """Test calculating aggregate statistics for code evaluations"""
        data = {
            "comprehensive": [],
            "code_evaluations": [
                {
                    "overall_score": 8.0,
                    "syntax_valid": True,
                    "execution_success": True,
                    "maintainability": 7.5,
                    "readability": 8.5
                },
                {
                    "overall_score": 9.0,
                    "syntax_valid": True,
                    "execution_success": True,
                    "maintainability": 9.0,
                    "readability": 9.0
                },
                {
                    "overall_score": 5.0,
                    "syntax_valid": False,
                    "execution_success": False,
                    "maintainability": 5.0,
                    "readability": 5.0
                }
            ],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        stats = calculate_aggregate_statistics(data)
        
        assert "code_evaluations" in stats
        assert stats["code_evaluations"]["count"] == 3
        assert stats["code_evaluations"]["overall_avg"] == pytest.approx(7.33, rel=0.1)
        assert stats["code_evaluations"]["syntax_success_rate"] == pytest.approx(66.67, rel=0.1)
        assert stats["code_evaluations"]["execution_success_rate"] == pytest.approx(66.67, rel=0.1)
    
    def test_calculate_aggregate_statistics_router_evaluations(self):
        """Test calculating aggregate statistics for router evaluations"""
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [
                {
                    "overall_score": 8.5,
                    "tool_accuracy": 9.0,
                    "routing_quality": 8.0,
                    "reasoning": 8.5
                },
                {
                    "overall_score": 9.0,
                    "tool_accuracy": 9.5,
                    "routing_quality": 9.0,
                    "reasoning": 9.0
                }
            ],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        stats = calculate_aggregate_statistics(data)
        
        assert "router_evaluations" in stats
        assert stats["router_evaluations"]["count"] == 2
        assert stats["router_evaluations"]["overall_avg"] == 8.75
        assert stats["router_evaluations"]["tool_accuracy_avg"] == 9.25
    
    def test_calculate_aggregate_statistics_skills_evaluations(self):
        """Test calculating aggregate statistics for skills evaluations"""
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [
                {
                    "overall_score": 8.5,
                    "skill_type": "mathematics",
                    "correctness": 9.0,
                    "completeness": 8.0,
                    "clarity": 8.5,
                    "proficiency": 8.5
                },
                {
                    "overall_score": 9.0,
                    "skill_type": "coding",
                    "correctness": 9.5,
                    "completeness": 9.0,
                    "clarity": 9.0,
                    "proficiency": 9.0
                }
            ],
            "trajectory_evaluations": []
        }
        
        stats = calculate_aggregate_statistics(data)
        
        assert "skills_evaluations" in stats
        assert stats["skills_evaluations"]["count"] == 2
        assert stats["skills_evaluations"]["overall_avg"] == 8.75
        assert "mathematics" in stats["skills_evaluations"]["by_skill_type"]
        assert "coding" in stats["skills_evaluations"]["by_skill_type"]
    
    def test_calculate_aggregate_statistics_trajectory_evaluations(self):
        """Test calculating aggregate statistics for trajectory evaluations"""
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": [
                {
                    "overall_score": 8.5,
                    "trajectory_type": "planning",
                    "step_quality": 8.0,
                    "path_efficiency": 9.0,
                    "reasoning_chain": 8.5,
                    "planning_quality": 9.0
                },
                {
                    "overall_score": 9.0,
                    "trajectory_type": "execution",
                    "step_quality": 9.0,
                    "path_efficiency": 9.5,
                    "reasoning_chain": 9.0,
                    "planning_quality": 9.0
                }
            ]
        }
        
        stats = calculate_aggregate_statistics(data)
        
        assert "trajectory_evaluations" in stats
        assert stats["trajectory_evaluations"]["count"] == 2
        assert stats["trajectory_evaluations"]["overall_avg"] == 8.75
        assert "planning" in stats["trajectory_evaluations"]["by_trajectory_type"]
        assert "execution" in stats["trajectory_evaluations"]["by_trajectory_type"]
    
    def test_calculate_aggregate_statistics_empty(self):
        """Test calculating aggregate statistics with empty data"""
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        stats = calculate_aggregate_statistics(data)
        assert stats == {}
    
    def test_prepare_time_series_data_comprehensive(self):
        """Test preparing time series data for comprehensive evaluations"""
        now = datetime.now()
        data = {
            "comprehensive": [
                {
                    "overall_score": 8.5,
                    "created_at": (now - timedelta(days=2)).isoformat()
                },
                {
                    "overall_score": 9.0,
                    "created_at": (now - timedelta(days=1)).isoformat()
                },
                {
                    "overall_score": 8.75,
                    "created_at": now.isoformat()
                }
            ],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        df = prepare_time_series_data(data, evaluation_type="comprehensive")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "overall_score" in df.columns
        assert "created_at" in df.columns
    
    def test_prepare_time_series_data_code_evaluations(self):
        """Test preparing time series data for code evaluations"""
        now = datetime.now()
        data = {
            "comprehensive": [],
            "code_evaluations": [
                {
                    "overall_score": 8.0,
                    "created_at": (now - timedelta(days=1)).isoformat()
                },
                {
                    "overall_score": 9.0,
                    "created_at": now.isoformat()
                }
            ],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        df = prepare_time_series_data(data, evaluation_type="code_evaluations")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "overall_score" in df.columns
    
    def test_prepare_time_series_data_empty(self):
        """Test preparing time series data with empty data"""
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        df = prepare_time_series_data(data, evaluation_type="comprehensive")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_prepare_time_series_data_no_created_at(self):
        """Test preparing time series data without created_at column"""
        data = {
            "comprehensive": [
                {"overall_score": 8.5}
            ],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        df = prepare_time_series_data(data, evaluation_type="comprehensive")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
    
    def test_prepare_time_series_data_router_evaluations(self):
        """Test preparing time series data for router evaluations"""
        now = datetime.now()
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [
                {
                    "overall_score": 8.5,
                    "created_at": (now - timedelta(days=1)).isoformat()
                },
                {
                    "overall_score": 9.0,
                    "created_at": now.isoformat()
                }
            ],
            "skills_evaluations": [],
            "trajectory_evaluations": []
        }
        
        df = prepare_time_series_data(data, evaluation_type="router_evaluations")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "overall_score" in df.columns
        assert "created_at" in df.columns
    
    def test_prepare_time_series_data_skills_evaluations(self):
        """Test preparing time series data for skills evaluations"""
        now = datetime.now()
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [
                {
                    "overall_score": 8.5,
                    "created_at": (now - timedelta(days=1)).isoformat()
                },
                {
                    "overall_score": 9.0,
                    "created_at": now.isoformat()
                }
            ],
            "trajectory_evaluations": []
        }
        
        df = prepare_time_series_data(data, evaluation_type="skills_evaluations")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "overall_score" in df.columns
        assert "created_at" in df.columns
    
    def test_prepare_time_series_data_trajectory_evaluations(self):
        """Test preparing time series data for trajectory evaluations"""
        now = datetime.now()
        data = {
            "comprehensive": [],
            "code_evaluations": [],
            "router_evaluations": [],
            "skills_evaluations": [],
            "trajectory_evaluations": [
                {
                    "overall_score": 8.5,
                    "created_at": (now - timedelta(days=1)).isoformat()
                },
                {
                    "overall_score": 9.0,
                    "created_at": now.isoformat()
                }
            ]
        }
        
        df = prepare_time_series_data(data, evaluation_type="trajectory_evaluations")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "overall_score" in df.columns
        assert "created_at" in df.columns

